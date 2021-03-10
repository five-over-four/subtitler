import pygame
import pygame._sdl2
import os
from random import randint, choice
from PIL import Image
from itertools import product
from math import ceil
import subeffects

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
        self.fps = 60 # set to whatever. most settings are independent of it.
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
                self.background = pygame.image.load(self.hub_path + "backgrounds/" + self.backgrounds[0]).convert_alpha()
            else:
                self.bg_index = (self.bg_index + direction) % len(self.backgrounds)
                self.background = pygame.image.load(self.hub_path + "backgrounds/" + self.backgrounds[self.bg_index]).convert_alpha()

pygame.init()
pygame.display.set_caption("...") # set custom caption here if you like.
clock = pygame.time.Clock()

class DisplayFrame:

    images = []

    def __init__(self, settings, screen):
        self.index = randint(0,len(settings.images)-1)
        if not DisplayFrame.images: # first instance loads imageset.
            DisplayFrame.load_new_imageset()

    def blit(self, pos): # load image and draw.
        if randint(0,settings.rng_factor) == 0: # 10 -> 1 flip/sec, 100 -> 0.01 flips/sec.
            self.index = randint(0,len(settings.images) - 1)
        screen.blit(self.images[self.index], pos)

    @classmethod
    def load_new_imageset(self):
        DisplayFrame.images = [pygame.image.load(settings.path + "/" + settings.images[i]).convert() for i in range(0, len(settings.images))]

class Text:

    def __init__(self, settings, screen):
        self.update_font_size()
        self.read_messages() # list of all lines in directory.txt.
        self.index = 0 # current line number in directory.txt.
        self.next_message()
        self.text_surfs = []
        self.box_surfs = []
        self.text_rects = []
        self.box_rects = []
        self.alpha = 0
        self.max_alpha = 255
        self.speaker_height = 120

    def update_font_size(self): # linear function: font_size is 40 at width 1500, 60 at 2000.
        self.font_size = (screen.get_width() - 500) // 25

    def load_surfaces(self): # this is a bit unwieldy.
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
            text_box.fill((0,0,0))
            speaker_box = pygame.Surface((speaker_surf.get_rect().width + 20, speaker_surf.get_rect().height + 20))
            speaker_box.fill((0,0,0))
            self.text_surfs = [text_surf, speaker_surf]
            self.box_surfs = [text_box, speaker_box]
            height = self.box_surfs[1].get_height()*1.3
            self.text_rects = [text_surf.get_rect(center=(x,y)), speaker_surf.get_rect(center=(x,y-self.speaker_height))]
            self.box_rects = [text_box.get_rect(center=(x,y)), speaker_box.get_rect(center=(x,y-self.speaker_height))]
        else: # regular line without speaker.
            self.set_subtitle_size(self.message[0])
            text_surf = self.font.render(self.message[0], True, (255,255,255))
            text_box = pygame.Surface((text_surf.get_rect().width + 20, text_surf.get_rect().height + 20))
            text_box.fill((0,0,0))
            self.text_surfs = [text_surf]
            self.box_surfs = [text_box]
            self.text_rects = [text_surf.get_rect(center=(x,y))]
            self.box_rects = [text_box.get_rect(center=(x,y))]

    def display(self):
        if not self.message or self.alpha == 0:
            return
        self.set_alpha()
        screen.blit(self.box_surfs[0], self.box_rects[0].topleft)
        screen.blit(self.text_surfs[0], self.text_rects[0].topleft)
        if len(self.text_surfs) > 1:
            screen.blit(self.box_surfs[1], self.box_rects[1].topleft)
            screen.blit(self.text_surfs[1], self.text_rects[1].topleft)

    def set_alpha(self): # cheaper blitting when max alpha.
        if self.alpha < self.max_alpha:
            for surf in self.text_surfs + self.box_surfs:
                surf.set_alpha(self.alpha)
                surf.convert_alpha()
        else:
            for surf in self.text_surfs + self.box_surfs:
                surf.convert() # TODO fix converting every frame.

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

def load_next_directory(text, settings, screen): # modifies relevant objects.

    # first load the new files into Settings(), skipping empty directories.
    while True:
        settings.current_index = (settings.current_index + 1) % len(settings.directory_list)
        try:
            settings.image_set = settings.directory_list[settings.current_index]
            settings.images = os.listdir(settings.hub_path + settings.image_set)
            settings.path = settings.hub_path + settings.image_set
            settings.img_width, settings.img_height = Image.open(settings.path + "/" + settings.images[0]).size
            settings.x = ceil(screen.get_width() / settings.img_width) 
            settings.y = ceil(screen.get_height() / settings.img_height)
            break
        except:
            continue

    # then make the changes to Text()
    text.read_messages()
    text.index = 0
    text.alpha = 0
    
def create_displays(settings, screen): # tiling via x-tile * y-tile DisplayFrame objects.
    displays = [DisplayFrame(settings, screen) for x in range(settings.x * settings.y)]
    DisplayFrame.load_new_imageset()
    offset = product([x for x in range(settings.x)], [x for x in range(settings.y)])
    pos = [(0 + off[0] * settings.img_width, 0 + off[1] * settings.img_height) for off in offset]
    return displays, pos

def main(settings, screen, effects): # todo: redesign blitting, fades, sdl2 functionality.

    displays, pos = create_displays(settings, screen)
    text = Text(settings, screen)
    text.index = 0
    text_show = False
    fade_time = 0 # this acts as both a boolean and counter.
    fade_duration = settings.fps // 5 # 1/x seconds.

    # for movable effects, like Sprite(). control_index tells which effect is moved.
    control_speed = 5
    control_index = None
    for i, effect in enumerate(effects):
        if hasattr(effect, "move"):
            control_index = i
            break

    while True:

        # draw flickering panels
        for i, display in enumerate(displays):
            display.blit(pos[i])

        if settings.bg_on: # expensive for large transparent backgrounds.
            screen.blit(settings.background, (0,0))

        # draw special effects on top
        for effect in effects:
            effect.blit(screen)

        text.display()

        # EVENT HANDLING SECTION
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                screen = pygame.display.set_mode(settings.resolution)
                exit()

            elif e.type == pygame.KEYDOWN:

                if e.key == pygame.K_ESCAPE:
                    screen = pygame.display.set_mode(settings.resolution) # exit fullscreen before quitting.
                    exit()

                elif e.key == pygame.K_a: # reload current text file. retain position.
                    text.read_messages()

                elif e.key == pygame.K_b: # enable background (transparent overlay)
                    settings.bg_on ^= True

                elif e.key == pygame.K_LEFT:
                    settings.next_background(-1)

                elif e.key == pygame.K_RIGHT:
                    settings.next_background(1)

                elif e.key == pygame.K_d: # switch directory.
                    load_next_directory(text, settings, screen)
                    displays, pos = create_displays(settings, screen)
                    text_show = False

                elif e.key == pygame.K_RETURN: # reset to the first line.
                    text.index = 0
                    if not text_show:
                        text.alpha = 0
                        text.next_message()
                    text_show ^= True
                    fade_time = 1 # access fades
                
                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

                # effect toggling. 1 to 9. 1 corresponds to 49.
                elif e.key in {x+49 for x in range(0,10)} and effects:
                    try:
                        effects[e.key-49].toggle(screen)
                        if effects[e.key-49].opacity: # if is on.
                            control_index = e.key - 49
                    except:
                        print("Not enough items in effects list.")

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
                    
                # next text line
                elif e.key in (pygame.K_z, pygame.K_x, pygame.K_c):
                    if not text_show:
                        text.alpha = 0
                        text.next_message()
                    text_show ^= True
                    fade_time = 1 # access fades.

            # recomputing various screensize aspects after resize
            elif e.type == pygame.VIDEORESIZE:
                settings.x = ceil(screen.get_width() / settings.img_width)
                settings.y = ceil(screen.get_height() / settings.img_height)
                displays, pos = create_displays(settings, screen)
                settings.resolution = screen.get_size()
                text.update_font_size()

        # FADES FOR TEXT AND BOXES. (todo: build into classes.)
        if fade_time > 0 and text_show: # fade in
            fade_time += 1
            text.alpha += text.max_alpha // fade_duration # adjust the 255 if you want a different *max* opacity.
        elif fade_time > 0 and not text_show: # fade out
            fade_time += 1
            text.alpha -= text.max_alpha // fade_duration

        if fade_time > fade_duration: # fade has finished.
            fade_time = 0

        # RESIZING CONTROL SECTION
        resize_factor = 0
        direction = (0,0)
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_PLUS] or pressed[pygame.K_MINUS]:
            resize_factor += 3 if pressed[pygame.K_PLUS] else -3

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
    
        # resize things that are resizable.
        for effect in effects:
            if hasattr(effect, "resize") and effects[control_index] == effect:
                effect.resize(resize_factor)
                break

        # move things
        for effect in effects:
            if hasattr(effect, "move") and effects[control_index] == effect:
                effect.move(direction)
                break

        pygame.display.flip()
        clock.tick(settings.fps)

if __name__ == "__main__":

    # uncomment this line if you want the window to appear with the drag bar available. (can still move with win + arrows).
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,32" # this ensures the window's dragging bar is not off-screen.

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
            screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
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

    # EFFECTS SECTION - experimental and fiddly. controls 1-9 for now.
    # make instances of classes in subeffects.py in effects. on keyboard, 1 corresponds to first, 2 to second etc.
    effects = [subeffects.Stars(screen, 400, 1, 4), \
                subeffects.ArcSprite("large_frozen_earth.png", (screen.get_width()//2, 300), 1, 400, 1, 2.5),
                subeffects.SweepSprite("large_frozen_earth.png", (settings.get_center()), 1, 400, 2),  
                subeffects.ArcSprite("large_frozen_earth.png", (screen.get_width()//2, 300), 0, 200, 0.5, 144),
                subeffects.ArcSprite("large_frozen_earth.png", (screen.get_width()//2, 300), 0, 200, 0.5, 216),
                subeffects.ArcSprite("large_frozen_earth.png", (screen.get_width()//2, 300), 0, 200, 0.5, 288),
                subeffects.Sprite("large_frozen_earth.png", (0,0), 10, 1), #7
                subeffects.SimpleSprite("moon_oil.png", (0,0), 45),
                subeffects.Spotlight(200, settings.resolution)]

    main(settings, screen, effects)