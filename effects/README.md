# Effects
This is where objects used for the subeffects.py file's effects are stored. Add your own if interested.

## Sprite
Draws spinning (possible spin speed 0), scalable (keys 0 and +) .png image that is movable with 'ijkl'. PGDN cycles through other controllable surfaces, so if you for instance have multiple instances of this class, you can move them all individually by cycling through them.

* ArcSprite: moves a Sprite object in a circle.

* SweepSprite: moves a Sprite object on a line with a circular pulse.

## Stars
Produces n white circles on the screen, sized between minsize and maxsize in radius. A starry sky.

## Spotlight
As shown in the image below. Follows the cursor. Toggle with mouse buttons and resize with +/-.

## Animation
Takes a directory in ./animations and cycles through the images in an orderly fashion with a frame timer. Essentially, produces an animated Sprite instance.

![Spotlight](https://i.imgur.com/fZnm9nj.png)

# Usage
Place any effects as instances of these classes into the 'effects' list in the main function. Alternatively, into the 'scenes' list. The files for these effects are held in ./effects, ./spotlights, and ./animations.