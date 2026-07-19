"""Thread-safe bridge between ``solution.py`` and the pygame render loop."""

from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from enum import Enum, auto
from queue import Queue
from threading import Lock
from weakref import WeakSet

import numpy as np

from state import State


GRID_DIM = 8


class GameModeEnum(Enum):
    UNIFORM = auto()
    AVOIDANT = auto()
    MARKOV_CHAIN = auto()


GAME_MODE = GameModeEnum.UNIFORM

# MARKOV_CHAIN mode setting:
MARKOV_MATRIX = np.random.dirichlet(np.ones(9)).reshape((3, 3))
AVOIDANCE_STRENGTH = 0.5

# Row-major order matches MARKOV_MATRIX.ravel(): (-1, -1), (-1, 0), ... (1, 1).
MOUSE_DELTAS = np.array([(row, col) for row in range(-1, 2) for col in range(-1, 2)])


class InitOps:
    @staticmethod
    def set_game_mode(mode: GameModeEnum) -> None:
        """Select the mouse movement rule before starting the game."""
        global GAME_MODE
        GAME_MODE = mode


class Direction(Enum):
    RIGHT = (0, 1)
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)


@dataclass
class Move:
    direction: Direction
    reply: Future[object] | None = None
    demands_step: bool = True


@dataclass
class ScoutMouse:
    reply: Future[object] | None = None
    demands_step: bool = False


@dataclass
class ScoutYourself:
    reply: Future[object] | None = None
    demands_step: bool = False


# SteppableTask = Move
Task = Move | ScoutMouse | ScoutYourself


def reply_set(task: Task, result: object) -> None:
    assert task.reply is not None
    if not task.reply.done():
        task.reply.set_result(result)


class DriverClosed(RuntimeError):
    """Raised in solution.py when the pygame window is closed."""


_STOP = object()


class Ops:
    """The operations made available to solution.py."""

    def __init__(self, problem: CatchingMiceProblem) -> None:
        self._problem = problem

    def move(self, direction: Direction) -> bool:
        return self._resolve(Move(direction))

    def scout_for_mouse(self) -> np.ndarray:
        return self._resolve(ScoutMouse())

    def scout_yourself(self) -> np.ndarray:
        return self._resolve(ScoutYourself())

    def _resolve(self, task: Task):
        """Move one cell in ``direction`` and wait for its animation."""
        reply: Future[object] = Future()
        task.reply = reply
        with self._problem._lock:
            if self._problem._closed:
                raise DriverClosed("the renderer is no longer running")
            self._problem._pending.add(reply)
            self._problem._tasks.put(task)
        return reply.result()


class TaskResolver:
    """Applies a queued task to the current game state."""

    @staticmethod
    def resolve(state: State, task: Task) -> tuple[State, bool]:
        if isinstance(task, Move):
            delta = np.array(task.direction.value)
            requested_robot_pos = state.robot_pos + delta
            move_succeeded = bool(
                np.all(requested_robot_pos >= 0)
                and np.all(requested_robot_pos < GRID_DIM)
            )
            robot_pos = requested_robot_pos if move_succeeded else state.robot_pos

            if GAME_MODE == GameModeEnum.UNIFORM:
                mouse_pos = _sample_mouse_position(state.mouse_pos)

            elif GAME_MODE == GameModeEnum.AVOIDANT:
                mouse_pos = _sample_avoidant_mouse_position(state.mouse_pos, robot_pos)

            elif GAME_MODE == GameModeEnum.MARKOV_CHAIN:
                mouse_pos = _sample_mouse_position(state.mouse_pos, MARKOV_MATRIX.ravel())

            reply_set(task, move_succeeded)
            next_state = State(robot_pos, mouse_pos)
        elif isinstance(task, ScoutMouse):
            reply_set(task, state.mouse_pos)
            next_state = state
        elif isinstance(task, ScoutYourself):
            reply_set(task, state.robot_pos)
            next_state = state

        return next_state, task.demands_step


def _sample_mouse_position(
    mouse_pos: np.ndarray,
    weights: np.ndarray | None = None,
) -> np.ndarray:
    """Choose one of the in-bounds mouse moves, optionally using its weights."""
    candidates = mouse_pos + MOUSE_DELTAS
    valid = np.all((candidates >= 0) & (candidates < GRID_DIM), axis=1)
    valid_candidates = candidates[valid]

    if weights is None:
        return valid_candidates[np.random.randint(len(valid_candidates))]

    valid_weights = np.asarray(weights, dtype=float).ravel()[valid]
    valid_weights /= valid_weights.sum()
    return valid_candidates[np.random.choice(len(valid_candidates), p=valid_weights)]


def _sample_avoidant_mouse_position(
    mouse_pos: np.ndarray,
    robot_pos: np.ndarray,
) -> np.ndarray:
    """Prefer valid moves that leave the mouse farther from the robot."""
    candidates = mouse_pos + MOUSE_DELTAS
    squared_distances = np.sum((candidates - robot_pos) ** 2, axis=1)

    # Softmax keeps every legal move possible while making greater distance more
    # likely. Subtracting max is numerically stable and does not change ratios.
    scores = AVOIDANCE_STRENGTH * squared_distances
    weights = np.exp(scores - scores.max())
    return _sample_mouse_position(mouse_pos, weights)


class CatchingMiceProblem:
    """Owns lifecycle and resolves queued tasks into game state."""

    def __init__(self) -> None:
        self._tasks: Queue[Task | object] = Queue()
        self._lock = Lock()
        self._pending: WeakSet[Future[object]] = WeakSet()
        self._closed = False

    def init(self) -> State:
        """Create a random initial board with the robot and mouse apart."""
        rng = np.random.default_rng()
        robot_pos = rng.integers(0, GRID_DIM, size=2)
        mouse_pos = rng.integers(0, GRID_DIM, size=2)
        while np.array_equal(robot_pos, mouse_pos):
            mouse_pos = rng.integers(0, GRID_DIM, size=2)
        return State(robot_pos, mouse_pos)

    def step(self, state: State) -> State:
        cur_state = state
        task_demands_step = False

        if np.all(cur_state.robot_pos == cur_state.mouse_pos):
            print("Bravo!")
            raise StopIteration

        while not task_demands_step:
            task = self._tasks.get()
            if task is _STOP:
                raise StopIteration
            cur_state, task_demands_step = TaskResolver.resolve(cur_state, task)
        return cur_state

    def signal_done(self) -> None:
        """Tell the render loop that solution.main() returned normally."""
        self._tasks.put(_STOP)

    def close(self) -> None:
        """Unblock any waiting solution call when pygame exits early."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for reply in self._pending:
                if not reply.done():
                    reply.set_exception(DriverClosed("the renderer was closed"))
            self._pending.clear()
        self._tasks.put(_STOP)
