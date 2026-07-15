"""Shared domain state for the grid-robot problem."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class State:
    robot_pos: np.ndarray
    mouse_pos: np.ndarray
