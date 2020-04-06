import random
import os


class World:
    persons = {}
    first_names_male = []
    first_names_female = []
    last_names = []

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


# def minmax(value, lower_limit=-1, upper_limit=1):
#    """constrains a value inside two limits"""
#    value = max(lower_limit, value)
#    value = min(upper_limit, value)
#    return value


# def randomizer(list_of_chances=(1.0,)):
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
    print("feeding names list...")
    feed_list_from_file(World.last_names, "surnames.txt")
    feed_list_from_file(   World.first_names_male, "male_firstnames.txt")
    feed_list_from_file(World.first_names_female, "female_firstnames.txt")
    print(World.last_names)


    for _ in range(5):
        x = Person(min_age=20, max_age=25, year=2020)  ## adam und eva *2.5
    for year in range(1921, 2099):
        # for n in World.persons.values()
        for n in [p for p in World.persons.values()]:
            n.update(year)
        for n in World.persons.values():
            if n.update_year is None or n.update_year != year:
                n.update(year)
    for n in World.persons.values():
        n.print_history()


class Person:
    number = 0

    def __init__(self, year, min_age=0, max_age=95, last_name = None, immigrant=True):
        """creates a person with full history"""
        self.number = Person.number
        Person.number += 1
        World.persons[self.number] = self
        self.text = ""
        self.last_name = last_name if last_name is not None else random.choice(World.last_names)
        self.gender = random.choice(("male", "female"))
        self.first_name = random.choice(World.first_names_male if self.gender == "male" else World.first_names_female)

        # self.year = year
        self.birth_year = year - random.randint(min_age, max_age)

        # self.place_of_birth = random.choice(("Vienna", "Munich", "Berlin"))
        self.youth = random.choice(("student", "worker", "unemployed"))
        self.job = random.choice(("office clerk", "salesman", "doctor"))
        self.married = None  # numbers only !
        self.ex_partners = []
        self.hobbies = random.choice(("watching tv", "annoying people", "painting walls"))
        self.children = []  # only numbers!
        self.friends = []  # only numbers !
        self.foes = []  # only number!
        self.ideology = random.choice(("conservative", "liberal", "ecological", "socialist", "communist", "anarchist",
                                       "religious", "uninterested"))
        # self.get_friends()
        # self.get_married()
        self.history = [str(self.number) + "====== "+ "arriving in city" if immigrant else "born here" +" with those attributes:" + str(self.__dict__)]
        # self.get_children()
        self.update_year = None

    def update(self, year):
        text = "year {}: ".format(year)
        if self.married is None:
            # chance to find partner
            if random.random() < 0.15:
                spouse = self.get_married(year)
                if spouse is None:
                    text += "tried very hard but failed to marry someone"
                else:
                    text += "suscessfully married to {}!".format(self.married)
        # chance to find new friend
        if random.random() < 0.1:
            newfriend = self.get_friends(year)
            if newfriend is None:
                text += "tried to start a friendship but failed."
            else:
                text += " Becomes friend with {}.".format(newfriend)

        # chance to loose friend
        if len(self.friends) > 0 and random.random() < 0.05:
            exfriend = random.choice(self.friends)
            self.friends.remove(exfriend)
            ## TODO becomes foe ?
            text += " Ends friendship with {}.".format(exfriend)

            World.persons[exfriend].friends.remove(self.number)
            World.persons[exfriend].history.append("{}: Looses friendship with {}".format(year, self.number))

        # chance to get baby
        self.get_children(year)

        self.history.append(text)
        self.update_year = year

    def get_friends(self, year):
        """friends must have: different number, age-difference +- 10 at max. """

        candidates = [p for p in World.persons.values() if p.number != self.number and abs(
            p.birth_year - self.birth_year) < 11 and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number != self.married and self.birth_year < year - 5]
        if len(candidates) == 0:
            return None
        x = random.choice(candidates).number
        self.friends.append(x)
        # gegenseitige Freundschaft:
        World.persons[x].friends.append(self.number)
        World.persons[x].history.append("{}: Accepted friendship request of {} ".format(year, self.number))
        return x

    def get_married(self, year):
        """married people must have: different number, age-difference +- 10 at max. """

        candidates = [p for p in World.persons.values() if p.married is None and p.number != self.number and abs(
            p.birth_year - self.birth_year) < 16 and p.number not in self.foes and p.number not in self.children and p.gender != self.gender and p.birth_year < year - 20]
        if len(candidates) == 0:
            return None
        x = random.choice(candidates).number
        self.married = x
        # take name of partner
        self.last_name = World.persons[x].last_name
        # remove spouse of friendlist to avoid becoming ex-friend
        if x in self.friends:
            self.friends.remove(x)
        if self.number in World.persons[x].friends:
            World.persons[x].friends.remove(self.number)
        # self.marriages.add(x)
        # gegenseitige Heirat:
        World.persons[x].married = self.number
        World.persons[x].history.append("{}: Gracefully accepted marriage proposal of {} ".format(year, self.number))
        # little chance that both choose a comlete new name
        if random.random() < 0.15:
            new_name = random.choice(World.last_names)
            self.last_name = new_name
            World.persons[x].last_name = new_name
            self.history.append("year {}: The marriaged couple choose for both the new family name {}".format(year, new_name))
        return x

    def get_children(self, year):
        """children only from married couple (including ex), children for both parents! children at least 20 years younger"""

        if self.married is not None:
            children = len(self.children)
            p = 1 / (3 + children)
            if random.random() < p:
                # NEUER MENSCH BABABABY
                baby = Person(year, min_age=0, max_age=0, last_name=self.last_name, immigrant=False)
                self.children.append(baby.number)
                World.persons[self.married].children.append(baby.number)
                self.history.append("{}: Got a baby: {}".format(year, baby.number))
                World.persons[self.married].history.append("{}: Got a baby: {}".format(year, baby.number))

        # if len(self.marriages) == 0:
        #    return
        # for _ in range(megaroll("1D3")-1):
        #    partner = World.persons[random.choice(self.marriages)]
        # candidates = [p for p in World.persons.values() if p.number != self.number and p.number not in self.marriages and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number  and p.birth_year > self.birth_year+20 and p.birth_year > partner.birth_year + 20]

        #    x = random.choice(candidates).number
        #    self.children.add(x)

    def print_history(self):
        for line in self.history:
            print(line)


if __name__ == "__main__":
    story()
