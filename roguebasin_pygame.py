
#lukasr2026@student.vis.ac.at
"""
Idea: create a roguelike game in python3 inspired by dungeon crawl,
capable of different graphic engines (at the moment: pygame)
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: https://github.com/horstjens/roguebasin_python3

based on: http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_4

field of view and exploration
see http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds

field of view improving, removing of artifacts:
see https://sites.google.com/site/jicenospam/visibilitydetermination

graphics mostly from Dungeon Crawl: http://crawl.develz.org/
"""

import pygame
import random
# import inspect

import os

# declare constants
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


# TODO: poblem bei DragonFire: wenn die duration zu klein ist sieht man oft gar keine Explosion
# TODO: warum blinkt panelscreeen --> background blit schuld?
# TODO: different dungeon create methods, see test/DungeonCreator
# TODO: different graphic engines: pysimplegui/text/arcade/ .. godot?
# TODO: monster (sprites?) move a bit toward victim on melee attack / move animation between tiles
# TODO: monster (and floors?) as sprites, for animation loops (flapping wings, glowing torches etc)
# TODO: monster speed > 1 tile possible ?
# TODO: rework NaturalWeapon
# TODO: Item
# TODO: Equipment
# TODO: Consumable
# TODO: blood after impact on floor (feat.png, 58,384,22,32.....
# TODO: highlight mouse-path for shooting, / Fireball


class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {}  # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups)  # call parent class. NEVER FORGET !
        self.number = VectorSprite.number  # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self.create_image()
        self.distance_traveled = 0  # in pixel
        self.rect.center = (-300, -300)  # avoid blinking image in topleft corner
        if self.angle != 0:
            self.set_angle(self.angle)
        # self.visible = False # will be changed to True when age becomes positive

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        # if "static" not in kwargs:
        #    self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(x=150, y=150)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(x=0, y=0)
        # if "acceleration" not in kwargs:
        #    self.acc = 0.0 # pixel/second speed is constant
        # TODO: acc, gravity-vector
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:
            # self.color = None
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # if "hitpoints" not in kwargs:
        #    self.hitpoints = 100
        # self.hitpointsfull = self.hitpoints # makes a copy
        # if "mass" not in kwargs:
        #    self.mass = 10
        # if "damage" not in kwargs:
        #    self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0  # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0  # age in seconds
        if "visible" not in kwargs:
            self.visible = False  # becomes True when self.age becomes >= 0

    def kill(self):
        if self.number in self.numbers:
            del VectorSprite.numbers[self.number]  # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((self.color))
        # self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # position and move are pygame.math.Vector2 objects
        # ----- kill because... ------
        # if self.hitpoints <= 0:
        #    self.kill()
        # TODO: pygame.DirtySprite verwenden, mit dirty und visible flag
        if self.age < 0:
            self.visible = False
        else:
            self.visible = True
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                # self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(x=boss.pos.x, y=boss.pos.y)
        if self.age > 0:
            self.pos += self.move * seconds
            self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        if not self.visible:
            self.rect.center = (-200, -200)
        else:
            self.wallbounce()
            self.rect.center = (round(self.pos.x, 0), round(self.pos.y, 0))

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width
        # -------- upper edge -----
        if self.pos.y < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = Viewer.height
        # -------- right edge -----
        if self.pos.x > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.pos.y > Viewer.height:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = Viewer.height
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0


class HealingSprite(VectorSprite):
    image = None

    # TODO: move upwards in sinus-curve instead of in straight line
    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.picture = self.image
        self.create_image()

class Animation(VectorSprite):
    """expects a zoomdelta parameter """
    image = None
    images = None

    def update(self, seconds):
        super().update(seconds)
        oldcenter = self.rect.center
        self.zoom += self.zoom_delta * seconds
        self.rotation += 0
        # self.image = pygame.transform.rotozoom(self.image0, self.rotation, self.zoom)
        # self.image.convert_alpha()

        # next animation picture?
        i = int(self.age / self.animation_delta)
        i = min(i, len(self.images) - 1)
        if i > self.i:
            self.i = i
            self.picture = self.images[i]
            self.create_image()
            self.image0 = self.image.copy()
        self.image = pygame.transform.rotozoom(self.image0, self.rotation, self.zoom)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter


class FireBallAnimation(Animation):


    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.i = 0
        self.max_age = 1.6
        self.animation_delta = self.max_age / len(self.images)
        self.picture = self.images[0]
        self.create_image()
        self.zoom = 1.0
        self.rotation = 0
        self.pos += pygame.math.Vector2(Viewer.grid_size[0] // 2, Viewer.grid_size[1] // 2)
        self.image0 = self.image.copy()



class FlameAnimation(Animation):

    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.i = 0
        self.max_age = 1.6
        self.animation_delta = self.max_age / len(self.images)
        self.picture = self.images[0]
        self.create_image()
        self.zoom = 1.0
        self.rotation = 0
        self.pos += pygame.math.Vector2(Viewer.grid_size[0] // 2, Viewer.grid_size[1] // 2)
        self.image0 = self.image.copy()


class BleedingSprite(VectorSprite):
    """a skull symbol, incrasing in size and dissappearing"""
    image = None

    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.picture = self.image
        self.create_image()
        self.zoom = 1.0

        self.rotation = 0
        self.pos += pygame.math.Vector2(Viewer.grid_size[0] // 2, Viewer.grid_size[1] // 2)
        self.image0 = self.image.copy()

    def update(self, seconds):
        super().update(seconds)
        oldcenter = self.rect.center
        self.zoom += self.zoom_delta
        self.rotation += 0
        self.image = pygame.transform.rotozoom(self.image0, self.rotation, self.zoom)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter


class BlinkSprite(BleedingSprite):
    image = None


class FragmentSprite(VectorSprite):

    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.alpha = 255
        self.delta_alpha = 255 / self.max_age if self.max_age > 0 else 1

    def update(self, seconds):
        super().update(seconds)
        # 0 = full transparency, 255 = no transparency at all
        self.alpha -= self.delta_alpha * seconds * 0.4  # slowly become more transparent
        self.image.set_alpha(self.alpha)
        self.image.convert_alpha()


class Flytext(VectorSprite):
    def __init__(self, text, fontsize=22, acceleration_factor=1.02, max_speed=300, **kwargs):
        """a text flying upward and for a short time and disappearing"""

        VectorSprite.__init__(self, **kwargs)
        ##self._layer = 7  # order of sprite layers (before / behind other sprites)
        ##pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.acceleartion_factor = acceleration_factor
        self.max_speed = max_speed
        self.kill_on_edge = True
        self.image = make_text(self.text, self.color, fontsize)[0]  # font 22
        self.rect = self.image.get_rect()

    def update(self, seconds):
        self.move *= self.acceleartion_factor
        if self.move.length() > self.max_speed:
            self.move.normalize_ip()
            self.move *= self.max_speed
        VectorSprite.update(self, seconds)


class GoldSprite(VectorSprite):
    """praticle that fly in a complicated path from the gold -pickup area to the side-panel"""

    image = None  # will be set from Viewer.create_tiles
    blackhole = pygame.math.Vector2(0, 0)  # Vector2  :  will be set from Viewer.init
    speed = 10
    krit = 5
    blackholemass = 10 ** 7
    speedlimit = 300

    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.picture = self.image
        self.undisturbed = 0 + random.random() * 0.5  # time without black hole pull
        self.create_image()
        self.move = pygame.math.Vector2(random.randint(50, 200), 0)
        self.move.rotate_ip(random.randint(0, 360))
        # self.max_age = 10
        # self.friction = 0.99
        # print("black hole:", self.blackhole)

    def update(self, seconds):
        super().update(seconds)
        # self.move *= self.friction
        if self.age < self.undisturbed:
            return
        distance = self.blackhole - self.pos
        acc = self.blackholemass / distance.length() ** 1.8  # 2

        if distance.length() < self.krit:
            Game.player.gold += 1  # delay, gold is added only after gold-fly animation
            self.kill()
        distance.normalize_ip()
        acc *= distance
        self.move += acc * seconds  # pygame.math.Vector2(0,5)#distance
        if self.move.length() > self.speedlimit:
            self.move.normalize_ip()
            self.move *= self.speedlimit


class FlyingObject(VectorSprite):
    image = None  # will be set from Viewer.create_tiles

    def _overwrite_parameters(self):

        self.move = pygame.math.Vector2(x=self.endpos[0] - self.startpos[0], y=self.endpos[1] - self.startpos[1])
        self.picture = self.image
        self.create_image()
        distance = self.max_distance = self.move.length()
        if distance > 0:
            self.move.normalize_ip()  # reduce to lenght 1
        else:
            self.max_age = 0  # kill this arrow as soon as possible
        self.move *= self.speed  #
        self.duration = distance / self.speed  # in seconds
        # arrow shall start in the middle of tile, not in the topleft corner
        self.pos = pygame.math.Vector2(self.startpos[0], self.startpos[1])

        self.set_angle(self.move.angle_to(pygame.math.Vector2(1, 0)))


class FireBallSprite(FlyingObject):
    """ a sprite flying from startpos to endpos with fixed speed
        startpos and endpos are in pixel
    """
    image = None

    def _overwrite_parameters(self):
        self.speed = 220  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = (255, 0, 0)  # orange
        self.explosion_maxspeed = 50  #
        self.explosion_minspeed = 20
        self.explosion_frags = 20
        self.explosion_duration = 0.5

    def update(self, seconds):
        # wobble in flight
        self.set_angle(self.angle + 5)  # rotate image in flight
        super().update(seconds)
        # TODO: zoom?


class ArrowSprite(FlyingObject):
    """ a sprite flying from startpos to endpos with fixed speed
        startpos and endpos are in pixel
    """
    image = None

    def _overwrite_parameters(self):
        self.speed = 200  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = (200, 0, 0)  # orange
        self.explosion_maxspeed = 20  #
        self.explosion_minspeed = 10
        self.explosion_frags = 5
        self.explosion_duration = 0.3


class MagicMissileSprite(FlyingObject):
    image = None

    def _overwrite_parameters(self):
        self.speed = 200  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = None  # random
        self.explosion_maxspeed = 120  #
        self.explosion_minspeed = 80
        self.explosion_frags = 45
        self.explosion_duration = 0.4


class PoisonSpitSprite(FlyingObject):
    image = None

    def _overwrite_parameters(self):
        self.speed = 32  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = (20, 30, 240)  # orange
        self.explosion_maxspeed = 20  #
        self.explosion_minspeed = 15
        self.explosion_frags = 25
        self.explosion_duration = 0.6


class IceBallSprite(FlyingObject):
    """ a blue magic missile, usually shot from player"""
    image = None  # will be overwritten by Viewer.create_tiles

    def _overwrite_parameters(self):
        self.speed = 80  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = (50, 50, 250)  # orange
        self.explosion_maxspeed = 30  #
        self.explosion_minspeed = 3
        self.explosion_frags = 15
        self.explosion_duration = 0.6

    # TODO: cool effect of snowball trail
    # def update(self, seconds):
    #    self.set_angle(self.angle + 10) # rotate image in flight
    #    super().update(seconds)


class DragonFireSprite(FlyingObject):
    """dragon missile"""

    def _overwrite_parameters(self):
        self.speed = 150  # pixel / second
        super()._overwrite_parameters()  # FlyingObject
        # --- values for explosion on impact
        self.explosion_color = (250, 160, 0)  # orange
        self.explosion_maxspeed = 200  #
        self.explosion_minspeed = 50
        self.explosion_frags = 30
        self.explosion_duration = 4.5

    def update(self, seconds):
        # wobble in flight
        self.set_angle(self.angle + random.randint(-5, 5))  # rotate image in flight
        super().update(seconds)
        # TODO: zoom?


class NaturalWeapon():

    def __init__(self, ):
        # self.number = NaturalWeapon.number
        # NaturalWeapon.number += 1
        # NaturalWeapon.store[self.number] = self
        self.damage_bonus = 0
        self.attack_bonus = 0
        self.defense_bonus = 0

        self.overwrite_parameters()

    def overwrite_parameters(self):
        pass


class Fist(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 0
        self.attack_bonus = 0
        self.defense_bonus = 0


class Kick(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 3
        self.attack_bonus = -2
        self.defense_bonus = 2


class YetiSnowBall(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 4
        self.defense_bonus = 1


class YetiSlap(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 4
        self.attack_bonus = -1
        self.defense_bonus = 0


class SnakeBite(NaturalWeapon):

    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 2
        self.defense_bonus = 2


class WolfBite(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 2
        self.defense_bonus = 2


class GolemArm(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 2
        self.attack_bonus = 0
        self.defense_bonus = 0


class DragonBite(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 9
        self.attack_bonus = -3
        self.defense_bonus = -3


class DragonClaw(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 2
        self.attack_bonus = -1
        self.defense_bonus = -1


class DragonTail(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 3
        self.attack_bonus = 0
        self.defense_bonus = 0


class FireBreath(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 4
        self.attack_bonus = 3
        self.defense_bonus = -4


def megaroll(dicestring="1d6 1d20", bonus=0):
    """roll all the dice in the dicestring and adds a bonus to the sum
    1d6 means one 6-sided die without re-roll
    1D6 means one 6-sided die with re-roll.
    re-roll: 1D6 means that when hightest side (6) is rolled, 5 (=6-1) is added and he rolls again"""
    dlist = dicestring.split(" ")
    total = 0
    # print("calculating: ", dicestring, "+", bonus)
    for code in dlist:
        # print("---processing", code)
        if "d" in code:
            # reroll = False
            rolls = int(code.split("d")[0])
            sides = int(code.split("d")[1])
            total += roll((rolls, sides), bonus=0, reroll=False)
        elif "D" in code:
            # reroll = True
            rolls = int(code.split("D")[0])
            sides = int(code.split("D")[1])
            total += roll((rolls, sides), bonus=0, reroll=True)
        else:
            raise SystemError("unknow dice type: {} use 1d6, 1D20 etc".format(code))
        # print("---result of", code, "is :", str(total))
    # print("adding " + str(bonus) + "=", str(total + bonus))
    return total + bonus


def roll(dice, bonus=0, reroll=True):
    """simulate a dice throw, and adding a bonus
       reroll means that if the highest number is rolled,
       one is substracted from the score and
       another roll is added, until a not-hightest number is rolled.
       e.g. 1D6 throws a 6, and re-rolls a 2 -> (6-1)+2= 7"""
    # TODO format-micro-language for aligning the numbers better
    # TODO: accepting string of several dice, like '2D6 3d4' where 'd' means no re-roll, 'D' means re-roll
    rolls = dice[0]
    sides = dice[1]
    total = 0
    # print("------------------------")
    # print("rolling {}{}{} + bonus {}".format(rolls, "D" if reroll else "d", sides, bonus))
    # print("------------------------")
    i = 0
    verb = "rolls   "
    # for d in range(rolls):
    while True:
        i += 1
        if i > rolls:
            break
        value = random.randint(1, sides)

        if reroll and value == sides:
            total += value - 1
            # print("die #{} {} {}  ∑: {} (count as {} and rolls again)".format(i, verb, value, total, value - 1))
            verb = "re-rolls"
            i -= 1
            continue
        else:
            total += value
            # print("die #{} {} {}  ∑: {}".format(i, verb, value, total))
            verb = "rolls   "

    # print("=========================")
    # print("=result:    {}".format(total))
    # print("+bonus:     {}".format(bonus))
    # print("=========================")
    # print("=total:     {}".format(total + bonus))
    return total + bonus


def minmax(value, lower_limit=-1, upper_limit=1):
    """constrains a value inside two limits"""
    value = max(lower_limit, value)
    value = min(upper_limit, value)
    return value


def randomizer(list_of_chances=(1.0,)):
    """gives back an integer depending on chance.
       e.g. randomizer((.75, 0.15, 0.05, 0.05)) gives in 75% 0, in 15% 1, and in 5% 2 or 3"""
    total = sum(list_of_chances)
    v = random.random() * total  # a value between 0 and total
    edge = 0
    for i, c in enumerate(list_of_chances):
        edge += c
        if v <= edge:
            return i
    else:
        raise SystemError("problem with list of chances:", list_of_chances)


def make_text(text="@", font_color=(255, 0, 255), font_size=48, font_name="mono", bold=True, grid_size=None):
    """returns pygame surface with text and x, y dimensions in pixel
       grid_size must be None or a tuple with positive integers.
       Use grid_size to scale the text to your desired dimension or None to just render it
       You still need to blit the surface.
       Example: text with one char for font_size 48 returns the dimensions 29,49
    """
    myfont = pygame.font.SysFont(font_name, font_size, bold)
    size_x, size_y = myfont.size(text)
    mytext = myfont.render(text, True, font_color)
    mytext = mytext.convert_alpha()  # pygame surface, use for blitting
    if grid_size is not None:
        # TODO error handler if grid_size is not a tuple of positive integers
        mytext = pygame.transform.scale(mytext, grid_size)
        mytext = mytext.convert_alpha()  # pygame surface, use for blitting
        return mytext, (grid_size[0], grid_size[1])

    return mytext, (size_x, size_y)


def write(background, text, x=50, y=150, color=(0, 0, 0),
          font_size=None, font_name="mono", bold=True, origin="topleft"):
    """blit text on a given pygame surface (given as 'background')
       the origin is the alignement of the text surface
    """
    if font_size is None:
        font_size = 24
    font = pygame.font.SysFont(font_name, font_size, bold)
    width, height = font.size(text)
    surface = font.render(text, True, color)

    if origin == "center" or origin == "centercenter":
        background.blit(surface, (x - width // 2, y - height // 2))
    elif origin == "topleft":
        background.blit(surface, (x, y))
    elif origin == "topcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "topright":
        background.blit(surface, (x - width, y))
    elif origin == "centerleft":
        background.blit(surface, (x, y - height // 2))
    elif origin == "centerright":
        background.blit(surface, (x - width, y - height // 2))
    elif origin == "bottomleft":
        background.blit(surface, (x, y - height))
    elif origin == "bottomcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "bottomright":
        background.blit(surface, (x - width, y - height))


def get_line(start, end):
    """Bresenham's Line Algorithm
       Produces a list of tuples from start and end
       source: http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
       see also: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

       #>>> points1 = get_line((0, 0), (3, 4))
       # >>> points2 = get_line((3, 4), (0, 0))
       #>>> assert(set(points1) == set(points2))
       #>>> print points1
       #[(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
       #>>> print points2
       #[(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


class Rect:
    """a rectangle object (room) for the dungeon
       x,y is the topleft coordinate
    """

    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def center(self):
        """returns the center coordinate of a room"""
        center_x = (self.x1 + self.x2) // 2  # TODO: // instead of / ?
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        """returns true if this rectangle intersects with another one"""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:
    """# a tile of the map and its properties
       block_movement means blocking the movement of Monster/Player, like a wall or water
       block_sight means blocking the field of view
       block_flying means the tile blocks flying objects like arrows or flying monsters
    """

    # number = 0  # "globale" class variable
    images = []  # for Viewer. light_images, dark_images

    def __init__(self, block_movement=None, block_sight=None, explored=False, block_flying=None):
        # self.number = Tile.number
        # Tile.number += 1 # each tile instance has a unique number
        # generate a number that is mostly 0,but very seldom 1 and very rarely 2 or 3
        # see randomizer .... creates a number between 0 and 8. used for wall and floor tiles

        self.char = "?"
        self.block_movement = block_movement
        self.block_sight = block_sight
        self.block_flying = block_flying
        self.explored = explored
        self.decoration = 0
        self._overwrite()

    def _overwrite(self):
        pass


class Wall(Tile):

    def _overwrite(self):
        super()._overwrite()
        self.char = "#"
        self.decoration = randomizer((.30, 0.15, 0.15, 0.15, 0.1, 0.1, 0.025, 0.025))  # 8
        self.block_movement = True
        self.block_flying = True
        self.block_sight = True


class Floor(Tile):

    def _overwrite(self):
        super()._overwrite()
        self.char = "."
        self.decoration = randomizer((.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.025, 0.025))  # 9
        self.block_movement = False
        self.block_flying = False
        self.block_sight = False


class Object():
    """this is a generic dungeon object: the player, a monster, an item, a stair..
       it's always represented by a character (for text representation).
       NOTE: a dungeon tile (wall, floor, water..) is represented by the Tile class
    """
    images = []  # for Viewer
    number = 0  # current object number. is used as a key for the Game.objects dictionary

    def __init__(self, x, y, z=0, char="?", color=None, **kwargs):
        self.number = Object.number
        Object.number += 1
        Game.objects[self.number] = self
        self.x = x
        self.y = y
        self.z = z
        self.hint = None  # longer description and hint for panel
        self.image_name = None
        self.char = char
        self.color = color
        self.hitpoints = 1  # objects with 0 or less hitpoints will be deleted
        self.look_direction = 0  # 0 -> looks to left, 1 -> looks to right
        # --- make attributes out of all named arguments. like Object(hp=33) -> self.hp = 33
        for key, arg in kwargs.items():
            setattr(self, key, arg)
        # ---- some default values ----
        # if "explored" not in kwargs:
        #    self.explored = False
        if "stay_visible_once_explored" not in kwargs:
            self.stay_visible_once_explored = False
        # --- child classes can do stuff in the _overwrite() method  without needing their own __init__ method
        self._overwrite()
        # --- update legend ---
        # if self.char not in Game.legend:
        #    Game.legend[self.char] = self.__class__.__name__

    def kill(self):
        # delete this object from Game.objects dictionary
        del Game.objects[self.number]

    def _overwrite(self):
        pass


class Item(Object):
    """an item that you can pick up"""

    images = []

    def _overwrite(self):
        self.color = (255, 165, 0)  # orange
        self.weight = 0
        self.i = 0  # index of item image


class Scroll(Item):
    """a scroll with a spell on it"""

    def _overwrite(self):
        super()._overwrite()
        self.color = (200, 200, 0)
        self.char = "i"
        self.hint = "consumable magic scroll "
        # TODO: scroll icons, hotkey tooltip?
        self.spell = random.choice(("heal",
                                    "magic map",
                                    "blink",
                                    "bleed",
                                    "magic missile",
                                    "fireball",
                                    ))
        # disarm onfuse hurt bleed combat bless defense bless bull strenght dragon strenght superman
        # TODO: different image index (i) for different spells


class Gold(Item):
    """a heap of gold"""

    def _overwrite(self):
        super()._overwrite()
        self.color = (200, 200, 0)
        self.char = "*"
        self.value = random.randint(1, 10)


class Arrows(Item):

    def _overwrite(self):
        super()._overwrite()
        self.color = (14, 55, 15)
        self.char = "a"
        self.quantity = random.randint(1, 33)


class Immobile(Object):
    """immobile object like trees, shops, stairs, doors etc
    immobile's can't be picked up """

    def _overwrite(self):
        self.stay_visible_once_explored = True


class Shop(Immobile):
    """a shop to trade items"""

    images_closed = []

    def close_shop(self):
        self.closed = True
        self.images = Shop.images_closed

    def _overwrite(self):
        super()._overwrite()
        # self.images = Shop.images
        self.color = (200, 200, 0)
        self.char = "$"
        self.hint = "press Space to buy hp"
        self.closed = False


class StairUp(Immobile):
    """a stair, going upwards < or downwards >"""

    def _overwrite(self):
        self.char = "<"
        self.color = (128, 0, 128)  # violet
        # self.stay_visible_once_explored = True
        self.hint = "press < to climb up"


class StairDown(Immobile):
    def _overwrite(self):
        self.char = ">"
        self.color = (128, 0, 128)  # violet
        # self.stay_visible_once_explored = True
        self.hint = "press > to climb down"


class Monster(Object):
    """a (moving?) dungeon Monster, like the player, a boss, a NPC..."""
    images = []

    def _overwrite(self):
        self.aggro = 3
        self.char = "M"
        self.shoot_arrows = False
        self.shoot_magic = False

        if self.color is None:
            self.color = (255, 255, 0)

    def ai(self, player):
        """returns dx, dy toward the player (if distance < aggro) or randomly"""
        # if self.immobile:
        #    return 0, 0
        distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

        if distance < self.aggro:
            dx = player.x - self.x
            dy = player.y - self.y
            dx = minmax(dx, -1, 1)
            dy = minmax(dy, -1, 1)
        else:
            dx = random.choice((-1, 0, 1))
            dy = random.choice((-1, 0, 1))
        try:
            target = Game.dungeon[self.z][self.y + dy][self.x + dx]
        except:
            # print("monster trying illegally to leave dungeon")
            return 0, 0
            ##raise SystemError("out of dungeon?", self.x, self.y, self.z)
        if target.block_movement:
            # print("monster trying to move into a wall")
            return 0, 0
        # print("dx dy", self.__class__.__name__, dx, dy)
        return dx, dy

    def move(self, dx, dy, dz=0):
        if dx > 0:
            self.look_direction = 1
        elif dx < 0:
            self.look_direction = 0
        try:
            target = Game.dungeon[self.z + dz][self.y + dy][self.x + dx]
        except:
            raise SystemError("out of dungeon?", self.x, self.y, self.z)
        # --- check if monsters is trying to run into a wall ---
        if target.block_movement:
            if isinstance(self, Player):
                self.hitpoints -= 1
                Game.log.append("ouch!")  # movement is not possible
            return

        self.x += dx
        self.y += dy
        self.z += dz


class Wolf(Monster):

    def _overwrite(self):
        super()._overwrite()
        self.char = "W"
        self.level = 1
        self.aggro = 5
        self.hitpoints = 30
        self.attack = (2, 6)
        self.defense = (2, 5)
        self.damage = (2, 4)
        self.agility = 0.4
        self.natural_weapons = [WolfBite()]
        self.image_name = "direwolf"


class Snake(Monster):

    def _overwrite(self):
        super()._overwrite()
        self.char = "S"
        self.aggro = 2
        self.level = 1
        self.hitpoints = 20
        self.attack = (2, 4)
        self.defense = (3, 3)
        self.damage = (3, 4)
        self.fighting_range = 3
        self.natural_weapons = [SnakeBite()]
        self.image_name = "snake"


class Yeti(Monster):

    def _overwrite(self):
        super()._overwrite()
        self.char = "Y"
        self.aggro = 4
        self.level = 2
        self.hitpoints = 20
        self.attack = (8, 2)
        self.defense = (4, 3)
        self.damage = (4, 5)
        self.fighting_range = 15
        self.natural_weapons = [YetiSnowBall(), YetiSlap()]
        self.image_name = "yeti"


class Dragon(Monster):

    def _overwrite(self):
        super()._overwrite()
        self.char = "D"
        self.aggro = 6
        self.level = 3
        self.immobile = True
        self.shoot_arrows = True
        self.fighting_range = 15  # random.randint(10, 15)
        self.hitpoints = 50
        self.attack = (6, 3)
        self.defense = (6, 3)
        self.damage = (5, 3)
        self.natural_weapons = [DragonBite(), DragonClaw(), DragonTail(), FireBreath()]
        self.image_name = "dragon"


class Player(Monster):

    def _overwrite(self):
        self.char = "@"
        self.color = (0, 0, 255)
        self.hitpoints = 100
        self.hitpoints_max = 125
        self.attack = (3, 6)
        self.defense = (3, 5)
        self.damage = (4, 5)
        self.natural_weapons = [Fist(), Kick()]
        self.items = {}
        self.gold = 100
        self.scrolls = {}
        self.scroll_list = []
        self.victims = {}
        self.arrows = 5
        self.image_name = "arch-mage"
        self.sniffrange_monster = 4
        self.sniffrange_items = 6

    def calculate_scroll_list(self):
        """returns a list of (key, spell name, number of scrolls) tuples"""

        result = []
        for i, spell in enumerate(self.scrolls):
            result.append((ALPHABET[i], spell, self.scrolls[spell]))
        self.scroll_list = result

    def spell_from_key(self, key):
        for i, spell, number in self.scroll_list:
            if i == key and number > 0:
                return spell
        return None


class Game():
    dungeon = []  # list of list of list. 3D map representation, using text chars. z,y,x ! z=0: first level. z=1: second level etc
    fov_map = []  # field of vie map, only for current level!
    objects = {}  # container for all Object instances in this dungeon
    tiles_x = 0
    tiles_y = 0
    torch_radius = 10  # for field of view calculation
    log = []  # message log
    game_over = False
    cursor_x = 0  # absolute coordinate, tile
    cursor_y = 0
    player = None

    # friend_image = "arch-mage-idle"
    # foe_image = None

    def __init__(self, tiles_x=80, tiles_y=40):
        Game.tiles_x = tiles_x  # max. width of the level in tiles
        Game.tiles_y = tiles_y  # max. height of the level in tiles, top row is 0, second row is 1 etc.
        # self.checked = set()   # like a list, but without duplicates. for fov calculation
        Game.player = Player(x=1, y=1, z=0)
        Game.cursor_x = self.player.x
        Game.cursor_y = self.player.y
        # Monster(2,2,0)
        Wolf(2, 2, 0)
        # Yeti(2,2,0)
        Snake(3, 3, 0)
        Yeti(4, 4, 0)
        Dragon(33, 6, 0)
        Dragon(30, 5, 0)
        Dragon(31, 4, 0)
        Shop(7, 1, 0)
        # for a in range(5):
        #    Gold(2, 1+a , 0)
        Gold(3, 1, 0)
        Gold(4, 1, 0)

        for _ in range(15):
            Scroll(4, 4, 0)
            Scroll(5, 4, 0)
            Scroll(4, 6, 0)

        self.levelmonsters = [Snake, Wolf, Yeti, Dragon]
        self.lootlist = [Gold, Arrows, Scroll]
        # Scroll(4, 5, 0)
        self.log.append("Welcome to the first dungeon level (level 0)!")
        self.log.append("Use cursor keys to move around")
        self.load_level(0, "level001.txt", "data")
        self.load_level(1, "level002.txt", "data")
        self.load_level(2, "level003.txt", "data")
        # TODO join create_empty_dungeon_level mit create_rooms_tunnels
        self.create_empty_dungeon_level(tiles_x, tiles_y, filled=True, z=1)  # dungoen is full of walls,
        # carve out some rooms and tunnels in this new dungeon level
        self.rooms = []
        # append empty dungeon level
        self.create_rooms_and_tunnels(z=1)  # carve out some random rooms and tunnels -> self.rooms
        self.place_monsters(z=1)
        self.place_loot(z=1)

        self.turn = 1

    def wait_a_turn(self):
        Game.log.append("You stay around for one turn")

    def shopping(self):
        """shop hp for gold if player stays on a shop
        otherwise, just wait a turn doing nothing
        return True if shopping sucessfull, otherwise return False"""
        # -----on shop buy 10 hp for one gold------
        for o in [o for o in Game.objects.values() if o.z == self.player.z and
                                                      o.x == self.player.x and o.y == self.player.y and
                                                      isinstance(o, Shop)]:
            # player is in a shop
            if o.closed:
                Game.log.append("This shop has gone out of business. Find another shop!")
                return False
            if self.player.gold <= 0:
                Game.log.append("You found a shop but you lack Gold to buy anything :-(")
                return False
            # player is in shop and has gold
            if self.player.hitpoints >= self.player.hitpoints_max:
                Game.log.append("You are already at your maximum health. Shopping is useless now.")
                return False
            # shopping
            self.player.gold -= 1
            self.player.hitpoints += 10
            self.player.hitpoints = min(self.player.hitpoints, self.player.hitpoints_max)
            Game.log.append("You spent one gold for healing")
            # 20% chance that shop dissapears
            if random.random() < 0.2:
                o.close_shop()  # = True
                Game.log.append("The shop is closed for business")
            return True
        else:  # no shop found here
            self.wait_a_turn()
            return False

    def new_turn(self):
        self.turn += 1
        for m in [o for o in Game.objects.values() if
                  o.z == self.player.z and o != self.player and o.hitpoints > 0 and isinstance(o, Monster)]:
            self.move_monster(m)
            # self.remove_dead_monsters(m) # TODO: check if dead monster is removed from all lists

    def player_has_new_position(self):
        """called after postion change of player,
        checks if the player can pick up something or stays
        on an interesting tile"""
        myfloor = []
        # ---- pick up items from the floor -----
        for o in [o for o in Game.objects.values() if (isinstance(o, Item) and o.z == self.player.z and
                                                       o.x == self.player.x and o.y == self.player.y)]:
            #        myfloor.append(o)
            # for o in myfloor:
            if isinstance(o, Gold):
                Game.log.append("You found {} gold!".format(o.value))
                # delay, gold is added only after gold-fly animation
                # animation
                for _ in range(o.value):
                    GoldSprite(pos=pygame.math.Vector2(Viewer.tile_to_pixel((o.x, o.y), center=True)))
                # kill gold from dungeon
                del Game.objects[o.number]


            elif isinstance(o, Arrows):
                Game.log.append("You found {} arrows!".format(o.quantity))
                self.player.arrows += o.quantity
                del Game.objects[o.number]

            elif isinstance(o, Scroll):
                Game.log.append("you found a scroll of {}".format(o.spell))
                if o.spell in self.player.scrolls:
                    self.player.scrolls[o.spell] += 1
                else:
                    self.player.scrolls[o.spell] = 1
                self.player.calculate_scroll_list()
                del Game.objects[o.number]  # kill this scroll instance in the dungeon

    def other_arrow(self, shooterposition, targetposition, object="arrow"):
        # returns  end-tile , victimposition(s)
        # TODO: randomized / formula damage calculation
        # check if line of tiles in arrow path
        flightpath = get_line(shooterposition, targetposition)
        victimposlist = []  # TODO: list of victimpositions (area damage, penetrating arrow)
        for i, (x, y) in enumerate(flightpath):
            if i == 0:  # flightpath = flightpath[1:] # remove first tile, because it is blocked by shooter
                continue  # don't look for objects at shooterposition
            # print(Game.dungeon[self.player.z][y][x]) # TODO: highlight flightpath with cursor movement ?
            if Game.dungeon[self.player.z][y][x].block_flying:
                targetposition = flightpath[i - 1]
                break  # some tile is blocking the path
            # is a monster blocking path ?
            for o in [o for o in Game.objects.values() if
                      o.z == self.player.z and o.y == y and o.x == x and isinstance(o, Monster)]:
                # TODO: arrow/object damage calculation, hit or miss calculation
                if object == "arrow":
                    damage = random.randint(5, 10)
                elif object == "magic missile":
                    damage = random.randint(15, 15)
                elif object == "fireball":
                    damage = random.randint(20, 40)
                else:
                    damage = 4  # TODO testen ob das jemals vorkommt
                # example: a fireball hit the Yeti and makes 20 damage
                Game.log.append("a {} hit the {} and makes {} damage!".format(object, o.__class__.__name__, damage))
                o.hitpoints -= damage
                victimposlist.append((o.x, o.y))
                self.remove_dead_monsters(o)  # only if really dead
                # non-penetration arrow. the flightpath stops here!
                # TODO: penetration arrow
                # return flightpath[:i]
                return flightpath[i], victimposlist
        return targetposition, []  # no victim
        # print("flightpath", flightpath)

    def player_arrow(self):
        """fires an arrow from player to Cursor.
           returns  end, victim"""
        if self.player.arrows < 1:
            Game.log.append("you must find/buy some arrows before you can shoot them")
            return None, None
        if Game.cursor_y == self.player.y and Game.cursor_x == self.player.x:
            Game.log.append("you must move the cursor with mouse before shooting with f")
            return None, None  # start, end, victim
        self.player.arrows -= 1
        return self.other_arrow((self.player.x, self.player.y),
                                (Game.cursor_x, Game.cursor_y))

    def checkfight(self, x, y, z):
        """wir gehen davon aus dass nur der player schaut (checkt) ob er in ein Monster läuft"""
        # Game.foe_image = None
        for o in Game.objects.values():
            if o == self.player:
                continue
            if o.hitpoints <= 0:
                continue
            if not isinstance(o, Monster):
                continue
            if o.z == z:
                if o.x > self.player.x:
                    o.look_direction = 0
                elif o.x < self.player.x:
                    o.look_direction = 1
                if o.x == x and o.y == y:
                    self.fight(self.player, o)
                    return True
        return False

    def move_player(self, dx=0, dy=0):
        if not self.checkfight(self.player.x + dx, self.player.y + dy, self.player.z):
            self.player.move(dx, dy)
            self.make_fov_map()
            self.player_has_new_position()

    def move_monster(self, m):
        """moves a monster randomly, but not into another monster (or wall etc.).
           starts a fight with player if necessary"""
        dx, dy = m.ai(self.player)
        # ai checked already that the move is legal (inside dungeon and not blocked by wall)
        # now only needed to check i running in another monster or into the player
        for o in Game.objects.values():
            if o.z != self.player.z:
                continue
            if o.hitpoints < 1:
                continue
            if not isinstance(o, Monster):
                continue
            if o.x == m.x + dx and o.y == m.y + dy:
                dx, dy = 0, 0
                if o == self.player:
                    self.fight(m, self.player)
                break
        m.x += dx
        m.y += dy

    def fight(self, a, b):
        self.strike(a, b)  # first strike
        if b.hitpoints > 0:
            self.strike(b, a)  # counterstrike
        self.remove_dead_monsters(a, b)  # remove dead monsters from game

    def remove_dead_monsters(self, *monster):
        for mo in monster:  # a monster is a Game.object.value, the key is it's number
            if mo != self.player and mo.hitpoints <= 0:
                name = mo.__class__.__name__
                if name not in self.player.victims:
                    self.player.victims[name] = 1
                else:
                    self.player.victims[name] += 1
                # del Game.objects[monster.number]
                mo.kill()

    def strike(self, a, b):
        wa = random.choice(a.natural_weapons)
        attack_value = roll(a.attack, wa.attack_bonus)
        wd = random.choice(b.natural_weapons)
        defense_value = roll(b.defense, wd.defense_bonus)
        if attack_value > defense_value:
            damage_value = roll(a.damage, wa.damage_bonus)
            b.hitpoints -= damage_value
        else:
            damage_value = 0
        Game.log.append("{} ({}hp) strikes at {} ({}hp) using {} against {}".format(
            a.__class__.__name__,
            a.hitpoints,
            b.__class__.__name__,
            b.hitpoints,
            wa.__class__.__name__,
            wd.__class__.__name__))
        Game.log.append("{}d{}{}{}={}  vs  {}d{}{}{}={} damage: {} hp ({}d{}{}{}) {} --> has {}hp left".format(
            a.attack[0], a.attack[1], "+" if wa.attack_bonus >= 0 else "", wa.attack_bonus, attack_value,
            b.defense[0], b.defense[1], "+" if wd.defense_bonus >= 0 else "", wd.defense_bonus, defense_value,
            damage_value, a.damage[0], a.damage[1], "+" if wa.damage_bonus >= 0 else "", wa.damage_bonus,
            b.__class__.__name__, b.hitpoints))
        # TODO: damage calculation only if hit occurs, else "no hit"

    def check_player(self):
        if self.player.hitpoints <= 0:
            Game.game_over = True

    def consume_scroll(self, spell):
        self.player.scrolls[spell] -= 1
        self.player.calculate_scroll_list()

    def cast(self, spell):
        if spell not in self.player.scrolls or self.player.scrolls[spell] < 1:
            Game.log.append("You have currently no scroll of {}".format(spell))
            return False  # no casting

        # ----- spells that need no cursor position at all -----
        if spell == "magic map":  # make all tiles in this dungeon level explored
            for y, line in enumerate(Game.dungeon[self.player.z]):
                for x, map_tile in enumerate(line):
                    map_tile.explored = True
            self.consume_scroll(spell)
            return True

        elif spell == "heal":  # give player some hitpoints
            self.consume_scroll(spell)
            self.log.append("your healing spell gives you +20 hp")
            self.player.hitpoints += 20  # TODO: max_hp ?
            return True

        # ----- spells that need a cursor position different from player position ---
        if Game.cursor_y == self.player.y and Game.cursor_x == self.player.x:
            Game.log.append("you must select another tile with the mouse before casting {}".format(spell))
            return False  # no casting

        if spell == "bleed":  # monster is  directly damaged, as long as it is visible.
            for monster in [o for o in Game.objects.values() if o.z == self.player.z and
                                                                o.y == Game.cursor_y and o.x == Game.cursor_x and
                                                                isinstance(o, Monster) and o.hitpoints > 0 and
                                                                Game.fov_map[o.y][o.x]]:
                monster.hitpoints -= 20
                Game.log.append("{} bleeds 20 hitpoints".format(monster.__class__.__name__))
                self.consume_scroll(spell)
                return (monster.x, monster.y)  # return tile of bleeding
            return False


        elif spell == "magic missile":  # shoot to Monster at cursor position, like arrow, but more damage
            self.consume_scroll(spell)
            # TODO check if target is outside line of sight / torchradius
            return self.other_arrow((self.player.x, self.player.y),
                                    (Game.cursor_x, Game.cursor_y), "magic missile")
            # return end, victim

        elif spell == "fireball":  # like magic missile, more damage # todo: area damage
            self.consume_scroll(spell)
            return self.other_arrow((self.player.x, self.player.y),
                                    (Game.cursor_x, Game.cursor_y), "fireball")


        elif spell == "blink":  # teleport the player to cursor position
            target_tile = Game.dungeon[self.player.z][Game.cursor_y][Game.cursor_x]
            if not target_tile.explored:
                Game.log.append("You can not blink on a unexplored tile.")
                return False
            if target_tile.block_movement:
                Game.log.append("You can not blink to this tile.")
                return False
            if not Game.fov_map[Game.cursor_y][Game.cursor_x]:
                Game.log.append("You can not blink on a tile outside your field of view")
                return False
            for o in Game.objects.values():
                if (o.z == self.player.z and o.y == Game.cursor_y and
                        o.x == Game.cursor_x and
                        isinstance(o, Monster) and o.hitpoints > 0):
                    Game.log.append("You can not blink on top of a monster")
                    return False
            old = (self.player.x, self.player.y)
            self.move_player(Game.cursor_x - self.player.x, Game.cursor_y - self.player.y)
            self.consume_scroll(spell)
            return old  # success

    def load_level(self, z, name, folder="data"):
        """load a text file and return a list of non-empty lines without newline characters"""
        lines = []
        with open(os.path.join(folder, name), "r") as f:
            for line in f:
                if line.strip() != "":
                    lines.append(line[:-1])  # exclude newline char
        # return lines
        level = []
        for y, line in enumerate(lines):
            row = []
            for x, char in enumerate(line):
                if char == "#":
                    row.append(Wall())
                else:
                    row.append(Floor())
                if char == "<":
                    StairUp(x, y, z, char)
                if char == ">":
                    StairDown(x, y, z, char)
                if char == "$":
                    Shop(x, y, z, char)
                if char == "a":
                    Arrows(x, y, z, char)
                if char == "*":
                    Gold(x, y, z, char)
                if char == "M":
                    if random.random() < 0.5:
                        Wolf(x, y, z)
                    else:
                        Snake(x, y, z)
            level.append(row)
        try:
            Game.dungeon[z] = level
        except:
            Game.dungeon.append(level)
        print("level loaded:", self.dungeon[z])

    def create_rooms_and_tunnels(self, z=0, room_max_size=10, room_min_size=6, max_rooms=30):
        """carve out some random rooms and connects them by tunnels. player is placed in the first room"""
        rooms = []
        num_rooms = 0
        self.room_max_size = room_max_size
        self.room_min_size = room_min_size
        self.max_rooms = max_rooms

        for r in range(self.max_rooms):
            print("carving out room number {}...".format(r))
            # random width and height
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            # random topleft position without going out of the boundaries of the map
            x = random.randint(0, Game.tiles_x - w - 1)
            y = random.randint(0, Game.tiles_y - h - 1)
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            # run through the other rooms and see if they intersect with this one
            # failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    # failed = True
                    break
            # if not failed:
            else:  # for loop got through without a break
                # this means there are no intersections, so this room is valid
                # carve out this room!
                self.create_room(new_room, z)
                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    # create tunnel from player position to this room
                    prev_x, prev_y = self.player.x, self.player.y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                self.create_tunnel(prev_x, prev_y, new_x, new_y, z)
                ### draw a coin (random number that is either 0 or 1)
                ##if random.choice([0,1]) == 1:
                ##    # first move horizontally, then vertically
                ##    self.create_h_tunnel(prev_x, new_x, prev_y, z)
                ##    self.create_v_tunnel(prev_y, new_y, new_x, z)
                ##else:
                ##    # first move vertically, then horizontally
                ##    self.create_v_tunnel(prev_y, new_y, prev_x, z)
                ##    self.create_h_tunnel(prev_x, new_x, new_y, z)
                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1
        # --------- all rooms added. check stairs now -------
        # ---------- stairs up ---------------
        # check if this is level 0, add a single stair up
        if z == 0:
            # place stair up in a random room
            r = random.choice(rooms)
            StairUp(r.center()[0], r.center()[1], z, char="<")
        else:
            # collect all stairs down from previous level,
            # make at same position a stair up, carve a tunnel to a random room if necessary
            stairlist = [(o.x, o.y) for o in Game.objects.values() if
                         o.z == z - 1 and isinstance(o, StairDown)]
            print("creating prev stairlist:", stairlist)
            for (x, y) in stairlist:
                if Game.dungeon[z][y][x].char != ".":
                    # carve tunnel to random room center
                    r = random.choice(rooms)
                    self.create_tunnel(x, y, r.center()[0], r.center()[1], z)
                # make a stair!
                StairUp(x, y, z, char="<")
        # ------------------ stairs down ----------------
        # select up to 3 random rooms and place a stair down in it's center
        num_stairs = 0
        stairs = random.randint(1, 3)
        print("creating stairs down...")
        while num_stairs < stairs:
            r = random.choice(rooms)
            x, y = r.center()
            # is there already any object at this position?
            objects_here = [o for o in Game.objects.values() if o.z == z and o.x == x and o.y == y]
            if len(objects_here) > 0:
                continue
            StairDown(x, y, z, char=">")
            num_stairs += 1
        # --- copy local rooms to self.rooms ---
        self.rooms = rooms

    def place_monsters(self, z):
        """place a random monster inside a room
        mayme more than one. maybe even 2 on the same tile
        depending on levelmonsters
        (in level 1 only snakes, in level 2 snakes or wolfes etc)
        """
        # TODO: better code to avoid 2 monsters spawn on same tile
        for room in self.rooms:
            # print("processing room", room)
            # x1, y1, x2, y2 = room
            # 10% chance for 0 monster in this room
            # 70% chance for 1 monster, 15% for 2, 5% for 3
            for _ in range(randomizer([0.1, 0.7, 0.15, 0.05])):
                mo = random.choice(self.levelmonsters[:z])  # if z > len(levelmonsters), take any monster
                try:
                    x = random.randint(room.x1 + 1, room.x2 - 1)
                    y = random.randint(room.y1 + 1, room.y2 - 1)
                except:
                    print("problem with placing monster in room:{}".format(room))
                    return
                mo(x, y, z)  # create a new monster

    def place_loot(self, z):
        """each floor tile has a small chance to spawn loot and very small chance to spawn a shop"""
        for y, line in enumerate(Game.dungeon[z]):
            for x, tile in enumerate(line):
                # print("tile = ", tile)
                if isinstance(tile, Floor):
                    if random.random() < 0.01:
                        loot = random.choice(self.lootlist)
                        loot(x, y, z)
                    if random.random() < 0.001:
                        Shop(x, y, z)

    def use_stairs(self):
        """go up or done one dungeon level, depending on stair"""
        for o in Game.objects.values():
            if (isinstance(o, StairUp) or
                isinstance(o, StairDown)) and o.z == self.player.z and o.y == self.player.y and o.x == self.player.x:
                break  # all ok, found a stair
        else:
            Game.log.append("You must find a stair up to ascend or descend")
            return False
        if isinstance(o, StairUp):
            self.ascend()
            return True
        elif isinstance(o, StairDown):
            self.descend()
            return True

    def ascend(self):
        """go up one dungeon level (or leave the game if already at level 0)"""
        if self.player.z == 0:
            Game.log.append("You climb back to the surface and leave the dungeon. Good Bye!")
            print(Game.log[-1])
            Game.game_over = True
        else:
            Game.log.append("climbing up one level....")
            self.player.z -= 1
            self.make_fov_map()
            self.player_has_new_position()

    def descend(self):
        """go down one dungeon level. create this level if necessary """
        Game.log.append("climbing down one level, deeper into the dungeon...")
        try:
            l = Game.dungeon[self.player.z + 1]
        except:
            z_new = self.player.z + 1
            Game.log.append("please wait a bit, i must create this level...")
            self.create_empty_dungeon_level(Game.tiles_x, Game.tiles_y,
                                            z=z_new)
            self.create_rooms_and_tunnels(z=z_new)
            self.place_monsters(z=z_new)
            self.place_loot(z=z_new)
        self.player.z += 1
        self.make_fov_map()
        self.player_has_new_position()
        # return True

    def create_empty_dungeon_level(self, max_x, max_y, filled=True, z=0):
        """creates empty dungeon level and append it to Game.dungeon
           if "filled" is False with floor tiles ('.') and an outer wall ('#')
           otherwise all is filled with walls
        """
        # TODO: check max x,y from doors in previous level, randomize level dimension
        # TODO: create tunnel from stair to closest room, not to random room
        floor = []
        for y in range(max_y):
            line = []
            for x in range(max_x):
                if filled:
                    line.append(Wall())  # fill the whole dungeon level with walls
                else:
                    # outer walls only
                    line.append(Wall() if y == 0 or y == max_y - 1 or x == 0 or x == max_x - 1 else Floor())
            floor.append(line)
        try:
            Game.dungeon[z] = floor
        except:
            Game.dungeon.append(floor)
        # print(Game.dungeon)

    def create_room(self, rect, z=0):
        """needs a rect object and carves a room out of this (z) dungeon level. Each room has a wall"""
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                # replace the tile at this position with an floor tile
                Game.dungeon[z][y][x] = Floor()  # replace whatever tile that was there before with a floor

    def create_h_tunnel(self, x1, x2, y, z=0):
        """create an horizontal tunnel in dungeon level z (filled with floor tiles)"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            Game.dungeon[z][y][x] = Floor()  # replace whatever tile that was there before with a floor

    def create_v_tunnel(self, y1, y2, x, z=0):
        """create an vertical tunnel in dungeon level z (filled with floor tiles)"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            Game.dungeon[z][y][x] = Floor()  # replace whatever tile that was there before with a floor

    def create_tunnel(self, x1, y1, x2, y2, z=0):
        if random.choice([0, 1]) == 1:
            # first move horizontally, then vertically
            self.create_h_tunnel(x1, x2, y1, z)
            self.create_v_tunnel(y1, y2, x2, z)
        else:
            # first move vertically, then horizontally
            self.create_v_tunnel(y1, y2, x1, z)
            self.create_h_tunnel(x1, x2, y2, z)

    def make_fov_map(self):
        Game.fov_map = []
        # self.checked = set() # clear the set of checked coordinates
        px, py, pz = self.player.x, self.player.y, self.player.z
        # set all tiles to False
        for line in Game.dungeon[pz]:
            row = []
            for tile in line:
                row.append(False)
            Game.fov_map.append(row)
        # set player's tile to visible
        Game.fov_map[py][px] = True
        # get coordinates form player to point at end of torchradius / torchsquare
        endpoints = set()
        for y in range(py - Game.torch_radius, py + Game.torch_radius + 1):
            if y == py - Game.torch_radius or y == py + Game.torch_radius:
                for x in range(px - Game.torch_radius, px + Game.torch_radius + 1):
                    endpoints.add((x, y))
            else:
                endpoints.add((px - Game.torch_radius, y))
                endpoints.add((px + Game.torch_radius, y))
        for coordinate in endpoints:
            # a line of points from the player position to the outer edge of the torchsquare
            points = get_line((px, py), (coordinate[0], coordinate[1]))
            self.calculate_fov_points(points)
        # print(Game.fov_map)
        # ---------- the fov map is now ready to use, but has some ugly artifacts ------------
        # ---------- start post-processing fov map to clean up the artifacts ---
        # -- basic idea: divide the torch-square into 4 equal sub-squares.
        # -- look of a invisible wall is behind (from the player perspective) a visible
        # -- ground floor. if yes, make this wall visible as well.
        # -- see https://sites.google.com/site/jicenospam/visibilitydetermination
        # ------ north-west of player
        for xstart, ystart, xstep, ystep, neighbors in [
            (-Game.torch_radius, -Game.torch_radius, 1, 1, [(0, 1), (1, 0), (1, 1)]),
            (-Game.torch_radius, Game.torch_radius, 1, -1, [(0, -1), (1, 0), (1, -1)]),
            (Game.torch_radius, -Game.torch_radius, -1, 1, [(0, -1), (-1, 0), (-1, -1)]),
            (Game.torch_radius, Game.torch_radius, -1, -1, [(0, 1), (-1, 0), (-1, 1)])]:

            for x in range(px + xstart, px, xstep):
                for y in range(py + ystart, py, ystep):
                    # not even in fov?
                    try:
                        visible = Game.fov_map[y][x]
                    except:
                        continue
                    if visible:
                        continue  # next, i search invisible tiles!
                    # oh, we found an invisble tile! now let's check:
                    # is it a wall?
                    if Game.dungeon[pz][y][x].char != "#":
                        continue  # next, i search walls!
                    # --ok, found an invisible wall.
                    # check south-east neighbors

                    for dx, dy in neighbors:
                        # does neigbor even exist?
                        try:
                            v = Game.fov_map[y + dy][x + dx]
                            t = Game.dungeon[pz][y + dy][x + dx]
                        except:
                            continue
                        # is neighbor a tile AND visible?
                        if isinstance(t, Floor) and v == True:
                            # ok, found a visible floor tile neighbor. now let's make this wall
                            # visible as well
                            Game.fov_map[y][x] = True
                            break  # other neighbors are irrelevant now

    def calculate_fov_points(self, points):
        """needs a points-list from Bresham's get_line method"""
        for point in points:
            x, y = point[0], point[1]
            # player tile always visible
            if x == self.player.x and y == self.player.y:
                Game.fov_map[y][x] = True  # make this tile visible and move to next point
                continue
            # outside of dungeon level ?
            try:
                tile = Game.dungeon[self.player.z][y][x]
            except:
                continue  # outside of dungeon error
            # outside of torch radius ?
            distance = ((self.player.x - x) ** 2 + (self.player.y - y) ** 2) ** 0.5
            if distance > Game.torch_radius:
                continue

            Game.fov_map[y][x] = True  # make this tile visible
            if tile.block_sight:
                break  # forget the rest


class CursorSprite(VectorSprite):

    def create_image(self):
        self.image = pygame.surface.Surface((Viewer.grid_size[0],
                                             Viewer.grid_size[1]))
        c = random.randint(100, 250)
        pygame.draw.rect(self.image, (c, c, c), (0, 0, Viewer.grid_size[0],
                                                 Viewer.grid_size[1]), 3)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        self.create_image()  # always make new image every frame with different color
        super().update(seconds)


class Viewer():
    width = 0  # screen x resolution in pixel
    height = 0  # screen y resolution in pixel
    panel_width = 200
    log_height = 100
    grid_size = (32, 32)
    pcx = 0  # player x coordinate in pixel
    pcy = 0  # player y coordinate in pixel

    def __init__(self, game, width=640, height=400, grid_size=(32, 32), fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = game
        self.fps = fps
        # position in pixel where all the gold sprites are flying to:
        Viewer.grid_size = grid_size  # make global readable
        Viewer.width = width
        Viewer.height = height
        GoldSprite.blackhole = pygame.math.Vector2(Viewer.width - self.panel_width + 10, Viewer.panel_width + 80)
        self.random1 = random.randint(1, 1000)  # necessary for Viewer.wall_and_floor_theme
        self.random2 = random.randint(1, 1000)
        pygame.init()
        # player center in pixel
        Viewer.pcx = (width - Viewer.panel_width) // 2  # set player in the middle of the screen
        Viewer.pcy = (height - Viewer.log_height) // 2
        self.radarblipsize = 4  # pixel
        self.logscreen_fontsize = 15
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self.playtime = 0.0
        # ------ surfaces for radar, panel and log ----
        # all surfaces are black by default
        self.radarscreen = pygame.surface.Surface((Viewer.panel_width,
                                                   Viewer.panel_width))  # same width and height as panel, sits in topright corner of screen
        self.panelscreen = pygame.surface.Surface((Viewer.panel_width, Viewer.height - Viewer.panel_width))
        self.panelscreen.fill((64, 128, 64))
        self.panelscreen0 = pygame.surface.Surface((Viewer.panel_width, Viewer.height - Viewer.panel_width))
        self.panelscreen0.fill((64, 128, 64))
        self.logscreen = pygame.surface.Surface((Viewer.width - Viewer.panel_width, Viewer.log_height))
        # radar screen center
        self.rcx = Viewer.panel_width // 2
        self.rcy = Viewer.panel_width // 2

        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.make_background()
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        # ------ create bitmaps for player and dungeon tiles ----
        # print("fontsize dim values")
        # test = make_text("@")
        self.images = {}
        # self.legend = {}
        # self.load_images()
        self.lightfloors = []
        self.darkfloors = []
        self.lightwalls = []
        self.darkwalls = []
        self.create_tiles()
        self.wall_and_floor_theme()

        self.prepare_spritegroups()
        self.cursor = CursorSprite(pos=pygame.math.Vector2(x=Viewer.pcx, y=Viewer.pcy))
        self.run()

    def prepare_spritegroups(self):
        self.allgroup = pygame.sprite.LayeredUpdates()  # for drawing
        self.whole_screen_group = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        # self.cursorgroup = pygame.sprite.Group()

        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        GoldSprite.groups = self.allgroup, self.whole_screen_group
        ArrowSprite.groups = self.allgroup
        CursorSprite.groups = self.allgroup

    def pixel_to_tile(self, pixelcoordinate):
        """transform pixelcoordinate (x,y, from pygame mouse).
           returns  distance to player tile in tiles (relative coordinates)"""
        x, y = pixelcoordinate
        return (x - self.pcx) // Viewer.grid_size[0], (y - self.pcy) // Viewer.grid_size[1]

    @staticmethod
    def explosion_at_tile(startpos, color=None, frags=None, minspeed=None, maxspeed=None, age=-2, gravity=None,
                          duration=None):
        """takes a tile coordinate (x,y) and starts explosion animation there"""
        x, y = Viewer.tile_to_pixel(startpos, center=True)
        for _ in range(50 if frags is None else frags):
            mo = pygame.math.Vector2(x=random.randint(5 if minspeed is None else minspeed,
                                                      150 if maxspeed is None else maxspeed), y=0)
            mo.rotate_ip(random.randint(0, 360))
            if duration is None:
                duration = random.random() * 1.5 + 0.5  # between half and 2 seconds

            if color is None:
                c = [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)]  # any color except black
            else:
                c = color
            # randomize a little bit each color value
            for value in c:
                value += random.randint(-20, 20)
            # sanity check for colors
            c = (minmax(c[0], 0, 255),
                 minmax(c[1], 0, 255),
                 minmax(c[2], 0, 255))
            FragmentSprite(pos=pygame.math.Vector2(x, y), move=mo,
                           max_age=duration, age=age, color=c,
                           kill_on_edge=True, gravity=gravity)

    @staticmethod
    def tile_to_pixel(pos, center=False):
        """get a tile coordinate (x,y) and returns pixel (x,y) of tile
           if center is True, returns the center of the tile,
           if center is False, returns the upper left corner of the tile"""
        x, y = pos
        x2 = Viewer.pcx + (x - Game.player.x) * Viewer.grid_size[0]
        y2 = Viewer.pcy + (y - Game.player.y) * Viewer.grid_size[1]
        if center:
            x2 += Viewer.grid_size[0] // 2
            y2 += Viewer.grid_size[1] // 2
        return (x2, y2)

    # def load_images(self):
    #     """single images. char looks to the right by default?"""
    # self.images["arch-mage-attack"] = pygame.image.load(
    #    os.path.join("data", "arch-mage-attack.png")).convert_alpha()

    def move_cursor_to(self, x, y):
        """moves the cursor to tiles xy, """
        target_x, target_y = self.game.player.x + x, self.game.player.y + y
        # check if the target tile is inside the current level dimensions
        level_width = len(Game.dungeon[self.game.player.z][0])
        level_height = len(Game.dungeon[self.game.player.z])
        # print("level dimension in tiles:", level_width, level_height, Game.cursor_x, Game.cursor_y, dx, dy)
        if target_x < 0 or target_y < 0 or target_x >= level_width or target_y >= level_height:
            # print("mouse outside level tiles", x, y)
            return  # cursor can not move outside of the current level
        # check if the target tile is outside the current game window
        x = self.pcx + x * self.grid_size[0]
        y = self.pcy + y * self.grid_size[1]
        if x < 0 or y < 0 or x > (self.width - self.panel_width) or y > (self.height - self.log_height):
            # print("mouse outside game panel", x, y)
            return  # cursor can not move outside of the game window
        #
        # ---- finally, move the cursor ---
        Game.cursor_x = target_x
        Game.cursor_y = target_y
        # self.screen.blit(self.background, (0, 0))

    def make_background(self):
        """scans the subfolder 'data' for .jpg files, randomly selects
        one of those as background image. If no files are found, makes a
        white screen"""
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:].lower() == ".jpg" or file[-5:].lower() == ".jpeg":
                        self.backgroundfilenames.append(os.path.join(root, file))
            random.shuffle(self.backgroundfilenames)  # remix sort order
            self.background = pygame.image.load(self.backgroundfilenames[0])

        except:
            print("no folder 'data' or no jpg files in it")
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((0, 0, 0))  # fill background #
            # TODO: background füllen mit logscreen/panelscreen farbe

        self.background = pygame.transform.scale(self.background,
                                                 (Viewer.width, Viewer.height))
        pygame.draw.rect(self.background, (64, 128, 64), (
            Viewer.width - Viewer.panel_width, Viewer.panel_width, Viewer.height - Viewer.panel_width,
            Viewer.height - Viewer.panel_width))
        self.background.convert()

    def create_tiles(self):
        """load tilemap images and create tiles for blitting"""
        # those are sprite-sheets, taken from dungeon crawl
        player_img = pygame.image.load(os.path.join("data",
                                                    "player.png")).convert_alpha()  # spritesheed, mostly 32x32, figures looking to the left
        # walls and flooors images need to be attributes (self.walls_img..)
        # because they are used in Viewer.wall_and_floor_theme
        self.kelly_img = pygame.image.load(os.path.join("data","colored_tileset.png")).convert_alpha() #
        self.kelly_dark_img = self.kelly_img.copy()
        self.walls_img = pygame.image.load(os.path.join("data", "wall.png")).convert_alpha()  # spritesheet 32x32 pixel
        self.floors_img = pygame.image.load(
            os.path.join("data", "floor.png")).convert_alpha()  # spritesheet 32x32 pixel
        self.walls_dark_img = self.walls_img.copy()
        self.floors_dark_img = self.floors_img.copy()
        feats_img = pygame.image.load(os.path.join("data", "feat.png")).convert_alpha()
        feats_dark_img = feats_img.copy()
        main_img = pygame.image.load(os.path.join("data", "main.png")).convert_alpha()
        main_dark_img = main_img.copy()
        # blit a darker picture over the original to darken
        darken_percent = .50
        for (original, copy) in [(self.walls_img, self.walls_dark_img), (self.floors_img, self.floors_dark_img),
                                 (feats_img, feats_dark_img), (main_img, main_dark_img), (self.kelly_img, self.kelly_dark_img)]:
            dark = pygame.surface.Surface(original.get_size()).convert_alpha()
            dark.fill((0, 0, 0, darken_percent * 255))
            copy.blit(dark, (0, 0))  # blit dark surface over original
            copy.convert_alpha()

        # ---- tiles for Monsters are tuples. first item looks to the left, second item looks to the right
        # --there is no dark tile for monsters. if a monster is outside FOV, it is not blitted
        wolf_tile = pygame.Surface.subsurface(player_img, (823, 607, 32, 32))
        wolf_tile_r = pygame.transform.flip(wolf_tile, True, False)
        Wolf.images = (wolf_tile, wolf_tile_r)
        snake_tile = pygame.Surface.subsurface(player_img, (256, 894, 32, 28))
        snake_tile_r = pygame.transform.flip(snake_tile, True, False)
        Snake.images = (snake_tile, snake_tile_r)
        dragon_tile = pygame.Surface.subsurface(player_img, (747, 559, 33, 49))
        dragon_tile_r = pygame.transform.flip(dragon_tile, True, False)
        Dragon.images = (dragon_tile, dragon_tile_r)
        # TODO useless ? there should be no "pure" monsters in the game, only child classes of Monster
        monster_tile = make_text("M", font_color=(139, 105, 20), grid_size=self.grid_size)[0]
        Monster.images = (monster_tile, monster_tile)
        ##self.player_tile = make_text("@", font_color=self.game.player.color, grid_size=self.grid_size)[0]
        player_tile = pygame.Surface.subsurface(player_img, (153, 1087, 27, 32))
        player_tile_r = pygame.transform.flip(player_tile, True, False)
        Player.images = (player_tile, player_tile_r)
        yeti_tile = pygame.Surface.subsurface(player_img, (193, 1279, 32, 32))
        yeti_tile_r = pygame.transform.flip(yeti_tile, True, False)
        Yeti.images = (yeti_tile, yeti_tile_r)
        self.unknown_tile = make_text(" ", font_color=(14, 14, 14), grid_size=self.grid_size)[0]
        # ---- dungeon elements with light and dark, like stairs, shops...
        StairUp.images = (pygame.Surface.subsurface(feats_img, (32, 192, 32, 32)),
                          pygame.Surface.subsurface(feats_dark_img, (32, 192, 32, 32)))
        StairDown.images = (pygame.Surface.subsurface(feats_img, (0, 192, 32, 32)),
                            pygame.Surface.subsurface(feats_dark_img, (0, 192, 32, 32)))
        # --- item/immobile tiles (scrolls etc) with light and dark
        Shop.images = (pygame.Surface.subsurface(feats_img, (439, 192, 32, 32)),
                       pygame.Surface.subsurface(feats_dark_img, (439, 192, 32, 32)))
        Shop.images_closed = (pygame.Surface.subsurface(feats_img, (695, 192, 32, 32)),
                              pygame.Surface.subsurface(feats_dark_img, (695, 192, 32, 32)))

        Gold.images = (pygame.Surface.subsurface(main_img, (207, 655, 26, 20)),
                       pygame.Surface.subsurface(main_dark_img, (207, 655, 26, 20)))
        Scroll.images = (pygame.Surface.subsurface(main_img, (188, 412, 27, 28)),
                         pygame.Surface.subsurface(main_dark_img, (188, 412, 27, 28)))
        Arrows.images = (pygame.Surface.subsurface(main_img, (681, 224, 27, 16)),
                         pygame.Surface.subsurface(main_dark_img, (681, 224, 27, 16)))
        # ------ sprites ----- TODO: sprite-list for animation?
        GoldSprite.image = pygame.Surface.subsurface(main_img, (462, 678, 13, 9))
        # arrow looking right, only used for Sprite Animation (arrow on the ground has different picture)
        ArrowSprite.image = pygame.Surface.subsurface(main_img, (808, 224, 22, 7))
        # self.arrow_tiles = ( pygame.Surface.subsurface(main_img, (808,224,22,7)),
        #                     pygame.Surface.subsurface(main_dark_img, (808,224,22,7)))
        FireBallSprite.image = pygame.Surface.subsurface(main_img, (159, 840, 16, 14))
        MagicMissileSprite.image = pygame.Surface.subsurface(main_img, (449, 834, 31, 5))
        IceBallSprite.image = pygame.Surface.subsurface(main_img, (72, 840, 21, 13))  # magic missile, orange rectangle
        PoisonSpitSprite.image = pygame.Surface.subsurface(main_img, (238, 853, 10, 10))
        DragonFireSprite.image = pygame.Surface.subsurface(main_img, (24, 841, 16, 14))
        BleedingSprite.image = pygame.Surface.subsurface(feats_img, (248, 160, 32, 22))  # (717,417,29,25))
        BlinkSprite.image = pygame.Surface.subsurface(feats_img, (0, 384, 30, 32))
        HealingSprite.image = pygame.Surface.subsurface(main_img, (158, 381, 15, 15))
        # ---- Animations ---
        FireBallAnimation.images = [pygame.Surface.subsurface(main_img, (55, 840, 16, 17)),
                                    pygame.Surface.subsurface(main_img, (304, 807, 28, 25)),
                                    pygame.Surface.subsurface(main_img, (869, 840, 32, 32)),
                                    pygame.Surface.subsurface(main_img, (901, 840, 32, 32)),
                                    pygame.Surface.subsurface(main_img, (933, 840, 32, 32)),
                                    ]
        FlameAnimation.images = [pygame.Surface.subsurface(feats_img, (5, 320, 18, 25)),
                                 pygame.Surface.subsurface(feats_img, (32, 320, 17, 25)),
                                 pygame.Surface.subsurface(feats_img, (60, 320, 17, 25)),
                                 pygame.Surface.subsurface(feats_img, (117, 320, 18, 25)),
                                 pygame.Surface.subsurface(feats_img, (144, 320, 18, 25)),
                                 pygame.Surface.subsurface(feats_img, (172, 320, 20, 25)),
                                 pygame.Surface.subsurface(feats_img, (199, 320, 19, 25)),
                                 ]
        # ---- gui tiles ----
        self.goldstack_image = pygame.Surface.subsurface(main_img, (507, 656, 32, 32))  # stack of gold

    def wall_and_floor_theme(self):
        """select a set of floor/walltiles, depending on level number (z)"""
        # TODO: make one function out of this and call it twice
        ##random.seed(self.game.player.z)
        # ---------------------------- walls ----------------------
        # walls: all tiles 32x32, huge image is 1024x1280 x(topleft), y(topleft), how many elements to the right
        # create 2 very large integer numbers
        a = self.game.player.z * self.random1
        b = self.game.player.z * self.random2
        walls = [(0, 0, 8), (256, 0, 8), (512, 0, 8), (768, 0, 8),
                 (0, 32, 8), (256, 32, 8), (512, 32, 8), (768, 32, 8),
                 (0, 64, 8), (256, 64, 8), (512, 64, 8), (768, 64, 8),
                 (0, 96, 8), (256, 96, 8), (512, 96, 8), (768, 96, 8),
                 (0, 128, 8), (256, 128, 8), (512, 128, 8), (768, 128, 8),
                 (0, 160, 8), (256, 160, 8), (512, 160, 8), (768, 160, 8),
                 (0, 192, 8), (256, 192, 8), (512, 192, 8), (768, 192, 4),
                 ]
        walls = walls[a % len(walls)]  # like random.choice, but with consistent result
        # walls = (992,384,5)
        # ---- add single subimages to darkwalls and lightwalls---
        # x1,y1, x2,y2: 0,225, 32 , 256
        # see class floor, attribute decoration for probability. first img comes most often
        mywalls = []
        for i in range(walls[2]):  # how many tiles
            x = walls[0] + i * 32  # topleft x
            y = walls[1]  # topleft y
            if x > 1024 - 32:  # wrap-around into next line
                x = x - 1024
                y += 32
            mywalls.append((x, y))
        darkwalls = []
        lightwalls = []
        for (x, y) in mywalls:
            lightwalls.append(pygame.Surface.subsurface(self.walls_img, (x, y, 32, 32)))
            darkwalls.append(pygame.Surface.subsurface(self.walls_dark_img, (x, y, 32, 32)))
        Wall.images = [lightwalls, darkwalls]
        # ---------------------- floors ------------------
        # floor.png 1024x960, tiles are 32x32
        # floors: all32x32: x(topleft), y(topleft), how many elements
        floors = [(576, 0, 9), (128, 32, 9), (416, 32, 9), (704, 32, 9), (256, 64, 9), (544, 64, 9),
                  (96, 96, 9), (384, 96, 9), (672, 96, 9), (224, 128, 9), (512, 128, 9), (64, 160, 4),
                  (192, 160, 4), (320, 160, 4), (448, 160, 9),
                  ]
        floors = floors[b % len(floors)]  # like random.choice, but consistent
        ##floors = (928,512,10)
        myfloors = []
        for i in range(floors[2]):
            x = floors[0] + i * 32
            y = floors[1]
            if x > 1024 - 32:
                x = x - 1024
                y += 32
            myfloors.append((x, y))
        darkfloors = []
        lightfloors = []
        for (x, y) in myfloors:
            lightfloors.append(pygame.Surface.subsurface(self.floors_img, (x, y, 32, 32)))
            darkfloors.append(pygame.Surface.subsurface(self.floors_dark_img, (x, y, 32, 32)))
        Floor.images = [lightfloors, darkfloors]
        # ------------- kelly overwrite walls , 16x16 ---------------------
        
        lightwalls = []
        darkwalls = []
        # ------------------------------------------------- x, y (left-top corner), width, height
        lightwalls.append(self.resize_tile_to_gridsize(pygame.Surface.subsurface(self.kelly_img, (170, 289, 16, 16))))
        darkwalls.append(self.resize_tile_to_gridsize(pygame.Surface.subsurface(self.kelly_dark_img, (170, 289, 16, 16))))
        lightwalls.append(self.resize_tile_to_gridsize(pygame.Surface.subsurface(self.kelly_img, (170, 306, 16, 16))))
        darkwalls.append(self.resize_tile_to_gridsize(pygame.Surface.subsurface(self.kelly_dark_img, (170, 306, 16, 16))))

        Wall.images = [lightwalls, darkwalls]

    def resize_tile_to_gridsize(self, original):
        """takes the original bitmap, transform it to Viewer.grid_size x Viewer.grid_size and returns it"""
        return pygame.transform.scale(original, (Viewer.grid_size[0], Viewer.grid_size[1]))


    def tile_blit(self, surface, x_pos, y_pos, corr_x=0, corr_y=0):
        """correctly blits a surface at tile-position x,y, so that the player is always centered at pcx, pcy"""
        x = (x_pos - self.game.player.x) * self.grid_size[0] + self.pcx + corr_x
        y = (y_pos - self.game.player.y) * self.grid_size[1] + self.pcy + corr_y
        # check if the tile is inside the game screen, otherwise ignore
        if (x > (Viewer.width - Viewer.panel_width)) or (y > (Viewer.height - Viewer.log_height)):
            return
        if (x + self.grid_size[0]) < 0 or (y + self.grid_size[1]) < 0:
            return

        self.screen.blit(surface, (x, y))

    def start_healing_sprites(self):
        for _ in range(15):
            p = pygame.math.Vector2(self.pcx + Viewer.grid_size[0] // 2 + random.randint(-20, 20),
                                    self.pcy + Viewer.grid_size[1])
            m = pygame.math.Vector2(0, -random.random() * 15 - 3)
            a = random.random() * -1.5
            HealingSprite(pos=p, move=m, age=a, max_age=2)

    def draw_dungeon(self):
        z = self.game.player.z
        px, py = self.game.player.x, self.game.player.y
        # first, draw dungeon tiles (walls and floors)
        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                # ---- check if tiles is outside torch radius of player ----
                # ---- or otherwise (mostly) invisible
                if distance > Game.torch_radius or not Game.fov_map[y][x]:
                    dark = True  # 1
                else:
                    dark = False  # 0
                    # -- only blit (dark) if tile is explored. only draw explored Items (stairs)
                # --------blit basic dungeon tiles (wall, floor) -------
                if not isinstance(map_tile, Wall) and not isinstance(map_tile, Floor):
                    raise SystemError("invalid map tile")
                images = map_tile.images[dark]
                i = map_tile.decoration % len(images)
                c = images[i]
                if dark and not map_tile.explored:
                    c = self.unknown_tile
                if not dark and not map_tile.explored:
                    map_tile.explored = True  # only dungeon Tile instances can have attribute explored
                self.tile_blit(c, x, y)
                # --- immobiles (shop, stair... ) #
                for o in [o for o in Game.objects.values() if
                          isinstance(o, Immobile) and o.z == z and
                          o.x == x and o.y == y]:
                    # print(dark)
                    c = o.images[dark]
                    if dark and not map_tile.explored:
                        continue  # skip
                    self.tile_blit(c, x, y)
                # ----- items (arrows, gold etc)---
                for o in [o for o in Game.objects.values() if
                          isinstance(o, Item) and o.z == z and
                          o.x == x and o.y == y]:
                    c = o.images[dark]
                    if dark and not map_tile.explored:
                        continue
                    self.tile_blit(c, x, y)
        # ------- now the monsters on top of all, -----
        # -- whole dungeon has to be already be painted, because
        # sometimes monster are bigger than tiles
        self.draw_all_monsters()

    def draw_all_monsters(self):
        z = self.game.player.z
        px, py = self.game.player.x, self.game.player.y
        # first, draw dungeon tiles (walls and floors)
        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                if distance > Game.torch_radius or not Game.fov_map[y][x]:
                    continue  # no monsters visible in the darkdark = True # 1
                # it is not dark here
                for o in [o for o in Game.objects.values() if
                          isinstance(o, Monster) and o.hitpoints > 0 and
                          o.z == z and o.x == x and o.y == y]:
                    # TODO: use sprites here (with animation) instead of tiles
                    c = o.images[o.look_direction]
                    self.tile_blit(c, x, y)

    def draw_radar(self):
        # make black square in top of panel
        self.radarscreen.fill((10, 10, 10))  # clear radarscreen
        delta_tiles = int(self.panel_width / 2 // self.radarblipsize)
        # make a radar blit for each explored dungeong tile
        for x in range(self.game.player.x - delta_tiles, self.game.player.x + delta_tiles + 1):
            if x < 0:
                continue
            for y in range(self.game.player.y - delta_tiles, self.game.player.y + delta_tiles + 1):
                if y < 0:
                    continue
                distance = ((x - self.game.player.x) ** 2 + (y - self.game.player.y) ** 2) ** 0.5
                try:
                    t = Game.dungeon[self.game.player.z][y][x]
                except:
                    continue
                color = (10, 10, 10)  # black
                dx = -(x - self.game.player.x) * self.radarblipsize
                dy = -(y - self.game.player.y) * self.radarblipsize
                if t.explored:
                    if t.block_movement:
                        color = (50, 50, 250)  # blue wall
                    else:
                        color = (150, 150, 150)  # light grey corridor
                    # pygame.draw.rect(self.radarscreen, color,
                    #                 (self.rcx - dx, self.rcy - dy, self.radarblipsize, self.radarblipsize))
                # ---if a stair is there, paint it (if explored) ---
                for o in Game.objects.values():
                    if o.z == self.game.player.z and o.y == y and o.x == x:
                        if Game.dungeon[self.game.player.z][y][x].explored:
                            if isinstance(o, StairDown):
                                color = (128, 255, 128)
                            elif isinstance(o, StairUp):
                                color = (64, 255, 64)
                            elif isinstance(o, Shop):
                                color = (200, 200, 200)
                        if isinstance(o, Item):
                            if Game.fov_map[y][x] or distance < self.game.player.sniffrange_items:
                                color = (0, 200, 0)
                        elif isinstance(o, Monster):
                            if Game.fov_map[y][x] or distance < self.game.player.sniffrange_monster:
                                color = (255, 0, 0)

                pygame.draw.rect(self.radarscreen, color,
                                 (self.rcx - dx, self.rcy - dy, self.radarblipsize, self.radarblipsize))
        # make withe glowing dot at center of radarmap
        white = random.randint(200, 255)
        color = (white, white, white)
        pygame.draw.rect(self.radarscreen, color, (self.rcx, self.rcy, self.radarblipsize, self.radarblipsize))
        # blit radarscreen on screen
        self.screen.blit(self.radarscreen, (Viewer.width - Viewer.panel_width, 0))

    def draw_panel(self):
        # print("inside paneldraw!")
        # fill panelscreen with color
        self.panelscreen.blit(self.panelscreen0, (0, 0))
        # self.panelscreen.fill((64, 128, 64))
        # write stuff in the panel
        # -y5------------
        write(self.panelscreen, text="dungeon: {}".format(self.game.player.z), x=5, y=5, color=(255, 255, 255))
        # - hitpoint bar in red, starting left
        pygame.draw.rect(self.panelscreen, (200, 0, 0),
                         (0, 35, self.game.player.hitpoints * Viewer.panel_width / self.game.player.hitpoints_max, 28))
        # -y35--------------------
        write(self.panelscreen, text="hp: {}/{}".format(
            self.game.player.hitpoints, self.game.player.hitpoints_max), x=5, y=35,
              color=(255, 255, 255), font_size=24)
        # -y65 ----------------------
        self.panelscreen.blit(self.goldstack_image, (5, 65))
        write(self.panelscreen, text="   {}".format(
            self.game.player.gold), x=5, y=65, color=(255, 255, 0), font_size=24)

        # --- write cursor information into panel ---
        # - y95 ------

        tilex, tiley = Game.cursor_x, Game.cursor_y
        ##print("cursor is at ", tilex, tiley, "=", self.tile_to_pixel(tilex, tiley))
        ##print("tile:", tilex, tiley)
        t = Game.dungeon[self.game.player.z][tiley][tilex]

        write(self.panelscreen, text="x:{} y:{} turn:{}".format(tilex, tiley, self.game.turn), x=5, y=95,
              color=(255, 255, 255),
              font_size=16)
        # tile information
        # - y115
        write(self.panelscreen, text=t.__class__.__name__ if t.explored else "not yet explored", x=5, y=115,
              color=(255, 255, 255), font_size=16)
        # objects on top of that tile ?
        here = []
        hints = []
        if t.explored:
            for o in Game.objects.values():
                # print("object:",o)
                if o.z == self.game.player.z and o.x == tilex and o.y == tiley and o.hitpoints > 0:
                    if not isinstance(o, Monster):
                        here.append(o)
                        if o.hint is not None:
                            hints.append(o.hint)
                    else:
                        # monster only if inside fov
                        if Game.fov_map[o.y][o.x]:
                            here.append(o)
                            if o.hint is not None:
                                hints.append(o.hint)

        # print(here)
        dy = 0
        for dy, thing in enumerate(here):
            # -y135 + 20*dy
            # TODO: blit text in variable fontsize/panel width with word wrap -> python module textwrap
            if isinstance(thing, Monster):
                t = thing.__class__.__name__ + " {} hp".format(thing.hitpoints)
            else:
                t = thing.__class__.__name__
            write(self.panelscreen, text=t, x=5, y=135 + 20 * dy, color=(255, 255, 255),
                  font_size=16)

        # --- print hints ----
        y = 135 + 20 * dy + 50
        for h in hints:
            write(self.panelscreen, text=h, x=5, y=y, color=(0, 0, 0), font_size=10)
            y += 20
        # ---- arrows -----
        write(self.panelscreen, text="Arrows (f): {}".format(self.game.player.arrows),
              x=5, y=y, color=(255, 255, 255), font_size=14)
        y += 20
        # ---- magic scrolls -----
        if len(self.game.player.scrolls) > 0:
            write(self.panelscreen, text="Magic: use CTRL+", color=(80, 0, 80),
                  font_size=20, x=5, y=y)
            y += 20
        for key, spell, number in self.game.player.scroll_list:
            t = "{}: {} x {}".format(key, spell, number)
            write(self.panelscreen, text=t, x=5, y=y, color=(255, 255, 255), font_size=14)
            y += 15

        # blit panelscreen
        self.screen.blit(self.panelscreen, (Viewer.width - self.panel_width, self.panel_width))

    def draw_log(self):
        # fill logscreen with color
        self.logscreen.fill((150, 150, 150))

        # write the log lines, from bottom (last log line) to top.
        for i in range(-1, -25, -1):  # start, stop, step
            try:
                text = "{}: {}".format(len(Game.log) + i, Game.log[i])
                c = (0, 0, 0) if (len(Game.log) + i) % 2 == 0 else (87, 65, 0)
            except:
                continue
            # ungerade und gerade Zeilennummern sollen verschiedenen
            # farben haben

            textsf, (w, h) = make_text(text, font_color=c,
                                       font_size=self.logscreen_fontsize)
            self.logscreen.blit(textsf, (5, self.log_height + i * h))
        # ---- blit logscreen ------
        self.screen.blit(self.logscreen, (0, Viewer.height - self.log_height))

    def new_turn_in_Viewer(self):
        """new turn in Viewer, calls new turn in Game and updates graphics that may have changed, plays animations etc"""
        # all shooters (except player) shoot their arrows at the same time

        for monster in [o for o in Game.objects.values() if
                        o != self.game.player and o.z == self.game.player.z and
                        isinstance(o, Monster) and o.shoot_arrows and o.hitpoints > 0]:
            # calculate distance to player
            distance = ((monster.x - self.game.player.x) ** 2 + (monster.y - self.game.player.y) ** 2) ** 0.5
            # monster shoots at you if it can, player is in shooting range and player sees monster
            if Game.fov_map[monster.y][monster.x] and distance < monster.fighting_range:
                ## FlyObject (start, end)
                end, victimpos = self.game.other_arrow((monster.x, monster.y),
                                                       (self.game.player.x, self.game.player.y), object="fire")
                start = self.tile_to_pixel((monster.x, monster.y), center=True)
                # decide tpye of flying object
                if isinstance(monster, Dragon):
                    flyclass = DragonFireSprite
                if isinstance(monster, Yeti):
                    flyclass = IceBallSprite
                if isinstance(monster, Snake):
                    flyclass = PoisonSpitSprite
                # a = IceBallSprite(startpos=start, endpos=self.tile_to_pixel(end, center=True))
                a = flyclass(startpos=start, endpos=self.tile_to_pixel(end, center=True))
                if self.playtime + a.duration > self.animation:
                    self.animation = self.playtime + a.duration
                # make a explosion on impact (at the player)
                if len(victimpos) > 0:
                    self.explosion_at_tile(startpos=(self.game.player.x, self.game.player.y),
                                           color=a.explosion_color,
                                           minspeed=a.explosion_minspeed,
                                           maxspeed=a.explosion_maxspeed,
                                           frags=a.explosion_frags,
                                           duration=a.explosion_duration,
                                           age=-a.duration)

        self.animate_sprites_only()
        # self.draw_panel()  # to update player hitpoints
        old_gold = self.game.player.gold
        self.game.new_turn()

        delta_gold = self.game.player.gold - old_gold
        if delta_gold > 0:
            self.explosion_at_tile(startpos=(self.game.player.x, self.game.player.y),
                                   frags=delta_gold, minspeed=10, maxspeed=50, gravity="gold")
        self.redraw = True
        # self.redraw = True

    def animate_sprites_only(self):
        """loop as long as necessary to finish all animations, before coninuing with main loop"""
        while self.animation > self.playtime:
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            self.playtime += seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # running = False
                    return
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # running = False

            self.allgroup.clear(self.screen, self.spriteless_background)
            self.allgroup.update(seconds)
            self.allgroup.draw(self.screen)
            # self.draw_panel() # TODO: remove? Fragments destroy panel otherwise. making area for Fragment sprite?
            pygame.display.update()

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(True)
        oldleft, oldmiddle, oldright = False, False, False
        self.game.make_fov_map()
        self.redraw = True
        # exittime = 0
        self.spriteless_background = pygame.Surface((Viewer.width - Viewer.panel_width, Viewer.height))
        # fill panel color into spriteless background
        # pygame.draw.rect(self.spriteless_background,(64, 128, 64), (self.width-self.panel_width,
        #                                                            self.panel_width, self.panel_width,
        #                                                            self.height-self.panel_width))
        # while True:
        self.screen.blit(self.spriteless_background, (0, 0))
        ###    pygame.display.flip()
        show_range = False
        self.animation = 0  # how many seconds animation should be played until the game accept inputs, new turn etc again
        reset_cursor = True
        log_lines = len(Game.log)
        while running:
            # print("mouse:", pygame.mouse.get_pos())
            self.game.check_player()  # if player has hitpoints left
            if Game.game_over:
                Flytext(text="Game Over", fontsize=100, pos=pygame.math.Vector2(self.pcx, self.pcy),
                        move=pygame.math.Vector2(0, -5), acceleration_factor=1.0, color=(200, 20, 20))
                for dy, v in enumerate(self.game.player.victims):
                    # print(v, self.game.player.victims[v])
                    Flytext(text="you killed {} {}".format(self.game.player.victims[v], v),
                            pos=pygame.math.Vector2(self.pcx, self.pcy + 50 + 20 * dy),
                            move=pygame.math.Vector2(0, -5), acceleration_factor=1.0,
                            fontsize=25, color=(40, 40, 240))

                self.animation = self.playtime + 5 + dy * 0.5
                self.animate_sprites_only()
                running = False
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            # --- redraw whole screen if animation has ended ----
            # if animation > self.playtime and animation < (self.playtime + seconds):
            #    self.redraw = True

            self.playtime += seconds

            # ------ mouse handler ------
            # left, middle, right = pygame.mouse.get_pressed()
            # oldleft, oldmiddle, oldright = left, middle, right

            # ------ joystick handler -------
            # for number, j in enumerate(self.joysticks):
            #    if number == 0:
            #        x = j.get_axis(0)
            #        y = j.get_axis(1)
            #        buttons = j.get_numbuttons()
            #        for b in range(buttons):
            #            pushed = j.get_button(b)

            # ------------ pressed keys (in this moment pressed down)------
            pressed_keys = pygame.key.get_pressed()

            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # ---- move the game cursor with wasd ----
                    # if event.key == pygame.K_a:
                    #    self.move_cursor(-1, 0)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #    # Game.cursor_x -= 1
                    # if event.key == pygame.K_d:
                    #    self.move_cursor(1, 0)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #
                    #    # Game.cursor_x += 1
                    # if event.key == pygame.K_w:
                    #    self.move_cursor(0, -1)
                    #    self.redraw = True
                    #    reset_cursor = False#
                    #
                    #    # Game.cursor_y -= 1
                    # if event.key == pygame.K_s:
                    #    self.move_cursor(0, 1)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #
                    #    # Game.cursor_y += 1
                    #
                    # ----------- magic with ctrl key and dynamic key -----
                    # if pressed_keys[pygame.K_RCTRL] or pressed_keys[pygame.K_LCTRL]:
                    if event.mod & pygame.KMOD_CTRL:  # any or both ctrl keys are pressed
                        key = pygame.key.name(event.key)  # name of event key: a, b, c etc.
                        spell = self.game.player.spell_from_key(key)  # get the spell that is currently bond to this key
                        result = self.game.cast(spell)  # sucessfull casting -> new turn
                        # --- spell animations ----
                        if spell == "magic missile":
                            end, victimposlist = result
                            a = MagicMissileSprite(startpos=(self.pcx + Viewer.grid_size[0] // 2,
                                                             self.pcy + Viewer.grid_size[1] // 2),
                                                   endpos=self.tile_to_pixel(end, center=True))
                            self.animation = self.playtime + a.duration
                            if len(victimposlist) > 0:
                                for victimpos in victimposlist:
                                    self.explosion_at_tile(victimpos, age=-a.duration)
                            self.animate_sprites_only()
                        elif spell == "fireball":
                            end, victimposlist = result
                            a = FireBallSprite(startpos=(self.pcx + Viewer.grid_size[0] // 2,
                                                         self.pcy + Viewer.grid_size[1] // 2),
                                               endpos=self.tile_to_pixel(end, center=True))
                            self.animation = self.playtime + a.duration
                            FireBallAnimation(pos=pygame.math.Vector2(Viewer.tile_to_pixel(end)), zoom_delta=1.9,
                                              age=-a.duration)
                            if len(victimposlist) > 0:
                                for victimpos in victimposlist:
                                    pass
                                    #self.explosion_at_tile(victimpos, age=-a.duration)

                            self.animate_sprites_only()
                        elif spell == "heal":
                            if result:
                                self.start_healing_sprites()

                        elif spell == "bleed":
                            if result:
                                # play blood animation for 1 second at victimtile (result)
                                duration = 0.45
                                BleedingSprite(pos=pygame.math.Vector2(self.tile_to_pixel(result, center=False)),
                                               max_age=duration, zoom_delta=0.1)
                                self.animation = self.playtime + duration
                                self.animate_sprites_only()

                        elif spell == "blink":
                            if result:  # result old position
                                BlinkSprite(pos=pygame.math.Vector2(self.tile_to_pixel(result)), zoom_delta=-0.008,
                                            max_age=2)  # shrink
                                BlinkSprite(pos=pygame.math.Vector2(self.pcx + Viewer.grid_size[0], self.pcy),
                                            zoom_delta=0.005,
                                            max_age=1.4)

                        if result:
                            self.new_turn_in_Viewer()
                    # --- end of spellcasting, no CTRL key is pressed ---
                    else:

                        # ---- -simple player movement with cursor keys -------
                        if event.key in (pygame.K_RIGHT, pygame.K_KP6):
                            self.new_turn_in_Viewer()
                            self.game.move_player(1, 0)

                        if event.key in (pygame.K_LEFT, pygame.K_KP4):
                            self.new_turn_in_Viewer()
                            self.game.move_player(-1, 0)

                        if event.key in (pygame.K_UP, pygame.K_KP8):
                            self.new_turn_in_Viewer()
                            self.game.move_player(0, -1)

                        if event.key in (pygame.K_DOWN, pygame.K_KP2):
                            self.new_turn_in_Viewer()
                            self.game.move_player(0, 1)

                        # --- diagonal movement ---
                        if event.key in (pygame.K_KP7, pygame.K_HOME):
                            self.new_turn_in_Viewer()
                            self.game.move_player(-1, -1)

                        if event.key in (pygame.K_KP9, pygame.K_PAGEUP):
                            self.new_turn_in_Viewer()
                            self.game.move_player(1, -1)

                        if event.key in (pygame.K_KP1, pygame.K_END):
                            self.new_turn_in_Viewer()
                            self.game.move_player(-1, 1)

                        if event.key in (pygame.K_KP3, pygame.K_PAGEDOWN):
                            self.new_turn_in_Viewer()
                            self.game.move_player(1, 1)

                        if event.key == pygame.K_SPACE:
                            # Game.turn += 1  # wait a turn
                            if self.game.shopping():
                                self.start_healing_sprites()
                            self.new_turn_in_Viewer()

                        if event.key == pygame.K_f:
                            # fire arrow to cursor
                            end, victimpos = self.game.player_arrow()  # None , None, None  when player can not shoot, otherwise startpos, endpos, victim
                            if end is not None:
                                a = ArrowSprite(startpos=(self.pcx + Viewer.grid_size[0] // 2,
                                                          self.pcy + Viewer.grid_size[1] // 2),
                                                endpos=self.tile_to_pixel(end, center=True))
                                self.animation = self.playtime + a.duration
                                if len(victimpos) > 0:
                                    pass  # todo victim impact animation

                                self.animate_sprites_only()
                                self.new_turn_in_Viewer()

                        if event.key in (pygame.K_LESS, pygame.K_GREATER):
                            self.new_turn_in_Viewer()
                            # go up a level
                            if self.game.use_stairs():
                                self.redraw = True
                                self.wall_and_floor_theme()  # new walls and floor colors
                                # if self.game.player.z == 100:
                                #    Flytext("You have won", fontsize=64, color=(230,230,25),
                                #            pos=pygame.math.Vector2(400,400),
                                #            move=pygame.math.Vector2(-20,0))
                                #    self.animation = self.playtime + 5
                                #    self.animate_sprites_only()
                                #    Game.game_over = True

                        if event.key == pygame.K_PLUS:
                            if event.mod & pygame.KMOD_SHIFT:
                                # zoom out radar
                                self.radarblipsize *= 0.5
                                self.radarblipsize = int(max(1, self.radarblipsize))  # don't become zero
                                # print("radarblip:", self.radarblipsize)
                                self.redraw = True
                            else:
                                # more torch radius
                                Game.torch_radius += 1
                                self.game.make_fov_map()
                                self.redraw = True

                        if event.key == pygame.K_MINUS:
                            if event.mod & pygame.KMOD_SHIFT:
                                # zoom in radar
                                self.radarblipsize *= 2
                                self.radarblipsize = min(64, self.radarblipsize)  # don't become absurd large
                                self.redraw = True
                            else:
                                # --- decrease torch radius ----
                                Game.torch_radius -= 1
                                self.game.make_fov_map()
                                self.redraw = True

            # --- set cursor to mouse if inside play area -----
            x, y = self.pixel_to_tile(pygame.mouse.get_pos())
            self.move_cursor_to(x, y)  # only moves if on valid tile

            # ============== draw screen =================
            # screen_without_sprites = self.screen.copy()
            # self.allgroup.clear(bgd=self.screen)

            # self.allgroup.clear(self.screen, self.spriteless_background)
            self.screen.blit(self.spriteless_background,
                             (0, 0))  # NOTICE: out-comment this line for very cool effect at goldexplosion
            self.allgroup.update(seconds)

            dirtyrects = []

            if len(self.allgroup) > 1:
                self.draw_radar()
                # self.draw_panel()  # always draw panel #über allgropu draw: münzen sichtbar,  flackert
                # append radar and panel to dirtyrects
                # dirtyrects.append(pygame.Rect(Viewer.width-Viewer.panel_width, 0, Viewer.panel_width, Viewer.height))
            self.draw_panel()  # always draw panel #unter allgropu draw: münzen unsichtbar, flackert
            dirtyrects.append(pygame.Rect(Viewer.width - Viewer.panel_width, 0, Viewer.panel_width, Viewer.height))
            dirtyrects.extend(self.allgroup.draw(self.screen))

            if self.redraw:
                # print(self.pixel_to_tile(pygame.mouse.get_pos()))
                # if self.pixel_to_tile(pygame.mouse.get_pos()) is not (None, None) and reset_cursor:

                # if reset_cursor and
                #    Game.cursor_x, Game.cursor_y = 0, 0
                # reset_cursor = True
                # delete everything on screen
                self.screen.blit(self.background, (0, 0))
                # --- order of drawing (back to front) ---
                self.draw_dungeon()

                self.draw_radar()
                dirtyrects.append((0, 0, Viewer.width, Viewer.height))
                self.draw_panel()
                self.draw_log()
                self.spriteless_background.blit(self.screen, (0, 0))

            elif len(Game.log) > log_lines:
                self.draw_log()  # always draw log
                log_lines = len(Game.log)
                dirtyrects.append((0, Viewer.height - self.log_height, Viewer.width, self.log_height))

            # dirtyrects.append((Viewer.width - self.panel_width, 0, Viewer.panel_width, Viewer.height))

            self.redraw = False
            # self.draw_panel()

            # write text below sprites
            fps_text = "FPS: {:5.3}".format(self.clock.get_fps())
            pygame.draw.rect(self.screen, (64, 255, 64), (Viewer.width - 110, Viewer.height - 20, 110, 20))
            write(self.screen, text=fps_text, origin="bottomright", x=Viewer.width - 2, y=Viewer.height - 2,
                  font_size=16, bold=True, color=(0, 0, 0))
            dirtyrects.append(pygame.Rect(Viewer.width - 110, Viewer.height - 20, 110, 20))

            # ------ Cursor -----
            self.cursor.pos = pygame.math.Vector2(self.tile_to_pixel((Game.cursor_x, Game.cursor_y), center=True))
            # self.cursor.pos += pygame.math.Vector2(Viewer.grid_size[0]//2, Viewer.grid_size[1]//2) # center on tile
            # -------- next frame -------------
            # print(dirtyrects)

            pygame.display.update(dirtyrects)
            # pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()
        print("you killed:")
        for v in self.game.player.victims:
            print(v, self.game.player.victims[v])


if __name__ == '__main__':
    g = Game(tiles_x=80, tiles_y=40)
    Viewer(g, width=1200, height=800, grid_size=(32, 32))  # , (35,35))
