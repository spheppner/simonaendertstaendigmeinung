# simon@heppner.at
"""
Author: Simon HEPPNER
Email: simon@heppner.at
Github: github.com/spheppner
Version: 001
"""

import pygame
import random
import os


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
    panel_width = 208
    log_height = 0
    grid_size = (32, 32)
    pcx = 0  # player x coordinate in pixel
    pcy = 0  # player y coordinate in pixel

    def __init__(self, width=640, height=400, grid_size=(32, 32), fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        # self.game = game
        self.fps = fps
        # position in pixel where all the gold sprites are flying to:
        Viewer.grid_size = grid_size  # make global readable
        Viewer.width = width
        Viewer.height = height
        self.cursor_x = 0
        self.cursor_y = 0

        pygame.init()
        # player center in pixel
        Viewer.pcx = (width - Viewer.panel_width) // 2  # set player in the middle of the screen
        Viewer.pcy = (height - Viewer.log_height) // 2
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self.playtime = 0.0
        # ------ surfaces for radar, panel and log ----
        # all surfaces are black by default
        self.panelscreen = pygame.surface.Surface((Viewer.panel_width, Viewer.height))# - Viewer.panel_width))
        self.panelscreen.fill((64, 128, 64))
        self.panelscreen0 = pygame.surface.Surface((Viewer.panel_width, Viewer.height))# - Viewer.panel_width))
        self.panelscreen0.fill((64, 128, 64))
        self.logscreen = pygame.surface.Surface((Viewer.width - Viewer.panel_width, Viewer.log_height))

        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.make_background()
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        # ------ create bitmaps for player and dungeon tiles ----
        self.prepare_spritegroups()
        self.cursor = CursorSprite(pos=pygame.math.Vector2(Viewer.grid_size[0] // 2, Viewer.grid_size[
            1] // 2))  # pos=pygame.math.Vector2(x=Viewer.pcx, y=Viewer.pcy))
        self.create_map()
        self.run()


    def create_map(self, xtiles= 40, ytiles= 40):
        """creates a 2d array to be later represented by graphical tiles.
        the 'map' 2d array is just a nested list of chars
        each char represent a graphical tile"""
        self.map = [["." for x in range(xtiles)] for y in range(ytiles)] # create a nested list
        # set some random tiles:
        for y, line in enumerate(self.map):
            for x, char in enumerate(line):
                self.map[y][x] = random.choice((".",".",".",".",".",".","a","a","a","b","b","c"))





    def prepare_spritegroups(self):
        self.allgroup = pygame.sprite.LayeredUpdates()  # for drawing
        self.whole_screen_group = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.Group()
        self.cursorgroup = pygame.sprite.Group()

        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        CursorSprite.groups = self.allgroup

    def pixel_to_tile(self, pixelcoordinate):
        """transform pixelcoordinate (x,y, from pygame mouse) into grid tile coordinate."""
        #   returns  distance to player tile in tiles (relative coordinates)"""
        x, y = pixelcoordinate
        # return (x - self.pcx) // Viewer.grid_size[0], (y - self.pcy) // Viewer.grid_size[1]
        return x // Viewer.grid_size[0], y // Viewer.grid_size[1]

    def draw_panel(self):
        self.panelscreen.blit(self.panelscreen0, (0, 0))
        write(self.panelscreen, text="cursor x:{} y:{} (pixel)".format(self.cursor.pos.x, self.cursor.pos.y), x=5, y=5,
              color=(255, 255, 255), font_size=12)
        write(self.panelscreen, text="cursor x:{} y:{} (tiles)".format(
            self.cursor.pos.x // Viewer.grid_size[0], self.cursor.pos.y // Viewer.grid_size[1]), x=5, y=25,
              color=(255, 255, 255), font_size=12)
        # - hitpoint bar in red, starting left
        # pygame.draw.rect(self.panelscreen, (200, 0, 0),
        #                 (0, 35, self.game.player.hitpoints * Viewer.panel_width / self.game.player.hitpoints_max, 28))
        # -y35--------------------

        # blit panelscreen
        self.screen.blit(self.panelscreen, (Viewer.width - self.panel_width, 0))

    @staticmethod
    def tile_to_pixel(pos, center=False):
        """get a tile coordinate (x,y) and returns pixel (x,y) of tile
           if center is True, returns the center of the tile,
           if center is False, returns the upper left corner of the tile"""
        x, y = pos
        # x2 = Viewer.pcx + (x - Game.player.x) * Viewer.grid_size[0]
        # y2 = Viewer.pcy + (y - Game.player.y) * Viewer.grid_size[1]
        x2 = Viewer.pcx + (x + 1000) * Viewer.grid_size[0]
        y2 = Viewer.pcy + (y + 1000) * Viewer.grid_size[1]
        if center:
            x2 += Viewer.grid_size[0] // 2
            y2 += Viewer.grid_size[1] // 2
        # print(x2, y2)
        return (x2, y2)

    # def load_images(self):
    #     """single images. char looks to the right by default?"""
    # self.images["arch-mage-attack"] = pygame.image.load(
    #    os.path.join("data", "arch-mage-attack.png")).convert_alpha()

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

    def move_cursor_to(self, x, y):
        """moves the cursor to tiles xy, """

        x = self.pcx + x * self.grid_size[0]
        y = self.pcy + y * self.grid_size[1]
        if x < 0 or y < 0 or x > (self.width - self.panel_width) or y > (self.height - self.log_height):
            # print("mouse outside game panel", x, y)
            return  # cursor can not move outside of the game window
        #
        # ---- finally, move the cursor ---
        self.cursor_x = x
        self.cursor_y = y
        # self.screen.blit(self.background, (0, 0))

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

    def draw_grid(self, color=(200, 200, 200)):
        """draws lines according to Viewer.grid_size"""
        for y in range(0, Viewer.height, Viewer.grid_size[1]):
            pygame.draw.line(self.screen, color, (0, y), (Viewer.width - Viewer.panel_width, y), 1)
        for x in range(0, Viewer.width - Viewer.panel_width, Viewer.grid_size[0]):
            pygame.draw.line(self.screen, color, (x, 0), (x, Viewer.height), 1)

    def draw_map_tiles(self):
        # blit (the visible tile of) self.map on the screen
        legend = {"." : (32,32,32),
                  "a" : (128,255,0),
                  "b" : (128,0,255),
                  "c" : (0,255,255)
                  }
        for y, line in enumerate(self.map):
            for x, char in enumerate(line):
                #print("legend:", self.map[y][x])
                pygame.draw.rect(self.screen, legend[self.map[y][x]],(x*Viewer.grid_size[0], y*Viewer.grid_size[1],
                                  Viewer.grid_size[0],Viewer.grid_size[1]) )

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(True)
        oldleft, oldmiddle, oldright = False, False, False

        self.redraw = True
        # exittime = 0
        self.spriteless_background = pygame.Surface((Viewer.width - Viewer.panel_width, Viewer.height))

        self.screen.blit(self.spriteless_background, (0, 0))
        ###    pygame.display.flip()
        # log_lines = len(Game.log)
        while running:

            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000

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
                    if event.key == pygame.K_a:
                        self.cursor.pos.x -= self.grid_size[0]
                    if event.key == pygame.K_d:
                        self.cursor.pos.x += self.grid_size[0]
                    if event.key == pygame.K_w:
                        self.cursor.pos.y -= self.grid_size[1]
                    if event.key == pygame.K_s:
                        self.cursor.pos.y += self.grid_size[1]
                        # self.redraw = True
                    #    reset_cursor = False
                    # Game.cursor_x -= 1

                    # ----------- magic with ctrl key and dynamic key -----
                    # if pressed_keys[pygame.K_RCTRL] or pressed_keys[pygame.K_LCTRL]:
                    # if event.mod & pygame.KMOD_CTRL:  # any or both ctrl keys are pressed

                    #    key = pygame.key.name(event.key)  # name of event key: a, b, c etc.

            # --- set cursor to mouse if inside play area -----
            mousepos = pygame.mouse.get_pos()
            if mousepos[0] < Viewer.width - Viewer.panel_width:
                x, y = self.pixel_to_tile(pygame.mouse.get_pos())
                print(x, y)
                self.cursor.pos = pygame.math.Vector2(x * Viewer.grid_size[0] + Viewer.grid_size[0] // 2,
                                                      y * Viewer.grid_size[1] + Viewer.grid_size[1] // 2)
            # self.move_cursor_to(x, y)  # only moves if on valid tile

            # ============== draw screen =================
            # screen_without_sprites = self.screen.copy()
            # self.allgroup.clear(bgd=self.screen)

            # self.allgroup.clear(self.screen, self.spriteless_background)
            # self.screen.blit(self.spriteless_background,
            #                 (0, 0))  # NOTICE: out-comment this line for very cool effect at goldexplosion

            self.screen.blit(self.background, (0, 0))

            self.draw_map_tiles()
            self.draw_grid()
            self.allgroup.update(seconds)
            # ------ Cursor -----
            # self.cursor.pos = pygame.math.Vector2(self.tile_to_pixel((self.cursor_x, self.cursor_y), center=True))
            self.allgroup.draw(self.screen)

            # dirtyrects = []

            self.draw_panel()  # always draw panel #unter allgropu draw: münzen unsichtbar, flackert
            # dirtyrects.append(pygame.Rect(Viewer.width - Viewer.panel_width, 0, Viewer.panel_width, Viewer.height))

            # write text below sprites
            fps_text = "FPS: {:5.3}".format(self.clock.get_fps())
            pygame.draw.rect(self.screen, (64, 255, 64), (Viewer.width - 110, Viewer.height - 20, 110, 20))
            write(self.screen, text=fps_text, origin="bottomright", x=Viewer.width - 2, y=Viewer.height - 2,
                  font_size=16, bold=True, color=(0, 0, 0))

            # self.cursor.pos += pygame.math.Vector2(Viewer.grid_size[0]//2, Viewer.grid_size[1]//2) # center on tile
            # -------- next frame -------------
            # print(dirtyrects)

            pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == '__main__':
    # g = Game(tiles_x=80, tiles_y=40)
    Viewer(width=1168, height=768, grid_size=(64, 64))  # , (35,35))
