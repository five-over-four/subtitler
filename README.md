# Subtitler / Random image tiler

For animating subtitles/play lines over randomly flickering sets of images with some built-in visual effects using your own images. Built for a personal creative project as a way of automating animation work and subtitling. Works as a fun little desktop screensaver as well.

![Sample image](https://i.imgur.com/3GEpYfE.png)

## Usage
Drop your images (ideally the same size) in a directory in 'pics' and the program will generate a text file with the same name as the directory. Write into it. Using z,x,c, you can cycle through the lines so as to overlay subtitles. Enter the resolution at the startup in terms of screen *height*: 1080 leads to 1920 x 1080.

## Speaker - Dialogue mode
If your line of text contains a '#', then the line will get split by it to a 'speaker' and 'dialogue' configuration, as shown in the following image:

![](https://i.imgur.com/VubJ7nk.png)

## Controls
    D               -   Switch to next image directory (in alphabetical order).
    A               -   Reload text file.
    ENTER           -   Reset to the first line of text.
    Z,X,C           -   Next line of text.
    +/-             -   Resize selected control surface.
    ijkl            -   Move control surface (if movable).
    PGUP/PGDN       -   Cycle through control surfaces.
    B               -   Enable background image.
    Right / Left    -   Change background image.
    ESC             -   Quit.
    1-9             -   Toggle effects (in the list 'effects', bottom of code).
    Mouseclick      -   Focus spotlight effect if enabled.

* Directory switching allows for 'scene-switching' by letting you make directories with differently themed images and text files.

* Using transparent backgrounds allows for nice mood-setting, such as a sunset or sunrise. I produce mine via GIMP.

## Effects
These are somewhat experimental and only really written for my personal use, so they require a bit of programming to work. They are created in a list in the `main()` function. Currently there's a few types, which are outlined in the 'effects' directory REAMDE.