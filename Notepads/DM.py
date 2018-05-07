#Dan's classy class example!! Ho, ho, ho!

import random as r
import time

class Troll:
    '''
        Lives under a bridge, terrorises goats
        and writes nasty comments on social media.
    '''
    #class variable
    attack_strength = 5

    def __init__(self):
        self.health = 20

    def attack(self, opponent):
        #Trolls are somewhat uncoordinated and only have a 80% chance of
        #landing a blow
        if r.random() < 0.8:
            opponent.health -= r.randint(5,15)/10.0 * Troll.attack_strength
            return True
        else : return False

class Hero:
    '''
        Player character.
    '''
    def __init__(self):
        self.attack_strength = 10
        self.super_attack_strength = 15
        self.health = 35
        self.super_attacks_left = 2

    def __str__(self):
        return ("******\n"+
                "Hero\n"+
               f"Health: {self.health}\n"+
               f"Num of special attacks left: {self.super_attacks_left}\n"+
               "******\n")

    def attack(self, opponent):
            opponent.health -= r.randint(5,15)/10.0 * self.attack_strength

    def super_attack(self, opponent):
        if self.super_attacks_left > 0:
            opponent.health -= r.randint(5,15)/10.0 * self.super_attack_strength
            self.super_attacks_left -= 1


bad_guys = []
bad_guys.append(Troll())
bad_guys.append(Troll())
bad_guys.append(Troll())
dan_mudie = Hero()
print(dan_mudie)
input("This is you.\nHit Enter to continue...")
print("You tread cautiously into the wood,"+
      " when all of a sudden...")
time.sleep(3)
print("...three trolls appear!\n")
time.sleep(2)

#Game-ish loop
while dan_mudie.health > 0 and len([t for t in bad_guys if t.health > 0]):

    #print trolls
    print("Troll 1       Troll 2       Troll 3")
    for i, troll in enumerate(bad_guys):
        if troll.health > 0 : print(f"Health: {troll.health}".ljust(14), end = '')
        else : print("DEAD".ljust(14), end='')
    print()
    time.sleep(2)

    #one troll attacks
    for t in [t for t in bad_guys if t.health > 0]:
        print("\nA troll attacks!")
        time.sleep(2)
        if t.attack(dan_mudie) : print("You've been hit!\n")
        else : print("The troll misses...and clumsily falls over." +
                     "  Awwww, isn't he cute!")

        break
    time.sleep(2)
    if dan_mudie.health < 1: break
    print(dan_mudie)
    input("Hit Enter to continue...")

    #Hero attacks...fyi, there is no input validation #thuglife
    troll_to_attack = int(input("Who will you attack (1,2,3): "))
    attack_mode = input("What will you do? (a = attack, sa = super attack): ")

    if attack_mode == 'a':
        dan_mudie.attack(bad_guys[troll_to_attack-1])
    elif attack_mode == 'sa':
        dan_mudie.super_attack(bad_guys[troll_to_attack-1])

    print(dan_mudie)

#either hero is dead or all the trolls are dead
if dan_mudie.health < 1:
    print("You've been killed!\n"
          "Who'll take the ring to Alderan now???")
    quit()
#if hero isn't dead, the trolls must be dead
print("Troll 1       Troll 2       Troll 3")
for i, troll in enumerate(bad_guys):
    if troll.health > 0 : print(f"Health: {troll.health}".ljust(14), end = '')
    else : print("DEAD".ljust(14), end='')
print("You are victorious!!!")
