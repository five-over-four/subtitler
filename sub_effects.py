import pygame._sdl2
import os
from random import randint
from math import cos, sin, pi

effects = os.path.dirname(os.path.realpath(__file__)) + "/effects/"

# set these from the main file in subtitler.main().
renderer = None
settings = None
screen = None

# movable and resizable image that can rotate.
class Sprite:

    def __init__(self, item, pos=(0,0), initial_scale=1, fade_speed=10, spin_speed=0, control_speed=4):
        self.img_ref = pygame.image.load(effects + item) # reference image
        self.original_size = self.img_ref.get_size() # reference size for scaling.
        self.w, self.h = self.original_size[0]*initial_scale, self.original_size[1]*initial_scale
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.img_ref)
        self.spin_speed = spin_speed
        self.control_speed = control_speed
        self.pos = pos
        self.rect = pygame.Rect(*self.pos, self.w, self.h)
        self.theta = 0
        self.opacity = 0
        self.fade_speed = -fade_speed # flips when calling toggle()

    def update(self):
        self.automate_movement() # inherited class defines this.
        self.opacity += self.fade_speed 
        if self.opacity > 255:
            self.opacity = 255
        elif self.opacity < 0:
            self.opacity = 0
        if self.spin_speed:
            self.theta = (self.theta + self.spin_speed) % 360
        self.TEXTURE.alpha = self.opacity
        return {"dstrect": self.rect, "angle": self.theta}

    def move(self, diff):
        self.pos = self.pos[0] + diff[0]*self.control_speed, self.pos[1] + diff[1]*self.control_speed
        self.rect.center = self.pos

    def resize(self, order):
        if order == 0 or (order < 0 and self.w <= 1): # don't resize too small.
            return
        self.w = self.w + order * 3 * self.w / self.original_size[0] * self.w/self.h # aspect ratio.
        self.h = self.h + order * 3 * self.h / self.original_size[1]
        self.rect = pygame.Rect(*self.pos, self.w, self.h)
        self.rect.center = self.pos

    def automate_movement(self): # for inheritance.
        pass

    def toggle(self):
        self.fade_speed *= -1
        self.opacity += self.fade_speed
        print(f"{self.__class__.__name__} is {self.fade_speed > 0}")

# animates a sprite on a circular path while spinning.
class ArcSprite(Sprite):

    def __init__(self, item, origin=(0,0), axes=(300,300), speed=0.5, start_angle=0, spin_speed=0):
        super().__init__(item, origin, 10, spin_speed)
        self.origin = origin
        self.axes = axes
        self.speed = speed
        self.phi = start_angle

    def arc_pos(self):
        x = self.axes[0] * cos(self.phi * pi / 180) + self.origin[0]
        y = self.axes[1] * sin(self.phi * pi / 180) + self.origin[1]
        return (x,y)

    def automate_movement(self):
        self.phi = (self.phi + self.speed) % 360
        self.pos = self.arc_pos()
        self.rect.center = self.pos

class SweepSprite(Sprite): # back and forth.
    def __init__(self, item, origin=(0,0), rate=0.5, width=300, spin_speed=0):
        super().__init__(item, origin, 10, spin_speed)
        self.origin = origin
        self.width = width
        self.rate = rate
        self.phi = 0

    def sway_pos(self):
        x = self.width * sin(self.phi * pi / 180) + self.origin[0]
        y = self.origin[1]
        return (x,y)

    def automate_movement(self):
        self.phi = (self.phi + self.rate) % 360
        self.pos = self.sway_pos()

# draw n minsize-maxsize small circles at random positions.
# toggle to redraw if resizing window.
class Stars:

    def __init__(self, n=400, minsize=1, maxsize=4):
        self.opacity = 0
        self.fade_speed = -3
        self.minsize = minsize
        self.maxsize = maxsize
        self.n = n
        self.dimensions = screen.size
        self.surf = pygame.Surface(self.dimensions)
        self.create_stars()

    def create_stars(self):
        self.surf.fill(0)
        self.surf.set_colorkey((0,0,0))
        self.stars = []
        for i in range(self.n):
            size = randint(self.minsize,self.maxsize)
            self.stars.append({"position": (randint(0,self.dimensions[0]), randint(0,self.dimensions[1])), "size": size})
        for star in self.stars:
            pygame.draw.circle(self.surf, (255,)*3, star["position"], star["size"])
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.surf)

    def update(self):
        self.opacity += self.fade_speed
        if self.opacity > 255:
            self.opacity = 255
        elif self.opacity < 0:
            self.opacity = 0
        self.TEXTURE.alpha = self.opacity
        return {"dstrect": (0,0)}

    def toggle(self):
        if self.opacity == 0 and self.surf.get_size() != screen.size:
            self.dimensions = screen.size
            self.surf = pygame.Surface(self.dimensions)
            self.create_stars()
        self.fade_speed *= -1
        self.opacity += self.fade_speed
        print(f"Stars is {self.fade_speed > 0}")

class Spotlight:
    def __init__(self, light_texture, resolution=(1920,1080)):
        self.cover = pygame.Surface(resolution)
        self.light = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/spotlights/" + light_texture)
        self.cover.set_colorkey((1,2,3)) # needed for alpha.
        self.COVER_TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.cover)
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.light)
        self.TEXTURE.blend_mode = 4
        self.original_size = self.light.get_size() # we use this to control the 1/r scaling.
        self.w, self.h = self.light.get_size()
        self.x, self.y = 0, 0
        self.opacity = 0
        self.fade_speed = -3

    def draw(self):
        if self.opacity == 0:
            return
        self.set_alpha()
        self.make_rects()
        for rect in self.surround_rects:
            self.COVER_TEXTURE.draw(dstrect=rect)
        if self.opacity >= 255:
            self.TEXTURE.draw(dstrect=self.main_rect)

    def set_alpha(self):
        self.opacity += self.fade_speed
        if self.opacity > 255:
            self.opacity = 255
        elif self.opacity < 0:
            self.opacity = 0
        self.COVER_TEXTURE.alpha = self.opacity
        self.TEXTURE.alpha = self.opacity

    def make_rects(self): # draw spotlight and black AROUND it to circumvent poor additive blending.
        x, y = pygame.mouse.get_pos()
        self.x = x - self.w//2
        self.y = y - self.h//2
        self.main_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.surround_rects = [pygame.Rect(0, 0, settings.resolution[0], self.y),
                               pygame.Rect(0, self.h + self.y, settings.resolution[0], settings.resolution[0] - self.y - self.h),
                               pygame.Rect(0, self.y, self.x, self.h),
                               pygame.Rect(self.x + self.w, self.y, settings.resolution[0] - self.x - self.w, self.h)]
        if self.opacity < 255: # blend_mode 4 forbids alpha, so we hide the image until the background is fully opaque.
            self.surround_rects.append(pygame.Rect(self.x, self.y, self.w, self.h))

    def resize(self, order):
        if self.w >= 1 and self.h >= 1:
            self.w = self.w + order * 3 * (self.w / self.original_size[0])
            self.h = self.w + order * 3 * (self.h / self.original_size[1])

    def toggle(self):
        self.fade_speed *= -1
        self.opacity += self.fade_speed
        print(f"Spot is {self.fade_speed > 0}")

# 4 (or 8) directions. like in a video game.
# order in directory: E, S, W, N, NE, SE, SW, NW.
class SpriteSheet:
    def __init__(self, speed = 3):
        path = os.path.dirname(os.path.realpath(__file__)) + "/directional_sprites"
        images = os.listdir(path)
        self.images = [pygame.image.load(path + "/" + image) for image in images]
        self.pos = settings.center
        self.rect = self.images[0].get_rect(center=self.pos)
        self.directions = [(1,0), (0,1), (-1,0), (0,-1), (1,-1), (1,1), (-1,1), (-1,-1)]
        self.TEXTURES = {key: pygame._sdl2.Texture.from_surface(renderer, image) for key, image in zip(self.directions, self.images)}
        self.TEXTURE = self.TEXTURES[(1,0)] # start right.
        self.speed = speed
        self.opacity = 0

    def update(self):
        return {"dstrect": self.rect}

    def move(self, diff):
        if diff != [0,0]:
            if len(self.TEXTURES) == 4 and abs(diff[0]) + abs(diff[1]) <= 1:
                self.pos = self.pos[0] + diff[0]*self.speed, self.pos[1] + diff[1]*self.speed
                self.TEXTURE = self.TEXTURES[tuple(diff)]
            elif len(self.TEXTURES) == 8:
                self.pos = self.pos[0] + diff[0]*self.speed, self.pos[1] + diff[1]*self.speed
                self.TEXTURE = self.TEXTURES[tuple(diff)]
            self.rect.center = self.pos

    def toggle(self):
        self.opacity = 1 if self.opacity == 0 else 0
        print(f"SpriteSheet is {self.opacity > 0}")

# like Sprite, but takes a directory in ./animations and draws them one by one,
# switching image each frametime frames. coding-wise, a mix of Sprite and SpriteSheet.
class Animation:
    def __init__(self, dirname, frametime=10, pos=(0,0), control_speed=3):
        path = os.path.dirname(os.path.realpath(__file__)) + "/animations/" + dirname
        images = [pygame.image.load(path + "/" + image) for image in os.listdir(path)]
        self.original_size = images[0].get_size()
        self.w, self.h = self.original_size
        self.TEXTURES = [pygame._sdl2.Texture.from_surface(renderer, image) for image in images]
        self.TEXTURE = self.TEXTURES[0]
        self.pos = pos
        self.rect = images[0].get_rect(center=self.pos)
        self.control_speed = control_speed
        self.frametime = frametime # per image.
        self.timer = 0 # takes care of flipping through the images.
        self.opacity = 0

    def update(self):
        if self.opacity == 0:
            return
        self.timer = (self.timer + 1) % (self.frametime * len(self.TEXTURES))
        self.TEXTURE = self.TEXTURES[self.timer // self.frametime]
        return {"dstrect": self.rect}
        
    def move(self, diff):
        self.pos = self.pos[0] + diff[0]*self.control_speed, self.pos[1] + diff[1]*self.control_speed
        self.rect.center = self.pos

    def resize(self, order):
        if order == 0 or (order < 0 and self.w <= 1): # don't resize too small.
            return
        self.w = self.w + order * 3 * self.w / self.original_size[0] * self.w/self.h # aspect ratio.
        self.h = self.h + order * 3 * self.h / self.original_size[1]
        self.rect = pygame.Rect(*self.pos, self.w, self.h)
        self.rect.center = self.pos

    def toggle(self):
        self.opacity = 1 if self.opacity == 0 else 0
        print(f"Animation is {self.opacity > 0}")