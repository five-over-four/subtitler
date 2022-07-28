import math

# These classes are used to move individual effects list instances around automatically.
# 'R' resets effect positions as well as mover parameters.
# Rememeber to include a reset() method in each class.

class Mover1: # sinusoidal vertical bob and weave.
    def __init__(self, anim):
        self.anim = anim
        self.ref_pos = anim.pos # need a starting position.
        self.angle = 0
        self.speed = 0.0002 # how many radians per frame
        self.scale = 200 # amount moved at max

    def move(self):
        self.angle += self.speed
        self.anim.pos = (self.ref_pos[0] + math.sin(math.pi*self.angle)*self.scale, self.ref_pos[1])
        self.anim.theta = round(15*math.sin(20*self.angle))

    def reset(self):
        self.angle = 0