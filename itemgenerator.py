import random
import os

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


#def minmax(value, lower_limit=-1, upper_limit=1):
#    """constrains a value inside two limits"""
#    value = max(lower_limit, value)
#    value = min(upper_limit, value)
#    return value


#def randomizer(list_of_chances=(1.0,)):
#    """gives back an integer depending on chance.
#       e.g. randomizer((.75, 0.15, 0.05, 0.05)) gives in 75% 0, in 15% 1, and in 5% 2 or 3"""
#    total = sum(list_of_chances)
#    v = random.random() * total  # a value between 0 and total
#    edge = 0
#    for i, c in enumerate(list_of_chances):
#        edge += c
#        if v <= edge:
#            return i
#    else:
#        raise SystemError("problem with list of chances:", list_of_chances)

def feed_list_from_file(listvar, filename):
    """takes filelname and search for this filename in the 'data' folder.
    add each line of this file to the list 'listvar' and returns listvar"""
    datafilename = os.path.join("data", filename)
    with open(datafilename) as f:
        lines = f.readlines()
    for line in lines:
        listvar.append(line.strip())
    return listvar

class Item:
    
    def __init__(self):
        
        self.item_type = random.choice(("weapon","weapon"))#"armour","accessoires","potions","scrolls","edibles"))
        
        if self.item_type == "weapon":
            self.sub_type = random.choice(("sword","axe","scepter","wand","dagger","bow"))
            bonus_damages = ["fire_bonus","cold_bonus","lightning_bonus","physical_bonus"]
            vulnerabilities = ["fire_weakness","cold_weakness","lightning_weakness"]
            
            
            
            self.rarity = megaroll("1D6")//5
            self.name = name_generator(self.item_type,self.rarity)
            #self.color = random.choice((""))
            for _ in range(self.rarity):
                amount = megaroll("1D20")//19+1
                if random.random() < 0.66:
                    bonus = random.choice(bonus_damages)
                else:
                    bonus = random.choice(vulnerabilities)
                if bonus in self.__dict__:
                    self.__dict__[bonus] += amount
                else:
                    setattr(self,bonus,amount)
            print(self.__dict__)
            
        #elif self.item_type == "armour":
        #   self.sub_type = random.choice(("helmet","plate","shoes","gloves"))
        #self.name
        #self.num_sockets
        
        
def name_generator(itemtype,rar):
	if itemtype == "weapon":
		adj = []
		subj = []
		adj = feed_list_from_file(adj, "adjectives.txt")
		subj = feed_list_from_file(subj, "weapon_nouns.txt")
		result = ""
		random.shuffle(adj)
		for a in range(megaroll("1D2")):
			result += adj[a] + " "
		result += random.choice(subj)
	if rar > 3:
		result += " of doom"
	return result
        
        

if __name__ == "__main__":
	Item()
