# Subtitler / Random image tiler

For animating subtitles/play lines over randomly flickering sets of images with some built-in visual effects using your own images. Built for a personal creative project as a way of automating animation work and subtitling. Works as a fun little desktop screensaver as well.

* Custom animations (put separate frames in order in ./animations)

* 8-directional spritesheets (put in order in ./directional_sprites)

* Various other features in drawing moving images.

![Sample image](https://i.imgur.com/3GEpYfE.png)

## Usage

### Flickering background panels
Drop your images (ideally the same size) in a directory in 'pics' and the program will generate a text file with the same name as the directory. Write into it. Using z,x,c, you can cycle through the lines so as to overlay subtitles. 

### Transparent overlays
Put your transparent images into ./overlays, enable with 'b' and cycle through with right/left. Ideally the equal or larger size to your use-resolution.

### Effects
Various types of animations, spritesheets, path-animated sprites, backgrounds, scene-settings are supported. Found in sub_effects.py. Place instances of these effect classes in the list 'effects' in subtitler.main(). Place the images used by these effects into ./effects.

### Spotlights
Toggle a spotlight with left click, cycle through styles with the mousewheel. Place your textures into ./spotlights. The images should have no transparency; black is opaque, any other colour is incrementally more see-through as it gets lighter (and whiter).

*Additionally, the list 'scenes' is for *cycling* through effects with fades in-between. This allows for scene transitions easily with PGDN, PGUP.*

## Speaker - Dialogue mode
If your line of text contains a '#', then the line will get split by it to a 'speaker' and 'dialogue' configuration, as shown in the following image:

![](https://i.imgur.com/VubJ7nk.png)

## Controls
    D               -   Switch to next image directory (in alphabetical order).
    Z,X,C           -   Next line of text.
    A               -   Reload text file.
    ENTER           -   Reset to the first line of text.
    +/-             -   Resize selected control surface.
    ijkl            -   Move control surface (if movable).
    PGUP / PGDN     -   Cycle through control surfaces.
    B               -   Enable background overlay.
    Up / Down       -   Change background overlay.
    Right / Left    -   Switch scene.
    1-9             -   Toggle effects.
    Mouseclick      -   Toggle spotlight.
    Scroll wheel    -   Cycle through spotlights.
    F11             -   Toggle fullscreen.
    ESC             -   Quit.

## The purpose of this project
I wrote this project to help me with animating and subtitling a personal creative project, so it may not be particularly useful to anyone else. However, it does offer a few 'fun' features for other users, such as acting as a neat-looking screensaver.

Due to this being for personal use, making use of its full set of features may be a little difficult.