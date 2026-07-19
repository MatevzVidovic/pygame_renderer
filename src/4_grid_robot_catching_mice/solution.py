"""Write the robot strategy here; it can use normal sequential Python."""

from problem_driver import Direction, Ops, InitOps, GameModeEnum

"""

# Description of the problem:

You control a robot/cat, which tries to catch a mouse.
Whenever you move, the mouse moves also.
You can move LEFT, RIGHT, UP, DOWN,
while the mouse can also move diagonally, and can also stay in its current spot.
You win the game when both you and the mouse move into the same square - you catch the mouse.

## Mouse movement description:

The mouse moves in each each of its 9 directions with uniform probability.
If it cannot move to any of those directions (e.g. it is in a corner) 
the available directions proportionally increase in likelihood.


# You have 3 fns you can use:

## 2 scouting fns:

ops.scout_for_mouse() -> numpy array with 2 elements
ops.scout_yourself() -> numpy array with 2 elements

These return a numpy array of integer coordinates on the grid.
You can get the coordinates in this way:

y = delta[0]
x = delta[1]

We use the standard coordinates of arrays and image processing
(which differ from the usual graphing coordinate system):

y \\ x ->
| [] [] [] []
v [] [] [] [M]
  [R] [] [] []
  [] [] [] []

So R has coordinates 2, 0
And M has coordinates 1, 3


Numpy arrays are implemented as vectors, which means you can do arithmetic with them:
a = np.array([3, 7])
b = np.array([-2, 1])
c = a + b  # equals np.array([1, 8])

 

## 1 movement fn:

ops.move(Direction.sth) ->
It returns a bool of: Was the move successful?
A move is not successful if you bump into the edge of the grid.

As its argument (Direction.sth) you can use:
Direction.LEFT
Direction.RIGHT
Direction.UP
Direction.DOWN



# Hints:

To read hints, paste them into chat-gpt and tell it to translate from pig latin.


## Basic info hints (can be read at the start. They don't reveal anything.):

But these hints might confuse you.
They are simply information on helpful functions/things what can be used in the language.
Not all of these hints are necessarily useful.

## Hint 1

In python, you can use this fn on any integer:
abs(a) # gives absolute value of a


## Solution hints (skip at first, then read them one-by-one in their order):

### Hint 1

First try to define the direction from the robot/cat to the mouse and work with that.

### Hint 2

A good first implementation is to first try to match one of the coordinates by moving towards the mouse.
And if that one is already matched, try to match the second one also.
You will generally be moving towards the mouse and increase your chances of a hit.


## Optimization hints (read later):

### Hint 1

Try to move in the one of the 4 predefined directions that is 
the most similar to the direction from the robot to the mouse.
Not trying to match one coordinate first, and then the other,
but instead figuting out the best direction at the moment.



# More complicated versions of the game

At the top of `main()` you can select a game mode:

from problem_driver import GameModeEnum, InitOps
InitOps.set_game_mode(GameModeEnum.MARKOV_CHAIN)

Set the mode before making any calls to `ops.move()`.

## AVOIDANT

Use `InitOps.set_game_mode(GameModeEnum.AVOIDANT)` to make the mouse prefer
legal moves that leave it farther from the robot. It still chooses randomly, so
it is not perfectly predictable.

## MARKOV_CHAIN

Use `InitOps.set_game_mode(GameModeEnum.MARKOV_CHAIN)`
so that the mouse doesn't move uniformly,
but instead starts out with random probabilities for each direction of movement.

## Hints

### Optimization hints (read later):

### Hint 1:

Before each move, scout the position of the mouse.
After each move, scout where the mouse landed.
You can use that data to make a guess at the markov chain matrix it is 
using and approach it faster.

### Hint 2:

Don't take the movements that happened so far at their face value.
Perhaps you used the approach of:
m = matrix_of_moves_so_far
p = matrix_of_moves_so_far / sum_of_elements(matrix_of_moves_so_far)
(frequentist approach)

Instead use a bayesian approach, where you assume some initial distribution,
and update it based on how the mouse moves.




"""


def main(ops: Ops) -> None:

    InitOps.set_game_mode(GameModeEnum.AVOIDANT)
    # InitOps.set_game_mode(GameModeEnum.MARKOV_CHAIN)

    while True:
        print("ja")
        print(ops.scout_yourself())
        cat = ops.scout_yourself()
        print(ops.scout_for_mouse())
        maus = ops.scout_for_mouse()
        delta = maus - cat
        print(delta)
        y = delta[0]
        x = delta[1]
        if x < 0 and y < 0:
            if abs(x) > abs(y):
                ops.move(Direction.LEFT)
            else:
                ops.move(Direction.UP)
        elif x < 0 and y >= 0:
            if abs(x) > abs(y):
                ops.move(Direction.LEFT)
            else:
                ops.move(Direction.DOWN)
        elif x >= 0 and y < 0:
            if abs(x) > abs(y):
                ops.move(Direction.RIGHT)
            else:
                ops.move(Direction.UP)
        else:
            if abs(x) > abs(y):
                ops.move(Direction.RIGHT)
            else:
                ops.move(Direction.DOWN)

    ## Showcase of how fns can be used

    # Each move waits until the requested move has been drawn before returning.
    # print(ops.scout_yourself())
    # print("aaaa")
    # for i in range(8):
    #     ops.move(Direction.RIGHT)
    #     mouse_pos = ops.scout_for_mouse()
    #     print(mouse_pos)
    # ops.move(Direction.DOWN)
    # ops.move(Direction.LEFT)
    # ops.move(Direction.UP)

    ## Solutions:

    ## Basic game, hint 2 solution
    # while True:
    #     print("ja")
    #     print(ops.scout_yourself())
    #     cat = ops.scout_yourself()
    #     print(ops.scout_for_mouse())
    #     maus = ops.scout_for_mouse()
    #     delta = maus - cat
    #     print(delta)
    #     y = delta[0]
    #     x = delta[1]
    #     if x < 0 and y < 0:
    #         if abs(x) > abs(y):
    #             ops.move(Direction.LEFT)
    #         else:
    #             ops.move(Direction.UP)
    #     elif x < 0 and y >= 0:
    #         if abs(x) > abs(y):
    #             ops.move(Direction.LEFT)
    #         else:
    #             ops.move(Direction.DOWN)
    #     elif x >= 0 and y < 0:
    #         if abs(x) > abs(y):
    #             ops.move(Direction.RIGHT)
    #         else:
    #             ops.move(Direction.UP)
    #     else:
    #         if abs(x) > abs(y):
    #             ops.move(Direction.RIGHT)
    #         else:
    #             ops.move(Direction.DOWN)
