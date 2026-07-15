"""Thread-safe bridge between ``solution.py`` and the pygame render loop."""

from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from threading import Lock
from weakref import WeakSet

import numpy as np

from state import State


GRID_DIM = 8


class Direction(Enum):
    RIGHT = (0, 1)
    UP = (-1, 0)
    LEFT = (0, -1)
    DOWN = (1, 0)


@dataclass
class Move:
    direction: Direction
    reply: Future["State"] | None = None
    demands_step: bool = True


@dataclass
class ScoutMouse:
    reply: Future["State"] | None = None
    demands_step: bool = False


# SteppableTask = Move
Task = Move | ScoutMouse  # | Sth


def reply_set(task, rpl):
    if not task.reply.done():
        task.reply.set_result(rpl)


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

    def _resolve(self, task: Task):
        """Move one cell in ``direction`` and wait for its animation."""
        reply: Future[State] = Future()
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
    def resolve(state: State, task: Task) -> (State, bool):

        if isinstance(task, Move):
            delta = np.array(task.direction.value)
            robot_pos = state.robot_pos + delta
            mouse_pos = np.clip(state.mouse_pos + np.random.randint(-1, 2, 2), 0, GRID_DIM - 1)
            if np.any(robot_pos >= GRID_DIM) or np.any(robot_pos < 0):
                reply_set(task, False)
                next_state = State(state.robot_pos, mouse_pos)
            else:
                reply_set(task, True)
                next_state = State(robot_pos, mouse_pos)
        elif isinstance(task, ScoutMouse):
            reply_set(task, state.mouse_pos)
            next_state = state

        return next_state, task.demands_step


class CatchingMiceProblem:
    """Owns lifecycle and resolves queued tasks into game state."""

    def __init__(self) -> None:
        self._tasks: Queue[Move | object] = Queue()
        self._lock = Lock()
        self._pending: WeakSet[Future[State]] = WeakSet()
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
