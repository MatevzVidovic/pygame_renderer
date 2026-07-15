Run this from the root of the repo:

```bash
source .venv/bin/activate
PYTHONPATH=. python src/4_grid_robot_catching_mice/main.py
```

`main.py` starts `solution.main(ops)` on a worker thread and keeps pygame on
the process main thread. Put your algorithm in `solution.py`; import `Ops` and
`Direction`, then call `ops.move(Direction.RIGHT)` (or `UP`, `LEFT`, `DOWN`).
Each move waits for its animation to complete.
