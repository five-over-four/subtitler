import pygame._sdl2
import os
from random import randint
from math import cos, sin, pi

effects = os.path.dirname(os.path.realpath(__file__)) + "/effects/"

# set these from the main file in subtitler.main().
renderer = None
settings = None
screen = None

class Sprite:

    def __init__(self, item, pos, fade_speed, spin_speed=0):
        self.img_ref = pygame.image.load(effects + item) # reference image
        self.size = self.img_ref.get_size()
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.img_ref)
        self.spin_speed = spin_speed
        self.pos = pos
        self.scale = 1.0 # this maintains aspect ratio by *not* directly manipulating size.
        self.w, self.h = self.img_ref.get_size()
        self.rect = self.img_ref.get_rect(center=self.pos)
        self.theta = 0
        self.opacity = 0
        self.fade_speed = -fade_speed # flips when calling toggle()

    def update(self):
        if self.opacity == 0:
           return
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
        self.pos = self.pos[0] + diff[0], self.pos[1] + diff[1]
        self.rect.center = self.pos

    def resize(self, order):
        if order < 0 and self.scale <= 0.01: # don't crash by shrinking negative.
            return
        elif order == 0:
            return
        self.scale += order
        self.size = (round(self.w * self.scale), round(self.h * self.scale))
        img = pygame.transform.scale(self.img_ref, self.size)
        self.rect = img.get_rect(center=self.pos)
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, img)

    def automate_movement(self): # for inheritance.
        pass

    def toggle(self):
        self.fade_speed *= -1
        self.opacity += self.fade_speed # certain values may overshoot 255
        print(f"{self.__class__.__name__} is {self.fade_speed > 0}")

# animates a sprite on a circular path while spinning.
class ArcSprite(Sprite):

    def __init__(self, item, origin, spin_speed, radius, speed, start_angle):
        super().__init__(item, origin, 10, spin_speed)
        self.origin = origin
        self.radius = radius
        self.speed = speed
        self.phi = start_angle

    def arc_pos(self):
        x = self.radius * cos(self.phi * pi / 180) + self.origin[0]
        y = self.radius * sin(self.phi * pi / 180) + self.origin[1]
        return (x,y)

    def automate_movement(self):
        self.phi = (self.phi + self.speed) % 360
        self.pos = self.arc_pos()
        self.rect.center = self.pos

class SweepSprite(Sprite): # back and forth.
    def __init__(self, item, origin, rate, radius, spin_speed):
        super().__init__(item, origin, 10, spin_speed)
        self.origin = origin
        self.radius = radius
        self.rate = rate
        self.phi = 0

    def sway_pos(self):
        x = self.radius * sin(self.phi * pi / 180) + self.origin[0]
        y = self.origin[1]
        return (x,y)

    def automate_movement(self):
        self.phi = (self.phi + self.rate) % 360
        self.pos = self.sway_pos()

# draw random-sized small circles at random positions.
class Stars:

    def __init__(self, n, minsize, maxsize):
        self.rect = (0,0)
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
            pygame.draw.circle(self.surf, (255,255,255), star["position"], star["size"])
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.surf)

    def update(self):
        if self.opacity == 0:
            return
        self.opacity += self.fade_speed
        if self.opacity > 255:
            self.opacity = 255
        elif self.opacity < 0:
            self.opacity = 0
        self.TEXTURE.alpha = self.opacity
        return {"dstrect": self.rect}

    def toggle(self):
        if self.opacity == 0 and self.surf.get_size() != screen.size:
            self.dimensions = screen.size
            self.create_stars()
        self.fade_speed *= -1
        self.opacity += self.fade_speed
        print(f"Stars is {self.fade_speed > 0}")

class Spotlight: # kinda hacky and renders a new texture every frame.

    def __init__(self, radius):
        self.cover = pygame.Surface(settings.resolution)
        self.cover.fill(0)
        self.rect = (0,0)
        self.cover.set_colorkey((255,255,255))
        self.pos = (0,0)
        self.radius = radius
        pygame.draw.circle(self.cover, (255,255,255), self.pos, self.radius)
        self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.cover)
        self.opacity = 0

    def update(self):
        if self.opacity > 0:
            self.cover.fill(0)
            self.pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.cover, (255,255,255), self.pos, self.radius)
            self.TEXTURE = pygame._sdl2.Texture.from_surface(renderer, self.cover)
            return {"dstrect": self.rect}

    def resize(self, order):
        self.radius *= 1 + order / 2

    def toggle(self):
        self.opacity = 255 if self.opacity == 0 else 0
        print(f"Spotlight is {self.opacity > 0}")