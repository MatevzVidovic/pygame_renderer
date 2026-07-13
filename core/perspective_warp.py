from __future__ import annotations

import numpy as np
import pygame


class PerspectiveWarp:
    def __init__(
        self,
        size: tuple[int, int],
        top_drop: float = 0.0,
        top_pull: float = 0.0,
        bottom_lift: float = 0.0,
        bottom_pull: float = 0.0,
        background: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        """
        size:
            The exact pixel size of the already-rendered source frame,
            as (width, height). This must match the surface passed to apply().

        top_drop:
            How much lower the old top edge appears in the output image,
            as a fraction of screen height.

            - 0.0 means the old top edge stays at the top: no vertical warp.
            - 0.2 means the old top edge moves 20% down from the top.
            - 0.5 means the old top edge appears halfway down the screen.

        top_pull:
            How much the old top-left and top-right corners move toward the
            center, as a fraction of screen width.

            - 0.0 means the top corners stay where they are: no horizontal warp.
            - 0.25 means each top corner moves 25% of the width inward.
            - 0.5 means the two top corners meet in the center.
            - values above 0.5 are allowed; the top edge crosses over itself.

        bottom_lift:
            How much higher the old bottom edge appears in the output image,
            as a fraction of screen height.

            - 0.0 means the old bottom edge stays at the bottom.
            - 0.2 means the old bottom edge moves 20% up from the bottom.

        bottom_pull:
            How much the old bottom-left and bottom-right corners move toward
            the center, as a fraction of screen width.

            - 0.0 means the bottom corners stay where they are.
            - 0.25 means each bottom corner moves 25% of the width inward.
            - 0.5 means the two bottom corners meet in the center.
            - values above 0.5 are allowed; the bottom edge crosses over itself.

        No-op:
            PerspectiveWarp(
                size,
                top_drop=0.0,
                top_pull=0.0,
                bottom_lift=0.0,
                bottom_pull=0.0,
            )
            is an exact identity transform.

        background:
            Fill color for pixels above/below the moved edges and for pixels
            outside the warped quadrilateral.

        Image quality note:
            This warp is intentionally fast. It precomputes integer source pixel
            indices and then uses np.take each frame. That is nearest-neighbor
            sampling, not bilinear filtering, so thin lines can look jagged after
            perspective compression. For nicer grid lines, draw them thicker,
            render the source at a higher resolution and downscale afterward, or
            add a future bilinear sampling mode.
        """
        if top_drop < 0.0 or top_drop >= 1.0:
            raise ValueError("top_drop must be in [0.0, 1.0)")
        if bottom_lift < 0.0 or bottom_lift >= 1.0:
            raise ValueError("bottom_lift must be in [0.0, 1.0)")
        if top_drop + bottom_lift >= 1.0:
            raise ValueError("top_drop + bottom_lift must be less than 1.0")

        self.size = w, h = size
        self.background = background

        xd, yd = np.mgrid[0:w, 0:h]
        top_y = (h - 1) * top_drop
        bottom_y = (h - 1) * (1.0 - bottom_lift)
        top_left_x = (w - 1) * top_pull
        top_right_x = (w - 1) * (1.0 - top_pull)
        bottom_left_x = (w - 1) * bottom_pull
        bottom_right_x = (w - 1) * (1.0 - bottom_pull)

        vertical_span = bottom_y - top_y
        v = (yd - top_y) / vertical_span
        left_x = top_left_x * (1.0 - v) + bottom_left_x * v
        right_x = top_right_x * (1.0 - v) + bottom_right_x * v
        row_width = right_x - left_x

        with np.errstate(divide="ignore", invalid="ignore"):
            u = (xd - left_x) / row_width

        xs = u * (w - 1)
        ys = v * (h - 1)

        self._invalid = ~(
            (yd >= top_y)
            & (yd <= bottom_y)
            & (np.abs(row_width) > 1e-9)
            & (u >= 0.0)
            & (u <= 1.0)
        )
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

        warped = self._buf.reshape(w, h)
        warped[self._invalid] = self._background_rgb
        self._out[:, :] = warped
        pygame.surfarray.blit_array(self._surface, self._out)
        return self._surface
