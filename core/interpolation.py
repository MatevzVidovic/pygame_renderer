from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import numpy as np
import pygame

from core.renderer import (
    Color,
    InterpolatingFn,
    ObjectTree,
    Splat,
    SplatId,
    _color_tuple,
    _position_tuple,
    _render_splat,
)

_previous_interpolation_splats: dict[SplatId, Splat] = {}


def interpolating_render_object_tree(
    surface: pygame.Surface,
    object_tree: ObjectTree,
    background_color: Color = (20, 20, 24),
    interpolating_factor: int = 1,
    after_render: Callable[[int], None] | None = None,
) -> None:
    if interpolating_factor < 1:
        raise ValueError("interpolating_factor must be greater than or equal to 1")

    new_splats = _flatten_splats(object_tree)
    should_interpolate = _has_changed_interpolating_positions(new_splats)
    frame_count = interpolating_factor if should_interpolate else 1
    positions_by_splat = _precalculate_positions(new_splats, frame_count)

    for frame_index in range(frame_count):
        surface.fill(_color_tuple(background_color))

        for splat, positions in zip(new_splats, positions_by_splat):
            _render_splat(surface, replace(splat, pos=positions[frame_index]))

        if after_render is not None:
            after_render(frame_count)

    _store_previous_splats(new_splats)


def _flatten_splats(object_tree: ObjectTree) -> list[Splat]:
    if isinstance(object_tree, Splat):
        return [object_tree]

    splats: list[Splat] = []
    for child in object_tree:
        splats.extend(_flatten_splats(child))
    return splats


def _has_changed_interpolating_positions(new_splats: list[Splat]) -> bool:
    for splat in new_splats:
        if splat.id is None or splat.id not in _previous_interpolation_splats:
            continue

        old_pos = _position_array(_previous_interpolation_splats[splat.id].pos)
        new_pos = _position_array(splat.pos)
        if not np.array_equal(old_pos, new_pos):
            return True

    return False


def _precalculate_positions(
    new_splats: list[Splat],
    frame_count: int,
) -> list[np.ndarray]:
    t_values = np.linspace(1 / frame_count, 1, frame_count)
    change_cache: dict[int | None, np.ndarray] = {}

    return [
        _precalculate_splat_positions(splat, frame_count, t_values, change_cache)
        for splat in new_splats
    ]


def _precalculate_splat_positions(
    splat: Splat,
    frame_count: int,
    t_values: np.ndarray,
    change_cache: dict[int | None, np.ndarray],
) -> np.ndarray:
    new_pos = _position_array(splat.pos)

    if splat.id is None or splat.id not in _previous_interpolation_splats:
        return np.tile(new_pos, (frame_count, 1))

    old_pos = _position_array(_previous_interpolation_splats[splat.id].pos)
    if np.array_equal(old_pos, new_pos):
        return np.tile(new_pos, (frame_count, 1))

    changes = _changes_for_fn(splat.interpolating_fn, t_values, change_cache)
    return old_pos + (new_pos - old_pos) * changes[:, None]


def _changes_for_fn(
    interpolating_fn: InterpolatingFn | None,
    t_values: np.ndarray,
    change_cache: dict[int | None, np.ndarray],
) -> np.ndarray:
    cache_key = None if interpolating_fn is None else id(interpolating_fn)

    if cache_key not in change_cache:
        if interpolating_fn is None:
            changes = t_values
        else:
            changes = _apply_interpolating_fn(interpolating_fn, t_values)

        if np.any(changes < 0) or np.any(changes > 1):
            raise ValueError("interpolating_fn must return values between 0 and 1")

        change_cache[cache_key] = changes

    return change_cache[cache_key]


def _apply_interpolating_fn(
    interpolating_fn: InterpolatingFn,
    t_values: np.ndarray,
) -> np.ndarray:
    try:
        result = interpolating_fn(t_values)
        changes = np.asarray(result, dtype=float)
        if changes.shape == t_values.shape:
            return changes
    except Exception:
        pass

    return np.asarray([interpolating_fn(float(t)) for t in t_values], dtype=float)


def _store_previous_splats(new_splats: list[Splat]) -> None:
    global _previous_interpolation_splats
    _previous_interpolation_splats = {
        splat.id: replace(splat, pos=_position_tuple(splat.pos))
        for splat in new_splats
        if splat.id is not None
    }


def _position_array(pos: object) -> np.ndarray:
    return np.asarray(_position_tuple(pos), dtype=float)
