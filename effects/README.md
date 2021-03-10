# Effects
This is where objects used for the subeffects.py file's effects are stored. Add your own if interested.

## Sprite
Draws spinning (possible spin speed 0), scalable (keys 0 and +) .png image that is movable with 'ijkl'. PGDN cycles through other controllable surfaces, so if you for instance have multiple instances of this class, you can move them all individually by cycling through them.

* ArcSprite: moves a Sprite object in a circle.

* SweepSprite: moves a Sprite object on a line with a circular pulse.

## Stars
Produces n white circles on the screen, sized between minsize and maxsize in radius. A starry sky.

## Spotlight
Makes a spotlight: hides flickering images under black, and show them only through a circle on your cursor. Can be resized.

# Usage
Place any effects as instances of these classes into the 'effects' list in the main function.

This feature is somewhat experimental, and requires some programming to make use of. This is, after all a personal project. Usability comes second.