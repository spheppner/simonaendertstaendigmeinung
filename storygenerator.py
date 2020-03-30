import random
import os

class World:
    persons = {}

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

def story():
	x = Person()
	for n in World.persons.values():
            print(n.history())
  
class Person:

    number = 0
    
    
    def __init__(self):
        """creates a person with full history"""
        self.number = Person.number
        Person.number += 1
        World.persons[self.number] = self
        self.text = ""
        self.gender = random.choice(("male","female","trans"))
        self.birth_year = random.randint(2020,2099)
        self.place_of_birth = random.choice(("Vienna", "Munich", "Berlin"))
        self.youth = random.choice(("student", "worker", "unemployed"))
        self.job = random.choice(("office clerk", "salesman", "doctor"))
        self.marriages = set() # numbers only !
        self.hobbies = random.choice(("watching tv", "annoying people", "painting walls"))
        self.children = set() # only numbers!
        self.friends = set()  # only numbers !
        self.foes = set()  # only number!
        self.ideology = random.choice(("conservative", "liberal", "ecological", "socialist", "communist", "anarchist", "religious", "uninterested"))
        self.get_friends()
        self.get_married()
        ##elf.get_children()
        
    def get_friends(self):
        """friends must have: different number, age-difference +- 10 at max. """
        for _ in range(megaroll("1d6")-1):
            candidates = [p for p in World.persons.values() if p.number != self.number and abs(p.birth_year - self.birth_year) < 11 and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number not in self.marriages]
            if len(candidates) == 0:
                continue
            x = random.choice(candidates).number
            self.friends.add(x)
            # gegenseitige Freundschaft:
            World.persons[x].friends.add(self.number)
            
    def get_married(self):
        """married people must have: different number, age-difference +- 5 at max. """
        for _ in range(megaroll("1d3")-1):
            candidates = [p for p in World.persons.values() if p.number != self.number and abs(p.birth_year - self.birth_year) < 6 and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number not in self.marriages and p.gender != self.gender and self.birth_year < 2082]
            if len(candidates) == 0:
                continue
            x = random.choice(candidates).number
            self.marriages.add(x)
            # gegenseitige Heirat:
            World.persons[x].marriages.add(self.number)
            
    def get_children(self):
        """children only from married couple (including ex), children for both parents! children at least 20 years younger"""
        if len(self.marriages) == 0:
            return
        #for _ in range(megaroll("1D3")-1):
        #    partner = World.persons[random.choice(self.marriages)]
            #candidates = [p for p in World.persons.values() if p.number != self.number and p.number not in self.marriages and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number and p.birth_year > self.birth_year+20 and p.birth_year > partner.birth_year + 20]
                        
            
        #    x = random.choice(candidates).number
        #    self.children.add(x)

    def history(self):
        return self.__dict__

  
  

if __name__ == "__main__":

    story()
