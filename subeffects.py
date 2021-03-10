import pygame._sdl2
import os
from random import randint
from math import cos, sin, pi

effects = os.path.dirname(os.path.realpath(__file__)) + "/effects/"

# blit image based on a *center* coordinate. controllable with ijkl.
# for now: if spinning, cannot resize. this is a design flaw.
class Sprite:

    def __init__(self, item, pos, fade_speed, spin_speed):
        self.img_ref = pygame.image.load(effects + item).convert_alpha() # reference image
        self.img = self.img_ref
        self.img_rect = self.img_ref.get_rect()
        self.w, self.h = self.img_ref.get_size()
        self.spin_speed = spin_speed
        self.pos = pos
        self.theta = 0
        self.opacity = 0
        self.fade_speed = -fade_speed # flips when calling toggle()

    def blit(self, screen): # TODO: allow spinning and scaling at the same time.
        if self.opacity == 0:
           return
        else:
            self.automate_movement() # inherited class defines this.
            if self.opacity < 255:
                self.opacity += self.fade_speed
                self.img = self.img_ref
                self.img.set_alpha(self.opacity)
            if (self.w,self.h) != self.img.get_size(): # reasonably expensive.
                self.img = pygame.transform.scale(self.img_ref, (self.w, self.h))
            if (self.spin_speed != 0): # rotate() is expensive.
                self.theta = (self.theta + self.spin_speed) % 360
                self.img = pygame.transform.rotate(self.img_ref, self.theta)
            self.img_rect = self.img.get_rect(center = self.pos)
            screen.blit(self.img, self.img_rect.topleft)

    def move(self, diff):
        self.pos = (self.pos[0] + diff[0], self.pos[1] + diff[1])

    def resize(self, order):
        if order < 0 and (self.h <= 3 or self.w <= 3): # don't crash by shrinking negative.
            return
        self.w += order * self.w // self.h # maintain aspect ratio
        self.h += order

    def automate_movement(self): # for inheritance.
        pass

    def toggle(self, screen):
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

class SweepSprite(Sprite): # back and forth.
    def __init__(self, item, center, rate, width, spin_speed):
        super().__init__(item, center, 10, spin_speed)
        self.width = width
        self.center = center
        self.rate = rate
        self.sway_pos = 0

    def automate_movement(self):
        self.sway_pos = (self.sway_pos + self.rate) % 360
        self.pos = ((self.width // 2) * sin(self.sway_pos * pi / 180), self.pos[1])

# much faster to draw.
class SimpleSprite:

    def __init__(self, item, pos, orientation):
        self.img = pygame.image.load(effects + item).convert()
        if orientation != 0: # initial orientation
            self.img = pygame.transform.rotate(self.img, orientation)
        self.opacity = 0
        self.pos = pos

    def blit(self, screen):
        if self.opacity == 1:
            img_rect = self.img.get_rect(center = self.pos)
            screen.blit(self.img, img_rect.topleft)

    def move(self, diff):
        self.pos = (self.pos[0] + diff[0], self.pos[1] + diff[1])

    def toggle(self, screen):
        self.opacity = 1 if self.opacity == 0 else 0
        print(f"SimpleSprite is {self.fade_speed > 0}")

# draw random-sized small squares at random positions.
class Stars:

    def __init__(self, screen, n, minsize, maxsize):
        self.opacity = 0
        self.fade_speed = -3
        self.minsize = minsize
        self.maxsize = maxsize
        self.n = n
        self.dimensions = screen.get_size()
        self.surf = pygame.Surface(self.dimensions).convert_alpha()
        self.surf.set_colorkey((0,0,0))
        self.create_stars(screen)

    def create_stars(self, screen):
        self.stars = []
        for i in range(self.n):
            size = randint(self.minsize,self.maxsize)
            self.stars.append({"position": (randint(0,self.dimensions[0]), randint(0,self.dimensions[1])), "size": size})

    def blit(self, screen):
        if self.opacity > 0:
            if self.opacity < 255:
                self.opacity += self.fade_speed
                self.surf.set_alpha(self.opacity)
                for star in self.stars:
                    pygame.draw.circle(self.surf, (255,255,255), star["position"], star["size"])
            screen.blit(self.surf, (0,0))
                
    def toggle(self, screen):
        if self.opacity == 0 and self.surf.get_size() != screen.get_size():
            self.dimensions = screen.get_size()
            self.surf = pygame.Surface(self.dimensions).convert_alpha()
            self.surf.set_colorkey((0,0,0))
            self.create_stars(screen)
        self.fade_speed *= -1
        self.opacity += self.fade_speed
        print(f"Stars is {self.fade_speed > 0}")

class Spotlight:
    def __init__(self, radius, resolution):
        self.cover = pygame.Surface(resolution)
        self.cover.fill(0)
        self.cover.set_colorkey((255,255,255))
        self.pos = (0,0)
        self.radius = radius
        self.opacity = 0

    def blit(self, screen):
        if self.opacity > 0:
            self.cover.fill(0)
            self.pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.cover, (255,255,255), self.pos, self.radius)
            screen.blit(self.cover, (0,0))

    def resize(self, order):
        self.radius += order

    def toggle(self, screen):
        self.opacity = 1 if self.opacity == 0 else 0
        print(f"Spotlight is {self.opacity > 0}")