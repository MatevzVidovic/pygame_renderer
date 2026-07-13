from __future__ import annotations

import numpy as np
import pygame


class PerspectiveWarp:
    def __init__(
        self,
        size: tuple[int, int],
        horizon: float = 0.30,
        depth: float = 3.0,
        background: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        """
        size:
            The exact pixel size of the already-rendered source frame,
            as (width, height). This must match the surface passed to apply().

        horizon:
            Where the vanishing horizon sits as a fraction of screen height.
            0.0 is the top edge, 1.0 is the bottom edge.
            Smaller values show more warped ground. Larger values leave more
            flat background above the horizon and compress the world into less
            vertical space.

            Good starting values: 0.25 to 0.40.

        depth:
            Strength of perspective. This is the far/near depth ratio.
            Must be greater than 1.0.

            - 1.1 is very mild, almost flat.
            - 2.0 to 4.0 gives a readable Mode-7 style effect.
            - 5.0+ is strong and will heavily squeeze distant pixels.

        background:
            Fill color for the sky/empty area above the horizon and for pixels
            that project outside the source frame.

        Image quality note:
            This warp is intentionally fast. It precomputes integer source pixel
            indices and then uses np.take each frame. That is nearest-neighbor
            sampling, not bilinear filtering, so thin lines can look jagged after
            perspective compression. For nicer grid lines, draw them thicker,
            render the source at a higher resolution and downscale afterward, or
            add a future bilinear sampling mode.
        """
        if depth <= 1.0:
            raise ValueError("depth must be greater than 1.0")

        self.size = w, h = size
        self.background = background
        self.horizon_y = hy = int(h * horizon)
        cx = w / 2.0

        xd, yd = np.mgrid[0:w, hy:h]
        p = (yd - hy + 1) / float(h - hy)

        k = 1.0 / depth
        v = (1.0 / k - 1.0 / p) / (1.0 / k - 1.0)
        xs = cx + (xd - cx) / p
        ys = v * (h - 1)

        self._invalid = ~((v >= 0.0) & (xs >= 0.0) & (xs <= w - 1))
        # Integer indices make apply() very fast, but this is nearest-neighbor
        # sampling. High-contrast 1px lines will alias after perspective warp.
        xi = np.clip(xs, 0, w - 1).astype(np.intp)
        yi = np.clip(ys, 0, h - 1).astype(np.intp)
        self._flat_idx = (xi * h + yi).ravel()

        self._buf = np.empty(self._flat_idx.size, dtype=np.uint32)
        self._out = np.empty((w, h), dtype=np.uint32)
        self._surface = pygame.Surface(size, depth=32)
        self._background_rgb = self._surface.map_rgb(background)
        self._out[:] = self._background_rgb

    def apply(self, frame: pygame.Surface) -> pygame.Surface:
        if frame.get_size() != self.size:
            raise ValueError("frame size must match PerspectiveWarp size")

        if frame.get_bitsize() < 32:
            frame = frame.convert(32)

        src = pygame.surfarray.pixels2d(frame)
        w, h = self.size
        np.take(src.ravel(), self._flat_idx, out=self._buf)
        del src

        warped = self._buf.reshape(w, h - self.horizon_y)
        warped[self._invalid] = self._background_rgb
        self._out[:, self.horizon_y :] = warped
        pygame.surfarray.blit_array(self._surface, self._out)
        return self._surface
