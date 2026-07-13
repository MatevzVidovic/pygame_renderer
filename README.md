

# Some important details

Create and activate the project `.venv` from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```


## Coordinates

They are in x, y form. Not y, x as we are used to in image processing.
This is a Pygame thing.

## Look at src/0_simple_test/ for examples

Look at RUN_ME.md.
We always run things from the repo root.
And so we also specify image paths from repo root and such.

## Resolution vs output size

`main(..., size=(w, h))` sets the final window/video size.
`main(..., render_scale=N)` sets the internal render resolution.

For example, `size=(720, 720), render_scale=3` renders internally at
`2160x2160`, applies post-processing like perspective warp there, and then
smooth-scales back down to `720x720`. Use this when warped grid lines or thin
objects look jagged but you do not want a larger output window/video.
