Run this from the root of the repo:

```bash
source .venv/bin/activate
PYTHONPATH=. python src/4_grid_robot_catching_mice/main.py
```

`main.py` starts `solution.main(ops)` on a worker thread and keeps pygame on
the process main thread. Put your algorithm in `solution.py`; import `Ops` and
`Direction`, then call `ops.move(Direction.RIGHT)` (or `UP`, `LEFT`, `DOWN`).
Each move waits for its animation to complete.

Run a renderer-free batch simulation with:

```bash
PYTHONPATH=. python src/4_grid_robot_catching_mice/sim_main.py
```

Configure `N`, `PARALLEL`, `BASE_SEED`, and `MAX_STEPS` at the top of
`sim_main.py`. Results are saved as one pickle in `simulation_results/` next
to that file.
