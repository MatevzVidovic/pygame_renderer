"""Run many grid-robot games without pygame and summarize their outcomes."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pickle

import numpy as np

import problem_driver as driver_module
import solution
from problem_driver import (
    Direction,
    GameModeEnum,
    GRID_DIM,
    InitOps,
    Move,
    ScoutMouse,
    ScoutYourself,
    Task,
    TaskResolver,
)
from state import State


N = 100
PARALLEL = 3
BASE_SEED = 20_260_719
MAX_STEPS = 100_000


class GameFinished(StopIteration):
    def __init__(self, final_state: State, num_steps: int) -> None:
        self.final_state = final_state
        self.num_steps = num_steps


class SimulationStepLimitReached(RuntimeError):
    def __init__(self, final_state: State, num_steps: int) -> None:
        self.final_state = final_state
        self.num_steps = num_steps


@dataclass(frozen=True)
class SimulationResult:
    run_index: int
    seed: int
    game_mode: GameModeEnum
    status: str
    num_steps: int
    final_state: State


class SimulationProblem:
    """Stateful, synchronous wrapper around the existing TaskResolver."""

    def __init__(self, seed: int, max_steps: int) -> None:
        # TaskResolver uses NumPy's module-level RNG, so seed it once for this
        # isolated process-run and create the Markov distribution from it too.
        np.random.seed(seed)
        driver_module.MARKOV_MATRIX = np.random.dirichlet(np.ones(9)).reshape((3, 3))
        self._max_steps = max_steps
        self.num_steps = 0
        self.state = self._initial_state()

    @staticmethod
    def _initial_state() -> State:
        robot_pos = np.random.randint(GRID_DIM, size=2)
        mouse_pos = np.random.randint(GRID_DIM, size=2)
        while np.array_equal(robot_pos, mouse_pos):
            mouse_pos = np.random.randint(GRID_DIM, size=2)
        return State(robot_pos, mouse_pos)

    def resolve(self, task: Task) -> object:
        next_state, demands_step = TaskResolver.resolve(self.state, task)
        self.state = next_state

        if demands_step:
            self.num_steps += 1
            if np.array_equal(self.state.robot_pos, self.state.mouse_pos):
                raise GameFinished(self.state, self.num_steps)
            if self.num_steps >= self._max_steps:
                raise SimulationStepLimitReached(self.state, self.num_steps)

        assert task.reply is not None
        return task.reply.result()


class SimulationOps:
    """The same solution-facing operations, resolved immediately without pygame."""

    def __init__(self, problem: SimulationProblem) -> None:
        self._problem = problem

    def move(self, direction: Direction) -> bool:
        return bool(self._resolve(Move(direction)))

    def scout_for_mouse(self) -> np.ndarray:
        return np.asarray(self._resolve(ScoutMouse()))

    def scout_yourself(self) -> np.ndarray:
        return np.asarray(self._resolve(ScoutYourself()))

    def _resolve(self, task: Task) -> object:
        task.reply = Future()
        return self._problem.resolve(task)


def _run_one(run_index: int, seed: int, max_steps: int) -> SimulationResult:
    """Run one independent game. Kept at module scope for process workers."""
    InitOps.set_game_mode(GameModeEnum.UNIFORM)
    problem = SimulationProblem(seed, max_steps)
    ops = SimulationOps(problem)

    try:
        solution.main(ops)
    except GameFinished as finished:
        return SimulationResult(
            run_index,
            seed,
            driver_module.GAME_MODE,
            "finished",
            finished.num_steps,
            finished.final_state,
        )
    except SimulationStepLimitReached as limit:
        return SimulationResult(
            run_index,
            seed,
            driver_module.GAME_MODE,
            "max_steps_reached",
            limit.num_steps,
            limit.final_state,
        )

    return SimulationResult(
        run_index,
        seed,
        driver_module.GAME_MODE,
        "solution_returned",
        problem.num_steps,
        problem.state,
    )


def _seeds(base_seed: int, count: int) -> list[int]:
    seed_sequences = np.random.SeedSequence(base_seed).spawn(count)
    # np.random.seed() accepts only legacy 32-bit seed values.
    return [int(sequence.generate_state(1, dtype=np.uint32)[0]) for sequence in seed_sequences]


def run_batch(
    n: int = N,
    parallel: int = PARALLEL,
    base_seed: int = BASE_SEED,
    max_steps: int = MAX_STEPS,
) -> list[SimulationResult]:
    if n < 1 or parallel < 1 or max_steps < 1:
        raise ValueError("n, parallel, and max_steps must all be at least 1")

    jobs = list(enumerate(_seeds(base_seed, n)))
    with ProcessPoolExecutor(max_workers=parallel) as executor:
        return list(
            executor.map(
                _run_one,
                (run_index for run_index, _ in jobs),
                (seed for _, seed in jobs),
                (max_steps for _ in jobs),
            )
        )


def print_step_statistics(results: list[SimulationResult]) -> None:
    finished = [result for result in results if result.status == "finished"]
    capped = sum(result.status == "max_steps_reached" for result in results)
    returned = sum(result.status == "solution_returned" for result in results)
    print(f"finished: {len(finished)}/{len(results)}")
    print(f"max steps reached: {capped}")
    print(f"solution returned without a catch: {returned}")

    if not finished:
        print("No completed games; there are no completed-game step statistics.")
        return

    steps = np.asarray([result.num_steps for result in finished], dtype=float)
    game_modes = Counter(result.game_mode.name for result in results)
    if len(game_modes) == 1:
        print(f"game mode: {next(iter(game_modes))}")
    else:
        summary = ", ".join(f"{mode} ({count})" for mode, count in sorted(game_modes.items()))
        print(f"game modes: {summary}")

    counts = Counter(int(step) for step in steps)
    modes = sorted(step for step, count in counts.items() if count == max(counts.values()))
    print()
    print(f"avg: {steps.mean():.2f}")
    print(f"modus: {', '.join(map(str, modes))}")

    five_number_labels = ["min", "Q1", "median", "Q3", "max"]
    q1, median, q3 = np.quantile(steps, [0.25, 0.50, 0.75])
    five_number_values = [
        str(int(steps.min())),
        f"{q1:.2f}",
        f"{median:.2f}",
        f"{q3:.2f}",
        str(int(steps.max())),
    ]
    print(_aligned_table(five_number_labels, five_number_values))

    decile_labels = [f"d{index}" for index in range(1, 10)]
    decile_values = [f"{value:.2f}" for value in np.quantile(steps, np.arange(1, 10) / 10)]
    print("Deciles:")
    print(_aligned_table(decile_labels, decile_values))


def _aligned_table(labels: list[str], values: list[str]) -> str:
    """Return two pipe-separated rows with each column vertically aligned."""
    widths = [max(len(label), len(value)) for label, value in zip(labels, values)]
    header = " | ".join(label.ljust(width) for label, width in zip(labels, widths))
    row = " | ".join(value.ljust(width) for value, width in zip(values, widths))
    return f"{header}\n{row}"


def save_results(results: list[SimulationResult]) -> Path:
    output_dir = Path(__file__).with_name("simulation_results")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"run_{datetime.now():%Y%m%d_%H%M%S}.pkl"
    payload = [
        {
            "run_index": result.run_index,
            "seed": result.seed,
            "game_mode": result.game_mode.name,
            "status": result.status,
            "num_steps": result.num_steps,
            "final_state": result.final_state,
        }
        for result in results
    ]
    with output_path.open("wb") as output_file:
        pickle.dump(payload, output_file)
    return output_path


def main() -> None:
    results = run_batch()
    output_path = save_results(results)
    print_step_statistics(results)
    print(f"Saved {len(results)} simulation results to {output_path}")


if __name__ == "__main__":
    main()
