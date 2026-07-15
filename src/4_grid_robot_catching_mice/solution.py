"""Write the robot strategy here; it can use normal sequential Python."""

from problem_driver import Direction, Ops


def main(ops: Ops) -> None:
    # Each move waits until the requested move has been drawn before returning.
    for i in range(8):
        ops.move(Direction.RIGHT)
        mouse_pos = ops.scout_for_mouse()
        print(mouse_pos)
    ops.move(Direction.DOWN)
    ops.move(Direction.LEFT)
    ops.move(Direction.UP)
