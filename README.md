

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

In the simplest cae, the tree ovf objects you are maintaining in a visual or a game can simply be a list.
Like, just have them listed sequentially as you want them to be rendered (with overlapping objects, the later one will be rendered on top).