

# Programming with visuals

This repo is not about making general non-programming games (I dont feel like it, honestly. Too much work.)

I want to do some programming with visuals: where what I code produces some visual result and i can visually see the behaviour of the code.
It's just so fun.

The repo is about 2 things:
- making some system with starting conditions that interestingly evolves over time (differential equations, cellular automata...)
- making visual programming challenges: The farmer was replaced is an inspiration for this. But I'm not making continueos evolution game kinda thing, but rather separate levels that are coding challenges for coding something up, where that thing can be represented visually. And you give the player an object with nice a nice interface, and they just call the fns, and the array in the background evolves over time, and it is rendered on the screen (like a drone on a field). And it makes programming so much more fun. And really complex challenges can be represented in this way.

## For the renderer

I've considered a few approaches:

### manim

Manim lib is really cool for making math images and visualizations (transformations of 2d and 3d space, rendering equations)
But it doesnt do real time - it only renders a video.
And it would be hard to actually make cellular automata or games with it.

### Export or stream to Godot

Make the code that calculates positions of objects over time and export the positions to Godot, or even stream in real time.
Or possibly even do it in Godot code itself.

This was inspired by how we used Julia for calculation of planet positions of th n-body problem, which we then displayed in Unity.

This is cool and all, and really the only way to do 3d visuals.
But is is a lot more complicated then the next option.

### PyGame

Just have a python tree (list of lists of lists...) of objects that will be rendered (rects, circles, image rects).
And have an fn that takes that tree, clears the frame, and then sequentially renders the objects in the tree with recursion.
(In the simplest case, the tree of objects you are maintaining in a visual or a game can simply be a list.
Like, just have them listed sequentially as you want them to be rendered (with overlapping objects, the later one will be rendered on top).)

The renderer fn should take some sort of object Splat:
In some form like: (asset: Asset, pos: iterable)
Where iterable is supposed to have 2 elements, like (pos_y, pos_x).
And since we define it with the general iterable, we can also put in slices (views) of numpy arrays, which makes things efficient,
since in our visuals and games we will probably simply be computing positions with numpy arrays.

And Asset isn't really an object type, but really one of 3 types:
- Rect
- Elipse
- ImgRect

They all have:
- width
- height (can be None)
- coordinate_placing: (the type is an enum. We have 2 types for now: CENTER and TOP_LEFT. And the default is CENTER.)

But Rect and Elipse also have .color. 
And with them, if height is None, it is the same as width.

And ImgRect also has .image.
And the constructor for ImgRect takes a path to the img, loads it up, and scales it to width and height.
Here, if height is None, it becomes a number that retains dimensions of the loaded img.


#### Final design:

And you just have:
- renderer.py 
which will have the described renderer fn and the main fn that is the game loop that is trigered.
The main fn take takes an object that has fns: .step() and .get_object_tree().
And it just does: step, get object tree, cleqar, and then calls the rendering fn.
And make an interface there for objects that have these fns.

- Then make a simple_test.py where you import main and the interface, 
and you define a simple object that satisfies that interface, 
and then you just run main where you give it that object, and we can see the visuals happening.

## Interpolation

The interpolation renderer is implemented separately in `core/interpolation.py` and
re-exported through `core/renderer.py`. See `INTERPOLATION.md` for the full design,
usage, and diagrams.

## Presentation and Video

`main(...)` renders each frame into an offscreen pygame `Surface`. In normal mode,
that finished frame is blitted to the display and flipped. In video mode, the same
finished frame is written to an `ffmpeg` raw RGB pipe instead:

```python
main(
    visual,
    video_render=True,
    video_params={
        "output_path": "render.mp4",
        "num_frames": 300,
        "quality": 18,
        "preset": "medium",
    },
)
```

`quality` maps to ffmpeg `crf`, where lower numbers mean higher quality.
`num_frames` is the number of simulation steps to run; interpolation can produce
multiple video frames for each step.

## Perspective Warp

`main(...)` can apply a final perspective post-process before presenting a frame
to the screen or writing it to video:

```python
main(
    visual,
    perspective_params=PerspectiveWarp(
        (800, 600),
        horizon=0.30,
        depth=3.0,
        background=(20, 20, 30),
    ),
)
```

The world still renders normally into a 2D frame first. The warp is applied only
at the final output step.
