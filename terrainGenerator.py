import random

legend = {".": {"name": "floor",
                    "prob": None,
                    "max": None,
                    "character": "."},
          "*": {"name": "coin",
                "prob": 0.05,
                "max": None,
                "character": "*"},
          "#": {"name": "rock",
                "prob": 0.2,
                "max": 30,
                "character": "#"},             
          #"s": {"name": "strong rock",
          #      "prob": 0.4,
          #      "max": None,
          #      "character": "s"},
          #"g": {"name": "gold rock",
          #      "prob": 0.025,
          #      "max": None,
          #      "character": "g"},
          "<": {"name": "stair up",
                "prob": 0.05,
                "max": None,
                "character": "<"},
          ">": {"name": "stair down",
                "prob": 0.05,
                "max": None,
                "character": ">"}
          #"@": {"name": "Player",
          #      "prob": None,
          #      "max": 1,
          #      "character": "@"},
          #"monster": {"name": None,
          #            "prob": None,
          #            "max": 15,
          #            "character": None},
          #"1": {"name": "Monster1",
          #      "prob": 0.8,
          #      "max": None,
          #      "character": "1"},
          #"2": {"name": "Monster2",
          #      "prob": 0.6,
          #      "max": None,
          #      "character": "2"},
          #"3": {"name": "Monster3",
          #      "prob": 0.55,
          #      "max": None,
          #      "character": "3"},
          #"4": {"name": "Monster4",
          #      "prob": 0.5,
          #      "max": None,
          #      "character": "4"},
          #"S": {"name": "Shop",
          #      "prob": 0.3,
          #      "max": 1,
          #      "character": "S"},
          #"J": {"name": "Invisible Wall",
          #      "prob": None,
          #      "max": None,
          #      "character": "J"},
          #"O": {"name": "Invisible Coin",
          #      "prob": None,
          #      "max": None,
          #      "character": "O"}
          }
maxlines = 40
maxchars = 60
dmap = []

maxpebbles = legend["."]["max"]
maxcoins = legend["*"]["max"]
maxrocks = legend["#"]["max"]
#maxsrocks = legend["s"]["max"]
#maxgoldrocks = legend["g"]["max"]
maxstairsup = legend["<"]["max"]
maxstairsdown = legend[">"]["max"]
#maxshops = legend["S"]["max"]
#maxmonster = legend["monster"]["max"]
#maxinvisible = legend["J"]["max"]
#maxicoin = legend["O"]["max"]

pebble_prob = legend["."]["prob"]
coin_prob = legend["*"]["prob"]
rock_prob = legend["#"]["prob"]
#srock_prob = legend["s"]["prob"]
#goldrock_prob = legend["g"]["prob"]
stairup_prob = legend["<"]["prob"]
stairdown_prob = legend[">"]["prob"]
#shop_prob = legend["S"]["prob"]
#monster1_prob = legend["1"]["prob"]
#monster2_prob = legend["2"]["prob"]
#monster3_prob = legend["3"]["prob"]
#monster4_prob = legend["4"]["prob"]
#invisible_prob = legend["J"]["prob"]
#icoin_prob = legend["O"]["prob"]

pebble_character = legend["."]["character"]
coin_character = legend["*"]["character"]
rock_character = legend["#"]["character"]
#srock_character = legend["s"]["character"]
#goldrock_character = legend["g"]["character"]
stairup_character = legend["<"]["character"]
stairdown_character = legend[">"]["character"]
#player_character = legend["@"]["character"]
#shop_character = legend["S"]["character"]
#monster1_character = legend["1"]["character"]
#monster2_character = legend["2"]["character"]
#monster3_character = legend["3"]["character"]
#monster4_character = legend["4"]["character"]
#invisible_character = legend["J"]["character"]
#icoin_character = legend["O"]["character"]

def snakes(dungeon,room_num,maxnum_room):
    maxrooms = maxnum_room
    room_nr = room_num
    rt = 1
    dmap = dungeon
    rooms = []
    y = random.randint(1, maxlines-1)
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

    # --- snake2 ---

    for x in range(1, maxchars-1):
        dmap[y][x] = pebble_character
        if random.random() > 0.5:
            # i want to go deeper
            howmuch = random.randint(1, 7)
            if y + howmuch < maxlines-2:
                for _ in range(howmuch):
                    y += 1
                    dmap[y][x] = pebble_character
        elif random.random() < 0.5:
            # i want to go higher
            howmuch = random.randint(1, 7)
            if y - howmuch > 1:
                for _ in range(howmuch):
                    y -= 1
                    dmap[y][x] = pebble_character
        # ---- new room? ----
        elif rt == 1:
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
       

def cave():
    maxrooms = 5
    rooms = []
    dmap = []
    
    room_nr = 0
    rock_nr = 0

    for y, line in enumerate(range(maxlines)):
        l = []
        #if line == 0 or line == 1 or line == 2 or line == 3 or line == 4 or line == 5 or line == 6 or line == 7 or line == 8 or line == 9:
        for x, char in enumerate(range(maxchars)):
            #if x == 0 or x == maxchars-1 or y == 0 or y == maxlines-1:
            #    l.append(srock_character)
            #l.append(random.choice(list(legend.keys())))
            l.append(random.choice((rock_character)))
        dmap.append(l)
        

    dmap,rooms,room_nr = snakes(dmap,room_nr,maxrooms)

    for r in rooms:
        x1 , y1, b, h = r
        for y, line in enumerate(dmap):
            for x, char in enumerate(line):
                if y >= y1 and y <= y1+h and x >= x1 and x <= x1+ b:
                    dmap[y][x] = "."     
    #                if ft == 1:
    #                    ft = 0
    #                    dmap[y][x] = "<"     
    #                elif random.random() < stairdown_prob and stair_nr < maxstairs:
    #                    stair_nr += 1
    #                    dmap[y][x] = "<"
    #                elif et == 1:
    #                    et = 0
    #                    dmap[y][x] = ">"
    #                elif random.random() < stairup_prob and stair_nr < maxstairs:
    #                    stair_nr += 1
    #                    dmap[y][x] = ">"
                    if random.random() < rock_prob:
                        if rock_nr < maxrocks and y > y1 and y < y1+ h and x > x1 and x < x1+b:
                            rock_nr += 1
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

    # coinschleife
    
    random.shuffle(pebbles)
    n = 0
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < coin_prob:
            dmap[y][x] = coin_character

    # treppenschleife

    random.shuffle(pebbles)
    n = 0
    x = pebbles[n][0]
    y = pebbles[n][1]
    dmap[y][x] = stairdown_character

    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < stairdown_prob:
            dmap[y][x] = stairdown_character
    for n in range(1, random.randint(1, max_pebbles//4)):
        x = pebbles[n][0]
        y = pebbles[n][1]
        if random.random() < stairup_prob:
            dmap[y][x] = stairup_character
    
    # steinschleifen
    
    #random.shuffle(walls)
    #for n in range(0, random.randint(1, max_walls//4)):
    #    x = walls[n][0]
    #    y = walls[n][1]
    #    if random.random() < srock_prob:
    #        dmap[y][x] = srock_character
    #    elif random.random() < goldrock_prob:
    #        dmap[y][x] = goldrock_character
    
    # secrect treasure room ?
    #for v in range(50):
    #    cy = random.randint(5, maxlines-5)
    #    cx = random.randint(5, maxchars-5)
    #    goodcenter = True
    #    for dx in (-2,-1,0,1,2):
    #        for dy in (-2,-1,0,1,2):
    #            if dmap[cy+dy][cx+dx] not in "#sg":
    #                goodcenter = False
    #                
    #                # tile is a rock
    #    
    #    if goodcenter:
    #        # paint secret room wall
    #        for dx in (-2,-1,0,1,2):
    #            for dy in (-2,-1,0,1,2):
    #                if (dx == -2 and dy == -2) or (dx == -2 and dy == 2) or (dx == 2 and dy == -2) or (dx == 2 and dy == 2):
    #                    pass # corner should be normal wall
    #                else:
    #                    dmap[cy+dy][cx+dx] = invisible_character
    #        # paint secrent room treasure
    #        for dx in (-1,0,1):
    #            for dy in (-1,0,1):
    #                dmap[cy+dy][cx+dx] = icoin_character
    #        break
            
        
    
    # monsterschleifen
    
    #random.shuffle(pebbles)
    #for n in range(0, random.randint(1, maxmonster)):
    #    x = pebbles[n][0]
    #    y = pebbles[n][1]
    #    if random.random() < monster1_prob:
    #        dmap[y][x] = monster1_character
    #    elif random.random() < monster2_prob:
    #        dmap[y][x] = monster2_character
    #    elif random.random() < monster3_prob:
    #        dmap[y][x] = monster3_character
    #    elif random.random() < monster4_prob:
    #        dmap[y][x] = monster4_character
    
    # player generiert

    #random.shuffle(pebbles)
    #n = 0
    #x = pebbles[n][0]
    #y = pebbles[n][1]
    #dmap[y][x] = player_character
   # 
   # # shop generiert
   # 
   # random.shuffle(pebbles)
   # n = 0
   # x = pebbles[n][0]
    #y = pebbles[n][1]
    #if sps == 1:
    #    if random.random() < shop_prob:
    #        print("Erfolg!")
    #        sps = 0
    #        dmap[y][x] = shop_character
    

    # ---- dungeon printer ----

    with open("data/level002.txt", "w") as f:
        for l in dmap:
            for char in l:
                print(char, end="")
                f.write(char)
            print()
            f.write("\n")    
        #print(rooms)
def start():
    cave()
    
        
if __name__ == "__main__":
    start()
