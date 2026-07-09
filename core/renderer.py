from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Protocol, TypeAlias, runtime_checkable

import pygame

ColorTuple: TypeAlias = tuple[int, int, int] | tuple[int, int, int, int]
Position: TypeAlias = Iterable[float]
SplatId: TypeAlias = str | int | tuple[object, ...] | None
InterpolatingFn: TypeAlias = Callable[[float], float]


class RGB:
    def __init__(self, r: int, g: int, b: int) -> None:
        self.color = (r, g, b)


class HSV:
    def __init__(self, h: float, s: float, v: float) -> None:
        h %= 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        self.color = (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255),
        )


Color: TypeAlias = RGB | HSV | ColorTuple


class CoordinatePlacing(Enum):
    CENTER = auto()
    TOP_LEFT = auto()


class Rect:
    def __init__(
        self,
        width: float,
        color: Color,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        self.width = width
        self.height = width if height is None else height
        self.color = color
        self.coordinate_placing = coordinate_placing

    def scale(self, scaling_factor: float) -> Rect:
        _validate_scaling_factor(scaling_factor)
        return Rect(
            self.width * scaling_factor,
            self.color,
            self.height * scaling_factor,
            self.coordinate_placing,
        )


class Elipse:
    def __init__(
        self,
        width: float,
        color: Color,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        self.width = width
        self.height = width if height is None else height
        self.color = color
        self.coordinate_placing = coordinate_placing

    def scale(self, scaling_factor: float) -> Elipse:
        _validate_scaling_factor(scaling_factor)
        return Elipse(
            self.width * scaling_factor,
            self.color,
            self.height * scaling_factor,
            self.coordinate_placing,
        )


class ImgRect:
    def __init__(
        self,
        path: str | Path,
        width: float,
        height: float | None = None,
        coordinate_placing: CoordinatePlacing = CoordinatePlacing.CENTER,
    ) -> None:
        loaded_image = pygame.image.load(str(path))
        original_width, original_height = loaded_image.get_size()

        self.width = width
        self.height = (
            width * original_height / original_width if height is None else height
        )
        self.coordinate_placing = coordinate_placing
        self.image = pygame.transform.smoothscale(
            loaded_image,
            (int(self.width), int(self.height)),
        )

    def scale(self, scaling_factor: float) -> ImgRect:
        _validate_scaling_factor(scaling_factor)
        scaled = object.__new__(ImgRect)
        scaled.width = self.width * scaling_factor
        scaled.height = self.height * scaling_factor
        scaled.coordinate_placing = self.coordinate_placing
        scaled.image = pygame.transform.smoothscale(
            self.image,
            (int(scaled.width), int(scaled.height)),
        )
        return scaled


Asset: TypeAlias = Rect | Elipse | ImgRect


@dataclass(frozen=True)
class Splat:
    asset: Asset
    pos: Position
    id: SplatId = None
    interpolating_fn: InterpolatingFn | None = None


ObjectTree: TypeAlias = Splat | Sequence["ObjectTree"]
_previous_interpolation_splats: dict[SplatId, Splat] = {}


@runtime_checkable
class VisualProgram(Protocol):
    def step(self) -> None:
        pass

    def get_object_tree(self) -> ObjectTree:
        pass


def render_object_tree(
    surface: pygame.Surface,
    object_tree: ObjectTree,
    background_color: Color = (20, 20, 24),
) -> None:
    surface.fill(_color_tuple(background_color))
    _render_node(surface, object_tree)


def interpolating_render_object_tree(
    surface: pygame.Surface,
    object_tree: ObjectTree,
    background_color: Color = (20, 20, 24),
    interpolating_factor: int = 1,
    after_render: Callable[[], None] | None = None,
) -> None:
    if interpolating_factor < 1:
        raise ValueError("interpolating_factor must be greater than or equal to 1")

    new_splats = _flatten_splats(object_tree)

    for step in range(1, interpolating_factor + 1):
        t = step / interpolating_factor
        surface.fill(_color_tuple(background_color))

        for splat in new_splats:
            _render_splat(surface, _interpolated_splat(splat, t))

        if after_render is not None:
            after_render()

    global _previous_interpolation_splats
    _previous_interpolation_splats = {
        splat.id: _snapshot_splat(splat)
        for splat in new_splats
        if splat.id is not None
    }


def _render_node(surface: pygame.Surface, node: ObjectTree) -> None:
    if isinstance(node, Splat):
        _render_splat(surface, node)
        return

    for child in node:
        _render_node(surface, child)


def _render_splat(surface: pygame.Surface, splat: Splat) -> None:
    y, x = _position_tuple(splat.pos)
    asset = splat.asset
    draw_x, draw_y = _top_left(asset, x, y)
    rect = pygame.Rect(draw_x, draw_y, asset.width, asset.height)

    if isinstance(asset, Rect):
        pygame.draw.rect(surface, _color_tuple(asset.color), rect)
    elif isinstance(asset, Elipse):
        pygame.draw.ellipse(surface, _color_tuple(asset.color), rect)
    else:
        surface.blit(asset.image, rect)


def _flatten_splats(object_tree: ObjectTree) -> list[Splat]:
    if isinstance(object_tree, Splat):
        return [object_tree]

    splats: list[Splat] = []
    for child in object_tree:
        splats.extend(_flatten_splats(child))
    return splats


def _interpolated_splat(splat: Splat, t: float) -> Splat:
    if splat.id is None or splat.id not in _previous_interpolation_splats:
        return splat

    old_splat = _previous_interpolation_splats[splat.id]
    old_y, old_x = _position_tuple(old_splat.pos)
    new_y, new_x = _position_tuple(splat.pos)
    interpolating_fn = splat.interpolating_fn
    change = interpolating_fn(t) if interpolating_fn is not None else t

    if change < 0 or change > 1:
        raise ValueError("interpolating_fn must return a value between 0 and 1")

    return Splat(
        splat.asset,
        (
            old_y + (new_y - old_y) * change,
            old_x + (new_x - old_x) * change,
        ),
        splat.id,
        splat.interpolating_fn,
    )


def _snapshot_splat(splat: Splat) -> Splat:
    return Splat(
        splat.asset,
        _position_tuple(splat.pos),
        splat.id,
        splat.interpolating_fn,
    )


def _position_tuple(pos: Position) -> tuple[float, float]:
    y, x = pos
    return y, x


def _top_left(asset: Asset, x: float, y: float) -> tuple[float, float]:
    if asset.coordinate_placing is CoordinatePlacing.TOP_LEFT:
        return x, y

    return x - asset.width / 2, y - asset.height / 2


def _validate_scaling_factor(scaling_factor: float) -> None:
    if scaling_factor <= 0:
        raise ValueError("scaling_factor must be greater than 0")


def _color_tuple(color: Color) -> ColorTuple:
    if isinstance(color, RGB | HSV):
        return color.color
    return color


def main(
    program: VisualProgram,
    *,
    size: tuple[int, int] = (800, 600),
    fps: int = 60,
    title: str = "pygame renderer",
    background_color: Color = (20, 20, 24),
    interpolating_factor: int = 1,
) -> None:
    if interpolating_factor < 1:
        raise ValueError("interpolating_factor must be greater than or equal to 1")

    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        program.step()
        object_tree = program.get_object_tree()

        if interpolating_factor == 1:
            render_object_tree(screen, object_tree, background_color)
            pygame.display.flip()
            clock.tick(fps)
        else:
            interpolating_render_object_tree(
                screen,
                object_tree,
                background_color,
                interpolating_factor,
                lambda: _finish_interpolation_frame(clock, fps, interpolating_factor),
            )

    pygame.quit()


def _finish_interpolation_frame(
    clock: pygame.time.Clock,
    fps: int,
    interpolating_factor: int,
) -> None:
    pygame.display.flip()
    clock.tick(fps * interpolating_factor)
