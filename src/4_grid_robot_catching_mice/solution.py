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

Irst~fay y~tray o~tay efine~day e~thay irection~day om~fray e~thay obot~ray/at~cay o~tay e~thay ouse~may and~way ork~way
ith~way at~thay.

### Hint 2

A~way ood~gay irst~fay implementation~way is~way o~tay irst~fay y~tray o~tay atch~may one~way of~way e~thay
oordinates~cay y~bay oving~may owards~tay e~thay ouse~may.
And~way if~way at~thay one~way is~way already~way atched~may, y~tray o~tay atch~may e~thay econd~say one~way also~way.
Ou~yay ill~way enerally~gay e~bay oving~may owards~tay e~thay ouse~may and~way increase~way our~yay ances~chay of~way
a~way it~hay.


## Optimization hints (read later):

### Hint 1

Y~tray o~tay ove~may in~way e~thay one~way of~way e~thay 4 edefined~pray irections~day at~thay is~way
e~thay ost~may imilar~say o~tay e~thay irection~day om~fray e~thay obot~ray o~tay e~thay ouse~may.
Ot~nay ying~tray o~tay atch~may one~way oordinate~cay irst~fay, and~way en~thay e~thay other~way,
ut~bay instead~way iguting~fay out~way e~thay est~bay irection~day at~way e~thay oment~may.



# More complicated versions of the game

At~way e~thay op~tay of~way `main()` ou~yay an~cay elect~say a~way ame~gay ode~may:

from problem_driver import GameModeEnum, InitOps
InitOps.set_game_mode(GameModeEnum.MARKOV_CHAIN)

Et~say e~thay ode~may efore~bay aking~may any~way alls~cay o~tay `ops.move()`.

## AVOIDANT

Use~way `InitOps.set_game_mode(GameModeEnum.AVOIDANT)` o~tay ake~may e~thay ouse~may efer~pray
egal~lay oves~may at~thay eave~lay it~way arther~fay om~fray e~thay obot~ray. It~way ill~stay ooses~chay andomly~ray,
o~say
it~way is~way ot~nay erfectly~pay edictable~pray.

## MARKOV_CHAIN

Use~way `InitOps.set_game_mode(GameModeEnum.MARKOV_CHAIN)`
o~say at~thay e~thay ouse~may oes~day't~nay ove~may uniformly~way,
ut~bay instead~way arts~stay out~way ith~way andom~ray obabilities~pray or~fay each~way irection~day of~way ovement~may.

## Hints

### Optimization hints (read later):

### Hint 1:

Efore~bay each~way ove~may, out~scay e~thay osition~pay of~way e~thay ouse~may.
After~way each~way ove~may, out~scay ere~whay e~thay ouse~may anded~lay.
Ou~yay an~cay use~way at~thay ata~day o~tay ake~may a~way uess~gay at~way e~thay arkov~may ain~chay atrix~may it~way
is~way
using~way and~way approach~way it~way aster~fay.

### Hint 2:

On~day't~nay ake~tay e~thay ovements~may at~thay appened~hay o~say ar~fay at~way eir~thay ace~fay alue~vay.
Erhaps~pay ou~yay used~way e~thay approach~way of~way:
m = matrix_of_moves_so_far
p = matrix_of_moves_so_far / sum_of_elements(matrix_of_moves_so_far)
(equentist~fray approach~way)

Instead~way use~way a~way ayesian~bay approach~way, ere~whay ou~yay assume~way ome~say initial~way istribution~day,
and~way update~way it~way ased~bay on~way ow~hay e~thay ouse~may oves~may.




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
