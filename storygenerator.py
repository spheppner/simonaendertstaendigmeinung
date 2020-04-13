import random
import os

## TODO: Criminality from other factors, Actual game: mehrere varianten, Divorce

#  File "storygenerator.py", line 434, in <module>
#    story()
#  File "storygenerator.py", line 136, in story
#    n.update(year)
#  File "storygenerator.py", line 325, in update
#    World.persons[friend].friends.remove(px.number)
#ValueError: list.remove(x): x not in list

class World:
    persons = {}
    first_names_male = []
    first_names_female = []
    last_names = []
    radiation_level = 0 # how radiated the world is - how bad the people are. (moralic mutation)
    # --- 0: neutral mixed, 1: bad wins over neutral, 2: bad wins over good, 3: bad wins over good and neutral

def create_genes():
    """ Creates a list of three genes, each genes can be either good, neutral or bad (g, n, b)"""
    genom = []
    for _ in range(10):
        genom.append(random.choice((0.0, 0.5, 0.5, 1.0)))
    return genom

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
    feed_list_from_file(World.first_names_male, "male_firstnames.txt")
    feed_list_from_file(World.first_names_female, "female_firstnames.txt")

    for nr in range(15):
        x = Person(min_age=0, max_age=25, year=2000, gender="male" if nr % 2 == 0 else "female")  ## adam und eva *2.5
    for year in range(2000, 2100):
        # for n in World.persons.values()

        for n in [p for p in World.persons.values()]:
            n.update(year)
        for n in [p for p in World.persons.values()]:
            if n.update_year is None or n.update_year != year:
                n.update(year)
        print(year, len([p for p in World.persons.values() if p.death_year is None]), len([p for p in World.persons.values() if p.death_year is None and p.married is not None]))
        print(World.persons.keys())
        print(sum([sum(p.genom)/10 for p in World.persons.values() if p.death_year is None])/len([p for p in World.persons.values() if p.death_year is None]))
        #command = input(">>> ")
        #if command == "":
        #    continue
        #try:
        #    number = int(command)
        #except:
        #    print("Could not interpret number")
        #    continue
        #print(World.persons[number].history)
        #input("Press Enter!")

    #names = {}
    #for n in World.persons.values():
    #    if n.last_name in names:
    #        names[n.last_name] += 1
    #    else:
    #        names[n.last_name] = 1
    #print(names)

    #    n.print_history()

class Person:
    number = 0

    def __init__(self, year, min_age=0, max_age=95, last_name = None, immigrant=True, gender=None):
        """creates a person with full history"""
        self.number = Person.number
        Person.number += 1
        World.persons[self.number] = self
        self.text = ""
        self.last_name = last_name if last_name is not None else random.choice(World.last_names)
        self.gender = random.choice(("male", "female")) if gender is None else gender
        self.first_name = random.choice(World.first_names_male if self.gender == "male" else World.first_names_female)
        self.probability_of_death = 0.0001

        self.death_year = None
        self.birth_year = year - random.randint(min_age, max_age)
        self.marriage_year = None

        if self.birth_year < year:
            age = year-self.birth_year
            for i in range(age):
                if i % 8 == 0:
                    self.probability_of_death *= 2

        # self.place_of_birth = random.choice(("Vienna", "Munich", "Berlin"))
        self.youth = random.choice(("student", "worker", "unemployed"))
        self.job = random.choice(("office clerk", "salesman", "doctor"))
        self.married = None  # numbers only !
        self.hobbies = random.choice(("watching tv", "annoying people", "painting walls"))
        self.children = []  # only numbers!
        self.friends = []  # only numbers !
        self.foes = []  # only number!
        self.ideology = random.choice(("conservative", "liberal", "ecological", "socialist", "communist", "anarchist",
                                       "religious", "uninterested"))
        # self.get_friends()
        # self.get_married()
        text = str(self.number) + "====== "+ "arriving in city" if immigrant else "born here"
        self.history = [(text + " with those attributes:" + str(self.__dict__))]
        # self.get_children()
        self.update_year = None

        parents = self.get_parents()
        print(parents)

        if len(parents) != 2:
            print("Random Genes: ", end="")
            self.genom = create_genes()
        else:
            self.genom = []
            genom_papa = World.persons[parents[0]].genom
            genom_mama = World.persons[parents[1]].genom
            if len(genom_papa) != len(genom_mama):
                raise Exception("Genom length unequal")
                # TODO: handle case
            for x in range(len(genom_papa)):
                if World.radiation_level == 0:
                    # ---- Mixing genes -> Equal Chance ----
                    source = random.choice((0,1))
                    self.genom.append(World.persons[parents[source]].genom[x])
                elif World.radiation_level == 1:
                    # ---- Mixing genes -> Bad wins over neutral ----
                    if (genom_papa[x] == 0.0 and genom_mama[x] == 0.5) or (genom_mama[x] == 0.0 and genom_papa[x] == 0.5):
                        self.genom.append(0.0)
                    else:
                        source = random.choice((0,1))
                        self.genom.append(World.persons[parents[source]].genom[x])
                elif World.radiation_level == 2:
                    # ---- Mixing genes -> Bad wins over good ----
                    if (genom_papa[x] == 0.0 and genom_mama[x] == 1.0) or (genom_mama[x] == 0.0 and genom_papa[x] == 1.0):
                        self.genom.append(0.0)
                    else:
                        source = random.choice((0,1))
                        self.genom.append(World.persons[parents[source]].genom[x])
                elif World.radiation_level == 3:
                    # ---- Mixing genes -> Bad wins over good and neutral ----
                    if genom_papa[x] == 0.0 or genom_mama[x] == 0.0:
                        self.genom.append(0.0)
                    else:
                        source = random.choice((0,1))
                        self.genom.append(World.persons[parents[source]].genom[x])
                # TODO: all other cases like neutral and good cases

            print("Mixed Genes: ", end="")
        print(self.genom, "Mittelwert:",(sum(self.genom) / len(self.genom)))
        # moral 0 always does evil things
        # moral 1 never does evil things
        self.moral = sum(self.genom) / len(self.genom)
        self.situation = random.randint(5, 10)

    #def update(self, year):
    #    if self.death_year is not None:
    #        return(self.number) + "====== "+ "arriving in city" if immigrant else "born here"
    #    self.history = [(text + " with those attributes:" + str(self.__dict__))]
    #    # self.get_children()
    #    self.update_year = None

    def update(self, year):
        if self.death_year is not None:
            return

        # ----- double death probability every 8 years -----
        age = year-self.birth_year
        if age % 8 == 0:
            self.probability_of_death *= 2

        # ----- trying to marry someone -----
        if self.married is None and age > 16:
            if random.random() < 0.9:
                spouse = self.get_married(year)

        # ----- chance to find new friend -----
        if random.random() < 0.3:
            newfriend = self.get_friends(year)

        # ----- chance to loose friend -----
        if len(self.friends) > 0 and random.random() < 0.05:
            exfriend = random.choice(self.friends)
            self.friends.remove(exfriend)
            self.history.append("{}: Ends friendship with {}.".format(year, exfriend))
            World.persons[exfriend].friends.remove(self.number)
            World.persons[exfriend].history.append("{}: Looses friendship with {}.".format(year, self.number))

        # ----- chance to get baby -----
        self.get_children(year)

        # ----- changing of situation -----
        self.situation += random.randint(-2, 3)
        if self.situation < 0:
            self.moral *= 0.85
        else:
            self.moral *= 1.1

        # ----- crime event -----
        if self.situation < 0:
            p1 = abs(self.situation) * 0.01
            if random.random() < p1:
                # bad situation creates chance for crime
                if random.random() > self.moral:
                    crime = random.choice(("destruction_friendship", "cheat_marriage", "stealing", "killing"))
                    if crime == "destruction_friendship":
                        px = random.choice([p for p in World.persons.values() if p.death_year is None and p.friends != []])
                        x = World.persons[px.number]
                        y = x.friends[0]
                        World.persons[px.number].friends.remove(y)
                        World.persons[y].friends.remove(px.number)
                        self.history.append("{}: {} destroyed the friendship of {} and {}".format(year, self.number, px.number, y))
                        World.persons[px.number].history.append("{}: {} destroyed the friendship of {} and {}".format(year, self.number, px.number, y))
                        World.persons[y].history.append("{}: {} destroyed the friendship of {} and {}".format(year, self.number, px.number, y))


                    elif crime == "cheat_marriage":
                        px = random.choice([p for p in World.persons.values() if p.death_year is None and p.married is not None])
                        x = World.persons[px.number]
                        y = x.married
                        World.persons[px.number].married = None
                        World.persons[y].married = None
                        self.history.append("{}: Destroyed the marriage of {} and {}".format(year, px.number, y))
                        World.persons[px.number].history.append("{}: {} destroyed the marriage of {} and {}".format(year, self.number, px.number, y))
                        World.persons[y].history.append("{}: {} destroyed the marriage of {} and {}".format(year, self.number, px.number, y))
                    elif crime == "stealing":
                        px = random.choice([p for p in World.persons.values() if p.death_year is None])
                        x = World.persons[px.number]
                        x.situation -= random.randint(10,20)
                    elif crime == "killing":
                        ## TODO extra check
                        px = random.choice([p for p in World.persons.values() if p.death_year is None])
                        x = World.persons[px.number]
                        x.history.append("{}: Got killed by {}.".format(year, self.number))
                        x.death_year = year
                        if x.married is not None:
                            World.persons[x.married].married = None
                        for friend in x.friends:
                            World.persons[friend].friends.remove(px.number)
                    print(crime, self.number, year, self.situation, self.moral)

        # ----- chance to die -----
        if random.random() < self.probability_of_death:
            self.history.append("{}: Died of natural causes.".format(year))
            self.death_year = year
            if self.married is not None:
                World.persons[self.married].married = None
            for friend in self.friends:
                World.persons[friend].friends.remove(self.number)

    def get_friends(self, year):
        """friends must have: different number, age-difference +- 10 at max. """
        candidates = [p for p in World.persons.values() if p.death_year is None and p.number != self.number and abs(
            p.birth_year - self.birth_year) < 20 and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number != self.married]# and self.birth_year < year - 5]
        if len(candidates) == 0:
            self.history.append("{}: Found no suitable people to befriend.".format(year))
            return None
        x = random.choice(candidates).number
        self.friends.append(x)
        self.history.append("{}: Found a new friend: {}".format(year, x))
        # gegenseitige Freundschaft:
        World.persons[x].friends.append(self.number)
        World.persons[x].history.append("{}: Accepted friendship request of {} ".format(year, self.number))
        return x

    def get_married(self, year):
        """married people must have: different number, age-difference +- 10 at max. """

        candidates = [p for p in World.persons.values() if p.death_year is None and p.married is None and p.number != self.number and p.number not in self.foes and p.number not in self.children and p.gender != self.gender and p.birth_year < year - 16 and not p.is_sibling(self)]
        if len(candidates) == 0:
            self.history.append("{}: Found no suiteable candidates to marry.".format(year))
            return None
        x = random.choice(candidates).number
        self.married = x
        # take name of partner
        self.last_name = World.persons[x].last_name
        # remove spouse of friendlist to avoid becoming ex-friend
        self.history.append("{}: Managed to marry {} and changed last name to {}.".format(year, self.married, self.last_name))
        if x in self.friends:
            self.friends.remove(x)
        if self.number in World.persons[x].friends:
            World.persons[x].friends.remove(self.number)
        # self.marriages.add(x)
        # gegenseitige Heirat:
        self.marriage_year = year
        World.persons[x].marriage_year = year
        World.persons[x].married = self.number
        World.persons[x].history.append("{}: Gracefully accepted marriage proposal of {}.".format(year, self.number))
        # little chance that both choose a comlete new name
        if random.random() < 0.4:
            new_name = random.choice(World.last_names)
            self.last_name = new_name
            World.persons[x].last_name = new_name
            World.persons[x].history.append("{}: The married couple chose the new family name {}.".format(year, new_name))
            self.history.append("{}: The married couple chose the new family name {}.".format(year, new_name))
        return x

    def get_children(self, year):
        """children only from married couple (including ex), children for both parents! children at least 20 years younger"""
        if self.married is None:
            return
        if self.gender != "female":
            return
        if year-self.marriage_year < 1:
            return
        if year-self.birth_year > 50:
            return
        children = len(self.children)
        p = 1 / (3 + children)
        if random.random() < p:
            # ----- Baby kriegen -----
            babynumber = Person.number
            self.children.append(babynumber)
            World.persons[self.married].children.append(babynumber)
            self.history.append("{}: Mommy got a baby: {}.".format(year, babynumber))
            World.persons[self.married].history.append("{}: Becomes daddy of: {}.".format(year, babynumber))
            baby = Person(year, min_age=0, max_age=0, last_name=self.last_name, immigrant=False)

        # if len(self.marriages) == 0:
        #    return
        # for _ in range(megaroll("1D3")-1):
        #    partner = World.persons[random.choice(self.marriages)]
        # candidates = [p for p in World.persons.values() if p.number != self.number and p.number not in self.marriages and p.number not in self.friends and p.number not in self.foes and p.number not in self.children and p.number  and p.birth_year > self.birth_year+20 and p.birth_year > partner.birth_year + 20]

        #    x = random.choice(candidates).number
        #    self.children.add(x)

    def get_parents(self):
        parents = []
        for p in [p for p in World.persons.values() if p.birth_year < self.birth_year - 15]:
            if self.number in p.children:
                parents.append(p.number)
        return parents

    def is_sibling(self, x):
        """ Check if person x shares at least one parent with person self"""
        for p in self.get_parents():
            if p in x.get_parents():
                return True
        return False

    def print_history(self):
        for line in self.history:
            print(line)


if __name__ == "__main__":
    story()
