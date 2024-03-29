import pygame._sdl2
import pygame.locals
import os
from random import randint
from itertools import product
import math
import sub_effects
import automatic_movers

class Settings:

    '''
    This class contains all the information about the directories, screen properties, pygame
    runtime stuff. Certain effects such as the backgrounds and spotlights are kept saved here.
    Globally accessible, placed as settings = Settings() in the __main__ method.
    '''

    def __init__(self, folder, defaultres):
        self.resolution = defaultres
        self.path = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.image_set = folder # name of current image directory
        self.img_path = self.path + "pics/" + folder + "/" # actual path of the directory
        self.images = os.listdir(self.img_path) # list of filenames.
        self.speed = 15
        self.img_width, self.img_height = pygame.image.load(self.img_path + self.images[0]).get_size()
        self.x = math.ceil(self.resolution[0] / self.img_width) # number of tiles.
        self.y = math.ceil(self.resolution[1] / self.img_height)
        self.center = self.get_center()
        self.fps = 144 # set to whatever. most settings are independent of it.
        self.rng_factor = (self.fps * self.speed) // 10 # how often images switch randomly.
        self.overlay = None
        self.next_overlay(1) # 1 means 'forward', -1 'backward'.
        self.overlay_on = False

    def get_center(self):
        return (self.resolution[0] // 2, self.resolution[1] // 2)

    def refresh_rng_value(self):
        self.rng_factor = (self.fps * self.speed) // 10

    def next_overlay(self, direction):
        self.overlays = os.listdir(self.path + "overlays/")
        if len(self.overlays) > 0:
            if not self.overlay:
                self.pygame_overlay = pygame.image.load(self.path + "overlays/" + self.overlays[0])
                self.overlay_index = 0
            else:
                self.overlay_index = (self.overlay_index + direction) % len(self.overlays)
                self.pygame_overlay = pygame.image.load(self.path + "overlays/" + self.overlays[self.overlay_index])

    def next_spotlight(self, direction): # carbon copy of next_overlay; combine somehow.
        spotlights = os.listdir(self.path + "spotlights/")
        if len(spotlights) > 0:
            self.spotlight_index = (self.spotlight_index + direction) % len(spotlights)
            self.spotlight.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, pygame.image.load(self.path + "spotlights/" + spotlights[self.spotlight_index]))
            self.spotlight.TEXTURE.blend_mode = 4

    def render_overlay(self):
        self.overlay = pygame._sdl2.Texture.from_surface(renderer, self.pygame_overlay)

class DisplayFrame:

    '''
    Makes up the flickering image matrix that constitutes the lowest background layer of the
    program. give_textures() determines how quickly the images change into others in the same
    directory.
    '''

    TEXTURES = []

    def __init__(self):
        self.index = randint(0,len(settings.images)-1)
        if not DisplayFrame.TEXTURES: # first instance loads imageset.
            DisplayFrame.load_new_imageset()

    def give_textures(self): # load image and draw.
        if randint(0,settings.rng_factor) == 0: # 10 -> 1 flip/sec, 100 -> 0.01 flips/sec.
            self.index = randint(0,len(settings.images) - 1)
        return self.TEXTURES[self.index]

    @classmethod
    def load_new_imageset(self):
        pygame_images = [pygame.image.load(settings.img_path + "/" + settings.images[i]) for i in range(0, len(settings.images))]
        DisplayFrame.TEXTURES = [pygame._sdl2.Texture.from_surface(renderer, image) for image in pygame_images]

class Text:

    '''
    A single Text instance is needed to display the subtitles. Fade animations and scaling are
    done by update_font_size and some if blocks in the main function. load_surfaces should be
    rewritten later.
    '''

    def __init__(self):
        self.colour = (255,255,255)
        self.text_alpha = 0
        self.box_alpha = 0
        self.max_alpha = 225 # max alpha for the box under text.
        self.update_font_size()
        self.read_messages()
        self.index = 0 # current line number in directory.txt.
        self.next_message()
        self.texts = {} # Texture: Rect
        self.boxes = {} # Texture: Rect
        self.speaker_height = 120

    def update_font_size(self): # linear function: font_size is 40 at width 1500, 60 at 2000.
        self.font_size = (screen.size[0] - 500) // 25
        
    # creates a bunch of temporary Surfaces that are then rendered into Texture and Rect objects.
    def load_surfaces(self):
        if not self.message:
            return
        self.update_font_size()
        self.font = pygame.font.SysFont("courier", self.font_size) # first reset font at desired size (default 40).
        x, y = settings.get_center()
        self.set_subtitle_size(max(self.message, key=lambda x: len(x))) # based on the longer segment.
        text_surf = self.font.render(self.message[-1], True, self.colour)
        text_box = pygame.Surface((text_surf.get_width() + 20, text_surf.get_height() + 20))
        text_box.set_colorkey((1,2,3)) # Texture.alpha needs a colorkey to work properly.
        text_surfs = [text_surf]
        box_surfs = [text_box]
        text_rects = [text_surf.get_rect(center=(x,y))]
        box_rects = [text_box.get_rect(center=(x,y))]
        if len(self.message) > 1: # then the speaker line.
            speaker_surf = self.font.render("(" + self.message[0] + ")", True, (255,255,255))
            speaker_box = pygame.Surface((speaker_surf.get_width() + 20, speaker_surf.get_height() + 20))
            speaker_box.set_colorkey((1,2,3))
            text_surfs.append(speaker_surf)
            box_surfs.append(speaker_box)
            self.speaker_height = box_surfs[1].get_height()*1.3 # rough placement, 1.3 is arbitrary.
            text_rects.append(speaker_surf.get_rect(center=(x,y-self.speaker_height)))
            box_rects.append(speaker_box.get_rect(center=(x,y-self.speaker_height)))
        self.texts = {pygame._sdl2.Texture.from_surface(renderer, text_surf): text_rect for text_surf, text_rect in zip(text_surfs, text_rects)}
        self.boxes = {pygame._sdl2.Texture.from_surface(renderer, box_surf): box_rect for box_surf, box_rect in zip(box_surfs, box_rects)}

    def give_textures(self):
        return self.texts, self.boxes
        
    def read_messages(self): # find dirname.txt or create one if missing.
        filename = settings.path + "pics/" + settings.image_set + ".txt"
        if os.path.isfile(filename):
            with open(filename) as f:
                self.messages = f.readlines()
        else:
            open(settings.path + "pics/" + settings.image_set + ".txt", "a").close() # create missing file.

    def next_message(self): # load current index message, generate text surfaces and rects, then iterate index.
        if not self.messages:
            self.message = None
        else:
            self.message = self.messages[self.index].strip().split("#")
            self.load_surfaces()
            self.index = (self.index + 1) % len(self.messages)

    def set_subtitle_size(self, line: str): # automatic adjustment of each subtitle line to window width.
        w = self.font.size(line)[0]
        while w > settings.resolution[0]: # while text overshoots window frame.
            w = self.font.size(line)[0]
            self.font_size -= 1
            self.font = pygame.font.SysFont("courier", self.font_size)

    def purge_data(self):
        if self.message:
            self.texts.clear()
            self.boxes.clear()

def load_next_directory(text, settings):
    text.purge_data()
    while True:
        settings.current_index = (settings.current_index + 1) % len(settings.directory_list)
        try: # new directory and image data.
            settings.image_set = settings.directory_list[settings.current_index]
            settings.images = os.listdir(settings.path + "pics/" + settings.image_set)
            settings.img_path = settings.path + "pics/" + settings.image_set
            settings.img_width, settings.img_height = pygame.image.load(settings.img_path + "/" + settings.images[0]).get_size()
            settings.x = math.ceil(screen.size[0] / settings.img_width) 
            settings.y = math.ceil(screen.size[1] / settings.img_height)
            break
        except:
            continue
    text.read_messages()
    text.index = 0
    text.text_alpha = 0
    text.box_alpha = 0
    
def create_displays(settings): # tiling via x-tile * y-tile DisplayFrame objects.
    displays = [DisplayFrame() for x in range(settings.x * settings.y)]
    DisplayFrame.load_new_imageset()
    offset = product([x for x in range(settings.x)], [x for x in range(settings.y)])
    pos = [(0 + off[0] * settings.img_width, 0 + off[1] * settings.img_height) for off in offset]
    return displays, pos

# sub_effects effects are stored in a list called 'effects' in main(): each cell is toggled via 1-9.
# This function enables a cell to be a list of effects rather than a single effect, such as 
# 100 sprites at once. This is why there are if type(effect) == list checks inside main().
def toggle_effects(effects):
    if type(effects) != list:
        effects.toggle()
    else:
        for ef in effects:
            ef.toggle()

def main(settings, screen, renderer): # TODO: redesign fades.

    # pygame components, including SDL2 rendering.
    clock = pygame.time.Clock()
    buffer = pygame._sdl2.Texture(renderer, settings.resolution, target=True)
    buffer.blend_mode = 1

    # pass global parts into sub_effects
    sub_effects.renderer = renderer
    sub_effects.settings = settings
    sub_effects.screen = screen

    # EFFECTS SECTION - controls 1-9.
    # Each entry can be either a sub_effects class instance or a *list* of such instances. You can toggle each
    # instance or list of instances with keys 1-9.
    effects = [ sub_effects.Stars(400,1,4),
                sub_effects.Sprite("hand_hold_bits_gs.png", initial_scale=1.5, pos=(0,0)),
                sub_effects.Sprite("hand_point_bits_gs.png", initial_scale=1.5, pos=(0,0)),
                sub_effects.Animation("fist", frametime=30),
                sub_effects.Animation("frontfist", frametime=30, pos=(600, 440)),
                sub_effects.Animation("dice", frametime=15),
                sub_effects.Sprite("gif_test.gif"),
                [sub_effects.Animation("frontfist", frametime=30, pos=(600, 440), scale=1),
sub_effects.Animation("frontfist", frametime=30, pos=(300, 540), scale=1.5),
sub_effects.Animation("frontfist", frametime=27, pos=(800, 400), scale=0.7),
sub_effects.Animation("frontfist", frametime=24, pos=(350, 400), scale=0.7),
sub_effects.Animation("frontfist", frametime=21, pos=(750, 250), scale=0.4),
sub_effects.Animation("frontfist", frametime=18, pos=(500, 250), scale=0.4)
][::-1],
                sub_effects.Animation("frontfist", frametime=30, scale=2)
                ]

    # Call mover classes from movers.py here and invoke them on specific entries of effects[].
    movers = [automatic_movers.Mover1(effects[4])]

    settings.spotlight = sub_effects.Spotlight(os.listdir(settings.path + "spotlights/")[0], settings.resolution)
    settings.spotlight_index = 0

    # SCENES - press PGDN, PGUP to cycle through. basically, use Sprite or Animation.
    # pos=(0,0), initial_scale=2; make 960 x 540 image for 1920x1080.
    # SCENES are image files in /effects titled 001.png, 002.png, ..., 027.png etc.
    scene_files = os.listdir(os.path.dirname(os.path.realpath(__file__)) + "/effects/")
    largest_num = 0
    for filename in scene_files:
        if filename[:-4].isnumeric():
            largest_num = max(largest_num, int(filename[:-4]))
    scenes = [sub_effects.Sprite(str(i).zfill(3) + ".png", initial_scale=2, fade_speed=2) for i in range(1,largest_num+1)]
    scene_index = 0

    # rest of the generic settings
    displays, pos = create_displays(settings)
    text = Text()
    text.index = 0
    text_show = False
    fade_time = 0 # this acts as both a boolean and counter.
    fade_duration = settings.fps // 5 # 1/x seconds.
    control_index = 0
    fullscreen_toggle = False # no 'screen.is_fullscreen' in SDL2, need this.

    while True:

        renderer.target = buffer
        renderer.clear()

        # MOVER CLASSES.
        # Here we first call all the movers to move.
        for mover in movers:
            mover.move()

        # DRAWING SECTION
        # Flickering bottom layer images from a directory in /pics. Must be placed first because 100% opaque.
        for i, display in enumerate(displays):
            display.give_textures().draw(dstrect=pos[i])

        # Draw overlay with transparency. needs alpha layer or will cover panels.
        if settings.overlay_on:
            settings.overlay.draw(dstrect=(0,0))

        # If the effect cell is a list, iterate and draw, otherwise draw.
        for ef in effects:
            if type(ef) == list:
                if ef[0].opacity > 0:
                    for component in ef:
                        component.TEXTURE.draw(**component.update())
            elif ef.opacity > 0:
                ef.TEXTURE.draw(**ef.update())

        for scene in scenes:
            if scene.opacity > 0:
                scene.TEXTURE.draw(**scene.update())

        if settings.spotlight.opacity > 0:
            settings.spotlight.draw()

        # Text boxes are drawn last so that they are always visible.
        if text.text_alpha > 0 and text.message:
            for box in text.boxes:
                box.alpha = text.box_alpha
                box.draw(dstrect=text.boxes[box].topleft)
            for txt in text.texts:
                txt.alpha = text.text_alpha
                txt.draw(dstrect=text.texts[txt].topleft)

        # EVENT HANDLING SECTION
        for e in pygame.event.get():

            # uncomment if using.
            # # spotlight controls with mouse
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 3: # right click
                    settings.spotlight.toggle()
                elif e.button == 4: # scroll up (i think?)
                    settings.next_spotlight(1)
                elif e.button == 5: # scroll down
                    settings.next_spotlight(-1)

            if e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    exit()

                # show next text line / hide current one
                elif e.key in (pygame.K_z, pygame.K_x, pygame.K_c):
                    if not text_show:
                        text.text_alpha = 0
                        text.box_alpha = 0
                        text.next_message()
                    text_show ^= True
                    fade_time = 1 # access fades.
                
                # If you have large background images in 
                elif e.key in (pygame.K_RIGHT, pygame.K_LEFT):
                    if not scenes:
                        print("There are no scenes set up.")
                        break
                    if scenes[scene_index].opacity > 0:
                        scenes[scene_index].toggle()
                    if e.key == pygame.K_RIGHT:
                        scene_index = (scene_index + 1) % len(scenes)
                    else:
                        scene_index = (scene_index - 1) % len(scenes)
                    scenes[scene_index].toggle()

                elif e.key == pygame.K_t: # reload current text file. retain position.
                    text.read_messages()
                    print("Reloaded dialogue file.")

                elif e.key == pygame.K_r: # reset positions of effects.
                    for ef in effects:
                        if type(ef) == list:
                            for component in ef:
                                component.reset()
                        else:
                            ef.reset()
                    for mover in movers:
                        mover.reset()

                elif e.key == pygame.K_d: # switch directory.
                    load_next_directory(text, settings)
                    displays, pos = create_displays(settings)
                    text_show = False

                elif e.key == pygame.K_b: # toggle overlay
                    settings.overlay_on ^= True
                    if not settings.overlay:
                        settings.render_overlay()

                elif e.key == pygame.K_DOWN: # overlay switching.
                    settings.next_overlay(-1)
                    settings.render_overlay()

                elif e.key == pygame.K_UP: # other direction overlay switch.
                    settings.next_overlay(1)
                    settings.render_overlay()

                elif e.key == pygame.K_RETURN: # reset to the first line.
                    text.index = 0
                    if not text_show:
                        text.text_alpha = 0
                        text.box_alpha = 0
                        text.next_message()
                    text_show ^= True
                    fade_time = 1 # access fades

                # effect toggling. 1 to 9. 1 corresponds to 49.
                elif e.key in {x+49 for x in range(0,10)} and effects:
                    try:
                        toggle_effects(effects[e.key-49])
                        if type(effects[e.key-49]) == list:
                            if effects[e.key-49][0].opacity > 0 and hasattr(effects[e.key-49], "move"):
                                control_index = e.key - 49
                        elif effects[e.key-49].opacity > 0 and hasattr(effects[e.key-49], "move"):
                            control_index = e.key - 49
                    except:
                        print(f"Not enough items in effects list.")

                # cycle through controllable surfaces
                elif e.key in (pygame.K_PAGEDOWN, pygame.K_PAGEUP) and effects:
                    counter = 0 # we go through at most the whole list: possible that no control surface is enabled.
                    direction = -1 if e.key == pygame.K_PAGEDOWN else 1
                    control_index = (control_index + direction) % len(effects)
                    while not (hasattr(effects[control_index], "move") or hasattr(effects[control_index], "resize")) or not effects[control_index].opacity:
                        control_index = (control_index + direction) % len(effects)
                        counter += 1
                        if counter >= len(effects):
                            break
                    print(f"current control key: {control_index + 1}") # which button to press to enable this one.

                # toggle fullscreen on/off. clumsy due to lacking SDL2 functionality.
                elif e.key == pygame.K_F11:
                    fullscreen_toggle ^= True
                    if fullscreen_toggle:
                        screen.set_fullscreen()
                    else:
                        screen.set_windowed()

            # recomputing various screensize aspects after resize
            elif e.type == pygame.VIDEORESIZE:
                settings.x = math.ceil(screen.size[0] / settings.img_width)
                settings.y = math.ceil(screen.size[1] / settings.img_height)
                displays, pos = create_displays(settings)
                settings.resolution = screen.size
                buffer = pygame._sdl2.Texture(renderer, settings.resolution, target=True)
                text.update_font_size()
                print("Current resolution: %s x %s" %(settings.resolution))

            elif e.type == pygame.QUIT:
                exit()

        # FADES FOR TEXT AND BOXES. (TODO: build into classes.)
        if fade_time > 0 and text_show: # fade in
            fade_time += 1
            text.text_alpha += 255 // fade_duration
            text.box_alpha += text.max_alpha // fade_duration
        elif fade_time > 0 and not text_show: # fade out
            fade_time += 1
            text.text_alpha -= 255 // fade_duration
            text.box_alpha -= text.max_alpha // fade_duration
        if fade_time > fade_duration: # fade has finished.
            fade_time = 0

        # RESIZING CONTROL SECTION
        resize_factor = 0
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_PLUS] or pressed[pygame.K_MINUS]:
            resize_factor += 1 if pressed[pygame.K_PLUS] else -1
            
        # MOVEMENT CONTROL SECTION
        direction = [0,0]
        if pressed[pygame.K_i]:
            direction[1] -= 1
        if pressed[pygame.K_j]:
            direction[0] -= 1
        if pressed[pygame.K_k]:
            direction[1] += 1
        if pressed[pygame.K_l]:
            direction[0] += 1

        # apply controls
        if effects:
            ef = effects[control_index]
            if hasattr(ef, "move"):
                ef.move(direction)
            if settings.spotlight.opacity > 0: # takes precedent over sprites.
                settings.spotlight.resize(resize_factor)
            elif hasattr(ef, "resize"):
                ef.resize(resize_factor)
                
        renderer.target = None
        buffer.draw()
        renderer.present() 
        clock.tick(settings.fps)

def delete_old_textfiles(directory, dirnames):
    files = [file for file in os.listdir(directory) if ".txt" in file]
    for filename in files:
        if filename[:-4] not in dirnames:
            os.remove(directory + filename)

# STARTUP CONFIGURATION - directory choice and resolution.
# you want to put all the image directories into ./pics, 'tmp' ignored.
if __name__ == "__main__":

    possible_directories = []
    hub_path = os.path.dirname(os.path.realpath(__file__)) + "/pics/"
    dir_names = os.listdir(hub_path)
    for i in dir_names:
        if os.path.isdir(hub_path + i) and i != "tmp" and i != "overlays":
            possible_directories.append(i)
    print("#" * 40)
    print("# Available directories:" + " "*15 + "#")
    for i, name in enumerate(possible_directories):
        print("# {:1}. {:33} #".format(i + 1, name))
    print("#" * 40)

    while "entering config":
        try:
            dir_choice = input("Directory\n> ") # name or number
            res_choice = input("Resolution\n> ") # width, always 16:9
            resolution = (int(res_choice)*16//9, int(res_choice))

            if dir_choice.isnumeric():
                settings = Settings(possible_directories[int(dir_choice)-1], resolution)
                settings.current_index = int(dir_choice) - 1
            else:
                tmp_index = possible_directories.index(dir_choice)
                settings = Settings(possible_directories[tmp_index], resolution)
                settings.current_index = tmp_index
            settings.directory_list = possible_directories
            break

        except IndexError:
            print(f"The image directory is empty.")

        except Exception as e:
            print(f"Incorrect input: {e}.")

    screen = pygame._sdl2.Window("...", size=resolution, resizable=True)

    delete_old_textfiles(hub_path, dir_names)
    print("Current resolution: %s x %s" %(settings.resolution))
    renderer = pygame._sdl2.Renderer(screen, vsync=True)
 
    pygame.init()
    main(settings, screen, renderer)