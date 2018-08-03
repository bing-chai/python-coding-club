# my first notepad commit!!!
"""
My first class assignment about classes
"""
import random
import time

class BadmintonPlayer():
    # creates player and holds stats and moves

    def __init__(self):
        self.player_name = ""
        self.player_age = ""
        self.player_category= ""
        self.stamina = 10

    def __str__(self):
        return("---\n"+
                f"{self.name}\'s stats are:\n"+
                f"Stamina:{self.stamina}\n"+
                "---"
                )

    def badminton_hit():
        damage =

    def screenprint(self):
        this_string = "placeholder"
        print(this_string)



Player1 = BadmintonPlayer()
Player2 = BadmintonPlayer()

while match_points < 5:
    print(f"{Player1.name} serves!")
    print(f"{Player2.name} serves!")
    time.sleep(2)
