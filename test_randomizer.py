
import random

def randomizer(list_of_chances=[1]):
    """gives back an integer depending on chance.
       e.g. randomizer((.75, 0.15, 0.5, 0.5)) gives in 75% 0, in 15% 1, and in 5% 2 or 3"""
    total = sum(list_of_chances)
    v = random.random() * total # a value between 0 and total
    edge = 0
    for i, c in enumerate(list_of_chances):
        edge += c
        print("total, v, edge, i, c",total, v, edge, i, c)
        if v <= edge:
            return i
    else:
        raise SystemError("problem with list of chances:", list_of_chances)
        

# ---- testing ---
results = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0 }
for i in range(1000):
    r = randomizer([.30, 0.15, 0.15, 0.15, 0.1, 0.1,0.025, 0.025 ])
    if r in results:
        results[r] += 1
    else:
        results[r] = 1
        
print(results)
        
        
    
