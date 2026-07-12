


## Setup with venv

Create and activate the project `.venv` from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs the Python packages, but it does not install `ffmpeg`. `ffmpeg` is
a system executable used for video rendering. The Python dependency
`imageio-ffmpeg` provides a bundled ffmpeg fallback inside the `.venv`, so rerun
the requirements install if video rendering says ffmpeg is missing:

```bash
python -m pip install -r requirements.txt
```

You can also install ffmpeg as a system binary. On macOS with Homebrew:

```bash
brew install ffmpeg
```

After installing it, this should print a path:

```bash
command -v ffmpeg
```

## Setup with conda

If you want the Python packages and `ffmpeg` managed together, use conda:

```bash
conda env create -f environment.yml
conda activate pygame-renderer
```

If the environment already exists:

```bash
conda env update -f environment.yml --prune
conda activate pygame-renderer
```

Then verify:

```bash
python -c "import numpy, pygame"
ffmpeg -version
```

## Video rendering

Video rendering uses `ffmpeg`. With `.venv`, it will first look for a system
`ffmpeg`, then fall back to the `imageio-ffmpeg` package from `requirements.txt`.
With conda, `ffmpeg` is installed directly into the environment.

If `ffmpeg` is installed but not on `PATH`, pass it explicitly:

```python
main(
    visual,
    video_render=True,
    video_params={
        "output_path": "render.mp4",
        "num_frames": 600,
        "ffmpeg_path": "/path/to/ffmpeg",
    },
)
```