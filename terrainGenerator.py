import random

legend = {".": {"name": "floor",
                "prob": None,
                "max": None,
                "character": ".",
                "num": 0},
          "*": {"name": "coin",
                "prob": 0.05,
                "max": None,
                "character": "*",
                "num": 0},
          "#": {"name": "rock",
                "prob": 0.2,
                "max": 30,
                "character": "#",
                "num": 0},             
          "<": {"name": "stair up",
                "prob": 0.05,
                "max": 2,
                "character": "<",
                "num": 0},
          ">": {"name": "stair down",
                "prob": 0.05,
                "max": 2,
                "character": ">",
                "num": 0},
          "$": {"name": "Shop",
                "prob": 0.4,
                "max": 1,
                "character": "$",
                "num": 0},
          #"T": {"name": "Tree",
          #      "prob": "None",
          #      "max": "None",
          #      "character": "T",
          #      "num": 0}
          }
          
maxlines = 40
maxchars = 60
dmap = []

maxpebbles = legend["."]["max"]
maxcoins = legend["*"]["max"]
maxrocks = legend["#"]["max"]
maxstairsup = legend["<"]["max"]
maxstairsdown = legend[">"]["max"]
maxshops = legend["$"]["max"]
#maxtrees = legend["T"]["max"]

pebble_prob = legend["."]["prob"]
coin_prob = legend["*"]["prob"]
rock_prob = legend["#"]["prob"]
stairup_prob = legend["<"]["prob"]
stairdown_prob = legend[">"]["prob"]
shop_prob = legend["$"]["prob"]
#tree_prob = legend["T"]["prob"]

pebble_character = legend["."]["character"]
coin_character = legend["*"]["character"]
rock_character = legend["#"]["character"]
stairup_character = legend["<"]["character"]
stairdown_character = legend[">"]["character"]
shop_character = legend["$"]["character"]
#tree_character = legend["T"]["character"]

def snake(dungeon,room_num,maxnum_room,snakenum):
    maxrooms = maxnum_room
    room_nr = room_num
    rt = 1
    dmap = dungeon
    rooms = []
    y = random.randint(1, maxlines-1)
    for x in range(snakenum):
        for x in range(1, maxchars-1):
            dmap[y][x] = pebble_character
            z = random.random()
            if z < 0.5:
                # i want to go deeper
                howmuch = random.randint(1, 7)
                if y + howmuch < maxlines-2:
                    for _ in range(howmuch):
                        y += 1
                        dmap[y][x] = pebble_character
            #elif z < 0.5:
            else:
                # i want to go higher
                howmuch = random.randint(1, 7)
                if y - howmuch > 1:
                    for _ in range(howmuch):
                        y -= 1
                        dmap[y][x] = pebble_character
            # ---- new room? ----
            if rt == 1:
                rt = 0
                room_nr += 1
                maxbreite = maxchars-2 - x
                b = min(random.randint(3, 15), maxbreite)
                maxtiefe = maxlines-2 - y
                h = min(random.randint(2, 10), maxtiefe)
                rooms.append((x, y, b, h))
            elif random.random() < 0.1 and room_nr < maxrooms:
                room_nr += 1
                maxbreite = maxchars-2 - x
                b = min(random.randint(3, 15), maxbreite)
                maxtiefe = maxlines-2 - y
                h = min(random.randint(2, 10), maxtiefe)
                rooms.append((x, y, b, h))
    return dmap,rooms,room_nr

def cave(dig_type="snake"):
    maxrooms = 5
    rooms = []
    dmap = []
    
    room_nr = 0

    for y, line in enumerate(range(maxlines)):
        l = []
        for x, char in enumerate(range(maxchars)):
            l.append(random.choice((rock_character)))
        dmap.append(l)
        
    if dig_type == "snake":
        dmap,rooms,room_nr = snake(dmap,room_nr,maxrooms,2)

    for r in rooms:
        x1 , y1, b, h = r
        for y, line in enumerate(dmap):
            for x, char in enumerate(line):
                if y >= y1 and y <= y1+h and x >= x1 and x <= x1+ b:
                    dmap[y][x] = "."     
                    if random.random() < rock_prob:
                        if legend["#"]["num"] < maxrocks and y > y1 and y < y1+ h and x > x1 and x < x1+b:
                            legend["#"]["num"] += 1
                            dmap[y][x] = rock_character
    
    pebbles = []
    for y, line in enumerate(dmap):
        for x, char in enumerate(line):
            if dmap[y][x] == pebble_character:
                pebbles.append((x,y))
    max_pebbles = len(pebbles)
    
    walls = []
    for y, line in enumerate(dmap):
        for x, char in enumerate(line):
            if dmap[y][x] == rock_character:
                walls.append((x, y))
    max_walls = len(walls)

    # ---- Coins ----
    
    random.shuffle(pebbles)
    n = 0
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < coin_prob:
            dmap[y][x] = coin_character

    # ---- Treppen ----

    random.shuffle(pebbles)
    n = 0
    x = pebbles[n][0]
    y = pebbles[n][1]
    dmap[y][x] = stairdown_character
    print(maxstairsdown)
    print(maxstairsup)
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < stairdown_prob and legend[">"]["num"] < maxstairsdown-1:
            dmap[y][x] = stairdown_character
            legend[">"]["num"] += 1 
            print(legend[">"]["num"]) 
    random.shuffle(pebbles)
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < stairup_prob and legend["<"]["num"] < maxstairsup:
            dmap[y][x] = stairup_character
            legend["<"]["num"] += 1
    
    # ---- Shop ----
    
    random.shuffle(pebbles)
    n = 0
    x = pebbles[n][0]
    y = pebbles[n][1]
    if random.random() < shop_prob and legend["$"]["num"] < maxshops:
        dmap[y][x] = shop_character
        legend["$"]["num"] += 1
        
    return dmap

def start(filename="data/level002.txt"):
    dmap = cave()
    
    # ---- dungeon printer ----
    
    with open(filename, "w") as f:
        for l in dmap:
            for char in l:
                print(char, end="")
                f.write(char)
            print()
            f.write("\n")    
        
if __name__ == "__main__":
    start()
