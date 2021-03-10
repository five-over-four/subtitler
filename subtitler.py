import pygame
import pygame._sdl2
import os
from random import randint, choice
from PIL import Image
from itertools import product
from math import ceil
import sub_effects

pygame.init()

# every class has functions with a need to access these.
# they are also singletons, so this makes *some* sense.
class Globals:
    settings = None
    screen = None
    renderer = None

class Settings:

    def __init__(self, folder, defaultres):
        self.resolution = defaultres
        self.hub_path = os.path.dirname(os.path.realpath(__file__)) + "/pics/"
        self.image_set = folder # name of the directory
        self.path = self.hub_path + folder # actual path of the directory
        self.images = os.listdir(self.path) # list of filenames.
        self.speed = 15
        self.img_width, self.img_height = Image.open(self.path + "/" + self.images[0]).size
        self.x = ceil(self.resolution[0] / self.img_width) # number of tiles.
        self.y = ceil(self.resolution[1] / self.img_height)
        self.center = self.get_center()
        self.fps = 144 # set to whatever. most settings are independent of it.
        self.rng_factor = (self.fps * self.speed) // 10 # how often images switch randomly.
        self.background = None
        self.next_background(1) # 1 means 'forward', -1 'backward'.
        self.bg_index = 0
        self.bg_on = False

    def get_center(self):
        return (self.resolution[0] // 2, self.resolution[1] // 2)

    def refresh_rng_value(self):
        self.rng_factor = (self.fps * self.speed) // 10

    def next_background(self, direction):
        self.backgrounds = os.listdir(self.hub_path + "backgrounds")
        if len(self.backgrounds) > 0:
            if self.background == None:
                self.pygame_background = pygame.image.load(self.hub_path + "backgrounds/" + self.backgrounds[0])
            else:
                self.bg_index = (self.bg_index + direction) % len(self.backgrounds)
                self.pygame_background = pygame.image.load(self.hub_path + "backgrounds/" + self.backgrounds[self.bg_index])

    def render_background(self):
        self.background = pygame._sdl2.Texture.from_surface(Globals.renderer, self.pygame_background)

class DisplayFrame:

    TEXTURES = []

    def __init__(self):
        self.index = randint(0,len(Globals.settings.images)-1)
        if not DisplayFrame.TEXTURES: # first instance loads imageset.
            DisplayFrame.load_new_imageset()

    def give_textures(self): # load image and draw.
        if randint(0,Globals.settings.rng_factor) == 0: # 10 -> 1 flip/sec, 100 -> 0.01 flips/sec.
            self.index = randint(0,len(Globals.settings.images) - 1)
        return self.TEXTURES[self.index]

    @classmethod
    def load_new_imageset(self):
        pygame_images = [pygame.image.load(Globals.settings.path + "/" + Globals.settings.images[i]) for i in range(0, len(Globals.settings.images))]
        DisplayFrame.TEXTURES = [pygame._sdl2.Texture.from_surface(Globals.renderer, image) for image in pygame_images]

class Text:

    def __init__(self):
        self.update_font_size()
        self.read_messages() # list of all lines in directory.txt.
        self.index = 0 # current line number in directory.txt.
        self.next_message()
        self.text_surfs = [] # rewrite into dict format surf: rect or so.
        self.box_surfs = []
        self.text_rects = []
        self.box_rects = []
        self.text_alpha = 0
        self.box_alpha = 0
        self.max_alpha = 230 # for boxes.
        self.speaker_height = 120

    def update_font_size(self): # linear function: font_size is 40 at width 1500, 60 at 2000.
        self.font_size = (Globals.screen.size[0] - 500) // 25

    def load_surfaces(self): # this is a bit unwieldy. rewrite.
        if not self.message:
            return
        self.update_font_size()
        self.font = pygame.font.SysFont("courier", self.font_size) # first reset font at desired size (default 40).
        x, y = settings.get_center()
        if len(self.message) > 1: # speaker # line format.
            self.set_subtitle_size(self.message[1])
            text_surf = self.font.render(self.message[1], True, (255,255,255))
            speaker_surf = self.font.render("(" + self.message[0] + ")", True, (255,255,255))
            text_box = pygame.Surface((text_surf.get_rect().width + 20, text_surf.get_rect().height + 20))
            speaker_box = pygame.Surface((speaker_surf.get_rect().width + 20, speaker_surf.get_rect().height + 20))
            text_box.set_colorkey((1,2,3)) # this is a workaround.
            speaker_box.set_colorkey((1,2,3))
            self.text_surfs = [text_surf, speaker_surf]
            self.box_surfs = [text_box, speaker_box]
            height = self.box_surfs[1].get_height()*1.3
            self.text_rects = [text_surf.get_rect(center=(x,y)), speaker_surf.get_rect(center=(x,y-self.speaker_height))]
            self.box_rects = [text_box.get_rect(center=(x,y)), speaker_box.get_rect(center=(x,y-self.speaker_height))]
        else: # regular line without speaker.
            self.set_subtitle_size(self.message[0])
            text_surf = self.font.render(self.message[0], True, (255,255,255))
            text_box = pygame.Surface((text_surf.get_rect().width + 20, text_surf.get_rect().height + 20))
            text_box.set_colorkey((1,2,3))
            self.text_surfs = [text_surf]
            self.box_surfs = [text_box]
            self.text_rects = [text_surf.get_rect(center=(x,y))]
            self.box_rects = [text_box.get_rect(center=(x,y))]
        self.text_textures = [pygame._sdl2.Texture.from_surface(Globals.renderer, text_surf) for text_surf in self.text_surfs]
        self.box_textures = [pygame._sdl2.Texture.from_surface(Globals.renderer, box_surf) for box_surf in self.box_surfs]

    def give_textures(self):
        return (self.text_textures, self.text_rects, self.box_textures, self.box_rects)
        
    def read_messages(self): # find dirname.txt or create one if missing.
        filename = settings.hub_path + "/" + settings.image_set + ".txt"
        if os.path.isfile(filename):
            with open(filename) as f:
                self.messages = f.readlines()
        else:
            open(settings.hub_path + "/" + settings.image_set + ".txt", "a").close() # create missing file.

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
        self.text_surfs.clear()
        self.box_surfs.clear()
        self.text_rects.clear()
        self.box_rects.clear()
        self.text_textures.clear()
        self.box_textures.clear()

def load_next_directory(text, settings): # modifies relevant objects.
    text.purge_data()
    # first load the new files into Settings(), skipping empty directories.
    while True:
        settings.current_index = (settings.current_index + 1) % len(settings.directory_list)
        try:
            settings.image_set = settings.directory_list[settings.current_index]
            settings.images = os.listdir(settings.hub_path + settings.image_set)
            settings.path = settings.hub_path + settings.image_set
            settings.img_width, settings.img_height = Image.open(settings.path + "/" + settings.images[0]).size
            settings.x = ceil(screen.size[0] / settings.img_width) 
            settings.y = ceil(screen.size[1] / settings.img_height)
            break
        except:
            continue
    # then make the changes to Text()
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

def main(settings, screen): # todo: redesign blitting, fades, sdl2 functionality.

    # pygame components, including SDL2 compliant rendering.
    clock = pygame.time.Clock()
    renderer = pygame._sdl2.Renderer(screen, vsync=False)
    buffer = pygame._sdl2.Texture(renderer, settings.resolution, target=True)
    buffer.blend_mode = 1

    # pass global parts into sub_effects.py and Globals for simpler function calls (bad idea?)
    sub_effects.renderer = renderer
    sub_effects.settings = settings
    sub_effects.screen = screen
    Globals.renderer = renderer
    Globals.settings = settings
    Globals.screen = screen

    # EFFECTS SECTION - experimental and fiddly. controls 1-9 for now.
    # make instances of classes in subeffects.py in effects. on keyboard, 1 corresponds to first, 2 to second etc.
    effects = [sub_effects.Spotlight(200), 
                sub_effects.Stars(400, 1, 4),
                sub_effects.SweepSprite("large_frozen_earth.png", (settings.get_center()), 1, 400, 2),  
                sub_effects.ArcSprite("large_frozen_earth.png", (screen.size[0]//2, 300), 0, 200, 0.5, 144),
                sub_effects.ArcSprite("large_frozen_earth.png", (screen.size[0]//2, 300), 0, 200, 0.5, 216),
                sub_effects.ArcSprite("large_frozen_earth.png", (screen.size[0]//2, 300), 0, 200, 0.5, 288),
                sub_effects.Sprite("large_frozen_earth.png", (0,0), 10, 1)]

    displays, pos = create_displays(settings)
    text = Text()
    text.index = 0
    text_show = False
    fade_time = 0 # this acts as both a boolean and counter.
    fade_duration = settings.fps // 5 # 1/x seconds.
    control_speed = 5
    control_index = 0

    while True:

        renderer.target = buffer 
        renderer.clear()

        # draw flickering panels
        for i, display in enumerate(displays):
            display.give_textures().draw(dstrect=pos[i])

        if settings.bg_on:
            settings.background.draw(dstrect=(0,0))

        # draw effects on top
        for ef in effects:
            ef.update()
            if ef.opacity > 0:
                ef.TEXTURE.draw(dstrect=ef.rect, angle=ef.theta)

        # draw text and boxes
        if text.text_alpha > 0:
            texts = text.give_textures()
            for a,b in zip(texts[2], texts[3]): # boxes
                a.alpha = text.box_alpha
                a.draw(dstrect=b.topleft)
            for c,d in zip(texts[0], texts[1]): # texts
                c.alpha = text.text_alpha
                c.draw(dstrect=d.topleft)

        # EVENT HANDLING SECTION
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                exit()

            elif e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    exit()

                elif e.key == pygame.K_a: # reload current text file. retain position.
                    text.read_messages()

                elif e.key == pygame.K_b: # enable background (transparent overlay)
                    settings.bg_on ^= True
                    if not settings.background:
                        settings.render_background()

                elif e.key == pygame.K_LEFT:
                    settings.next_background(-1)
                    settings.render_background()

                elif e.key == pygame.K_RIGHT:
                    settings.next_background(1)
                    settings.render_background()

                elif e.key == pygame.K_d: # switch directory.
                    load_next_directory(text, settings)
                    displays, pos = create_displays(settings)
                    text_show = False

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
                        effects[e.key-49].toggle()
                        if effects[e.key-49].opacity: # if is on.
                            control_index = e.key - 49
                    except Exception as e:
                        print("Not enough items in effects list (or ", e + ")")

                # cycle through controllable surfaces
                elif e.key in (pygame.K_PAGEDOWN, pygame.K_PAGEUP) and control_index is not None:

                    counter = 0 # we go through at most the whole list: possible that no control surface is enabled.
                    direction = -1 if e.key == pygame.K_PAGEDOWN else 1
                    control_index = (control_index + direction) % len(effects)

                    while not (hasattr(effects[control_index], "move") or hasattr(effects[control_index], "resize")) or not effects[control_index].opacity:
                        control_index = (control_index + direction) % len(effects)
                        counter += 1
                        if counter >= len(effects): break
                    print(f"current control key: {control_index + 1}") # which button to press to enable this one.
                    
                # show next text line / hide current one
                elif e.key in (pygame.K_z, pygame.K_x, pygame.K_c):
                    if not text_show:
                        text.text_alpha = 0
                        text.box_alpha = 0
                        text.next_message()
                    text_show ^= True
                    fade_time = 1 # access fades.

            # recomputing various screensize aspects after resize
            elif e.type == pygame.VIDEORESIZE:
                settings.x = ceil(screen.size[0] / settings.img_width)
                settings.y = ceil(screen.size[1] / settings.img_height)
                displays, pos = create_displays(settings)
                settings.resolution = screen.size
                buffer = pygame._sdl2.Texture(renderer, settings.resolution, target=True)
                text.update_font_size()

        # FADES FOR TEXT AND BOXES. (todo: build into classes.)
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
        direction = (0,0)
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_PLUS] or pressed[pygame.K_MINUS]:
            resize_factor += 0.01 if pressed[pygame.K_PLUS] else -0.01

        # MOVEMENT CONTROL SECTION
        if pressed[pygame.K_i] or pressed[pygame.K_j] or pressed[pygame.K_k] or pressed[pygame.K_l]:

            # first diagonal checks.
            if pressed[pygame.K_i] and pressed[pygame.K_j]:
                direction = (-control_speed,-control_speed)
            elif pressed[pygame.K_i] and pressed[pygame.K_l]:
                direction = (control_speed,-control_speed)
            elif pressed[pygame.K_l] and pressed[pygame.K_k]:
                direction = (control_speed,control_speed)
            elif pressed[pygame.K_k] and pressed[pygame.K_j]:
                direction = (-control_speed,control_speed)
            
            # then the axes.
            elif pressed[pygame.K_i]:
                direction = (0,-control_speed)
            elif pressed[pygame.K_l]:
                direction = (control_speed,0)
            elif pressed[pygame.K_k]:
                direction = (0,control_speed)
            elif pressed[pygame.K_j]:
                direction = (-control_speed,0)
    
        # resize selected control surface.
        for ef in effects:
            if hasattr(ef, "resize") and effects[control_index] == ef:
                ef.resize(resize_factor)
                break

        # move things
        for ef in effects:
            if hasattr(ef, "move") and effects[control_index] == ef:
                ef.move(direction)
                break

        renderer.target = None
        buffer.draw()
        renderer.present() 
        clock.tick(settings.fps)

if __name__ == "__main__":

    # STARTUP CONFIGURATION - directory choice and resolution.
    # you want to put all the image directories into ./pics, 'tmp' ignored, 'backgrounds' only used for 'b' to enable background.
    possible_directories = []
    hub_path = os.path.dirname(os.path.realpath(__file__)) + "/pics/"
    dir_names = os.listdir(hub_path)
    for i in dir_names:
        if os.path.isdir(hub_path + i) and i != "tmp" and i != "backgrounds":
            possible_directories.append(i)
    print("#" * 40)
    print("# Available directories:" + " "*15 + "#")
    for i, name in enumerate(possible_directories):
        print("# {:1}. {:33} #".format(i + 1, name))
    print("#" * 40)

    while "entering config":
        try:
            dirchoice = input("Directory\n> ")
            reschoice = input("Resolution\n> ") # width
            resolution = (int(reschoice)*16//9, int(reschoice))
            screen = pygame._sdl2.Window("...", size=resolution, resizable=True)
            if dirchoice.isnumeric():
                settings = Settings(possible_directories[int(dirchoice)-1], resolution)
                settings.current_index = int(dirchoice) - 1
            else:
                tmp_index = possible_directories.index(dirchoice)
                settings = Settings(possible_directories[tmp_index], resolution)
                settings.current_index = tmp_index
            settings.directory_list = possible_directories
            break

        except IndexError:
            print(f"The image directory is empty.")

        except Exception as e:
            print(f"Incorrect input: {e}.")

    print(f"Current resolution: {resolution}")

    main(settings, screen)