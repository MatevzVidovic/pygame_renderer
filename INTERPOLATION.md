# Interpolation Renderer

The normal renderer draws one object tree directly. The interpolation renderer adds
in-between frames for splats with stable ids, while keeping all drawing logic in
`core/renderer.py`.

```mermaid
flowchart LR
    A[VisualProgram.step] --> B[get_object_tree]
    B --> C{interpolating_factor}
    C -->|1| D[render_object_tree]
    C -->|> 1| E[interpolating_render_object_tree]
    D --> F[pygame display]
    E --> F
```

## Public API

Use ids on `Splat` objects that should interpolate:

```python
Splat(asset, pos, id="ball")
```

Use `main(..., interpolating_factor=N)` to enable interpolation:

```python
main(visual, interpolating_factor=4)
```

Use a custom easing function when linear interpolation is not enough:

```python
def ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)

Splat(asset, pos, id="ball", interpolating_fn=ease_in_out)
```

## Why Non-Linear Interpolation Exists

Non-linear interpolation is useful for discrete-space renders and games. The
simulation state may jump from one grid cell, tile, board position, or logical
state to another, but the visual layer does not have to look like a boring
straight slide.

The interpolation function lets that state jump become a small animation: sticky,
snappy, slow-in, slow-out, overshooting, or otherwise stylized. The object still
begins exactly at the old state and ends exactly at the new state, but the motion
between them can communicate that this is a transition between discrete states
rather than continuous physics.

```mermaid
flowchart LR
    A[old discrete state] --> B[visual transition]
    B --> C[new discrete state]
    B --> D[sticky / snappy / eased motion]
```

```mermaid
flowchart TD
    A[game logic jumps one tile] --> B[position changes instantly in state]
    B --> C[interpolation adds in-between frames]
    C --> D[player sees an animated move]
```

```mermaid
flowchart TD
    A[Splat] --> B[asset]
    A --> C[pos: y, x]
    A --> D[id]
    A --> E[interpolating_fn]
```

## Matching

Only splats with ids can interpolate. The renderer stores the previous splat
positions by id, then matches the new tree against that state.

```mermaid
flowchart LR
    A[previous splats] --> C{id match?}
    B[new splats] --> C
    C -->|yes and pos changed| D[interpolate position]
    C -->|no id or no match| E[render new position]
    C -->|same position| E
```

Interpolation affects only position. The asset, color, size, image, and render
order always come from the new object tree.

## Numpy Precalculation

For each render step, positions are precomputed with numpy before drawing starts.
Linear interpolation uses `np.linspace` directly. Custom interpolation functions
are applied to the whole linspace first; if that does not return a vector of the
right shape, the renderer falls back to calling the function per `t`.

```mermaid
flowchart TD
    A[interpolating_factor] --> B[np.linspace]
    B --> C{custom fn?}
    C -->|no| D[changes = linspace]
    C -->|yes| E[fn linspace]
    E --> F{vector result?}
    F -->|yes| G[use vector]
    F -->|no| H[fallback per t]
    D --> I[old + delta * changes]
    G --> I
    H --> I
```

The interpolation function must start at `0` and end at `1`. Intermediate values
may go below `0` or above `1`, which is useful for overshoot and shake effects.

```mermaid
flowchart LR
    A[t values] --> B[change values]
    B --> C{ends at 1?}
    C -->|yes| D[render frames]
    C -->|no| E[ValueError]
```

See `src/2_interpolation_test` for a simple 8x8 discrete grid where a block jumps
between random cells and uses a sticky overshooting transition.

## No-Motion Fast Path

If no matched splat positions changed, the interpolation renderer skips the extra
frames. It renders one normal frame, stores the current positions, and returns.

```mermaid
flowchart TD
    A[new object tree] --> B[match ids]
    B --> C{any position changed?}
    C -->|yes| D[render interpolating_factor frames]
    C -->|no| E[render 1 frame]
    D --> F[store current positions]
    E --> F
```

This avoids doing work when a simulation step changes state that does not move
anything on screen.
