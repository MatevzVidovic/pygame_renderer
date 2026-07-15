# Grid Robot Architecture

The state is managed by `problem_driver.py`
We have 2 threads:

- `solution.py` (which uses `Ops` to add to `TASK_QUEUE` inside problem_driver and waits on the resolution of added task)
- `state_renderer.py` (`run_renderer`) (which runs `.step` on problem driver, which executes the state change due to the task using `TaskResolver`, which also gives `solution.py` what it was waiting on, and also returns that new state so that `state_renderer` actually renders it

## Ownership and threads

```mermaid
flowchart LR
    subgraph solution_thread[Solution thread]
        Solution["solution.py<br/>solution.main(ops)"]
        Ops["Ops.move / Ops.scout_for_mouse"]
        Solution --> Ops
    end

    subgraph driver[problem_driver.py]
        Queue[(TASK_QUEUE)]
        Driver["CatchingMiceProblem<br/>state owner"]
        Resolver["TaskResolver.resolve"]
        Queue --> Driver
        Driver --> Resolver
    end

    subgraph render_thread[Main / render thread]
        StateRenderer["state_renderer.py<br/>run_renderer"]
        Pygame["pygame renderer"]
        StateRenderer -->|request next state| Driver
        StateRenderer -->|render new state| Pygame
    end

    Ops -->|enqueue Task + Future| Queue
    Resolver -->|complete Future| Ops
    Resolver -->|new State| Driver
```

`main.py` creates one `CatchingMiceProblem` and one `Ops` instance. It starts
`solution.main(ops)` in the solution thread, then runs `run_renderer(driver)`
on the main thread, where pygame is allowed to run.

## A task from request to rendered state

```mermaid
sequenceDiagram
    participant S as solution.py (solution thread)
    participant O as Ops
    participant Q as TASK_QUEUE
    participant D as CatchingMiceProblem.step (render thread)
    participant R as TaskResolver
    participant V as state_renderer / pygame

    S->>O: move(Direction.RIGHT)
    O->>O: create Future
    O->>Q: put Move(task, future)
    O->>S: wait on future.result()

    D->>Q: get next task
    Q-->>D: Move task
    D->>R: resolve(current_state, task)
    R->>R: calculate next state
    R-->>O: future.set_result(move result)
    R-->>D: next state
    D-->>V: return next state
    V->>V: render the new state
    O-->>S: return the resolved result
```

Some tasks, such as `ScoutMouse`, can resolve immediately without demanding a
render step. `CatchingMiceProblem.step()` keeps taking and resolving those
tasks until it receives a task that changes state and requires rendering.

## Shutdown

```mermaid
flowchart TD
    Done[solution.main returns] --> Signal[main.py calls driver.signal_done]
    Signal --> Stop[STOP marker enters TASK_QUEUE]
    Stop --> EndRender[driver.step raises StopIteration]
    EndRender --> Quit[pygame loop exits]

    WindowClose[pygame window closes] --> Close[main.py calls driver.close]
    Close --> FailWaiting[Outstanding Futures receive DriverClosed]
    FailWaiting --> EndSolution[solution thread exits]
```
