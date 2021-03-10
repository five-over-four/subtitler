# Subtitler / Random image tiler

NOTE: the entire design is being currently overhauled, information here can be outdated.

For animating subtitles/play lines over randomly flickering sets of images with some built-in visual effects using your own images. Built for a personal creative project as a way of automating animation work and subtitling.

![Sample image](https://i.imgur.com/3GEpYfE.png)

## Usage
First, create directories in 'picks' that each contain same-sized images (can vary between directories).

An example configuration: In 'picks', a text file 'example.txt' and a directory named 'example', containing images of the same size. In 'example.txt', the following contents:

    Hello world.
    I am here,
    as are you.

Now, when you press any of the keys not mentioned below, you will cycle through the lines in order with a crossfaded animation.

* The format of the "Tiles" setting when starting up is 'x y'. So if you want a 3 by 2 tiling, write '3 2' without the quotes.

## Speaker - Dialogue mode
If your line of text contains a '#', then the line will get split by it to a 'speaker' and 'dialogue' configuration, as shown in the following image:

![](https://i.imgur.com/VubJ7nk.png)

## Controls
    D               -   Switch to next image directory (in alphabetical order).
    A               -   Reload text file.
    +/-             -   Resize selected control surface.
    ijkl            -   Move control surface (if movable).
    PGUP/PGDN       -   Cycle through control surfaces.
    B               -   Enable background image.
    Right / Left    -   Change background image.
    ESC             -   Quit.
    ENTER           -   Reset to the first line of text.
    Z,X,C           -   Next line of text.
    1-9             -   Toggle effects (in the list 'effects', bottom of code).

* Directory switching allows for 'scene-switching' by letting you make directories with differently themed images and text files.

## Backgrounds
Place a custom image with a transparency layer into ./picks/backgrounds to enable with 'b'.

## Effects
These are somewhat experimental and only really written for my personal use, so they require a bit of programming to work. They are created in a list in the `__main__()` part of the program, in the list `effects`. Currently there's a few types that draw stars and draw sprites.