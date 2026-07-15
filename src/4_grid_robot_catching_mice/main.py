# This has to handle concurrency:
# The problem driver runs, which runs, state_renderer, which runs renderer.
# In this section, the renderer asks state_renderer what to do, which then asks problem_driver, which then waits to get sth in the task queue.
# Then another process happens concurrently:
# in solution.py we have an fn called main() which will be using waiting fns defined in problem_driver.
# These fns will add their fn task to the TQ (task queue) and wait for it to get fulfilled, get the result that that fn returns,
# and then return it tp the solution.py main program so it can continue.


"""Application entry point: pygame runs here; solution.py runs in a worker."""

from __future__ import annotations

from threading import Thread

import solution
from problem_driver import CatchingMiceProblem, DriverClosed, Ops
from state_renderer import run as run_renderer


def main() -> None:
    driver = CatchingMiceProblem()
    ops = Ops(driver)
    worker_error: list[BaseException] = []

    def run_solution() -> None:
        try:
            solution.main(ops)
        except DriverClosed:
            # Closing the pygame window is a normal way to stop the program.
            pass
        except BaseException as error:
            worker_error.append(error)
        finally:
            driver.signal_done()

    solution_thread = Thread(target=run_solution, name="solution")
    solution_thread.start()
    try:
        run_renderer(driver)  # Must remain on Python's main thread for pygame.
    finally:
        driver.close()
        solution_thread.join()

    if worker_error:
        raise worker_error[0]


if __name__ == "__main__":
    main()
