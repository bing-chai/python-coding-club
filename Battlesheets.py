
"""A blatant clone of Battleship."""

import os
from random import randint, choice as rand_choice

__author__ = 'Dan Mudie'


#add sounds - first cut
import pygame
pygame.init()
hit_sound = pygame.mixer.Sound("sounds/explosion-01.wav")
miss_sound = pygame.mixer.Sound("sounds/beach-wave-01.wav")


class Coord(object):
    """A class to represent an x,y position on the gameboard."""

    def __init__(self, x, y):
        """Create a Coord objectself

        Args:
            x (int): The x coordinate
            y (int): The y coordinate

        """
        self.pos = (x,y)

    def __str__(self):
        return "Coord("+str(self.pos[0])+","+str(self.pos[1])+")"

    def __getitem__(self, key):
        return self.pos[key]

    def __add__(self, other):
        return Coord(self[0] + other[0], self[1] + other[1])

    def __eq__(self, other):
        if self.pos[0] == other.pos[0] and self.pos[1] == other.pos[1]:
            return True
        else: return False

    def __hash__(self):
        return hash(self.pos)

    def left(self):
        """Return a Coord that is one unit to the left of the current Coord"""
        return Coord(self[0]-1, self[1])

    def right(self):
        """Return a Coord that is one unit to the right of the current Coord"""
        return Coord(self[0]+1, self[1])

    def above(self):
        """Return a Coord that is one unit above of the current Coord"""
        return Coord(self[0], self[1]-1)

    def below(self):
        """Return a Coord that is one unit below the current Coord"""
        return Coord(self[0], self[1]+1)

#define some constants for the game
GAME_WIDTH = 10
GAME_HEIGHT = 10
NOT_HIT = 0
HIT = 1
SUNK = 2
MISS = '\\' #This is actually a single backslash

SHIP_LENGTHS = {'CARRIER'    : 5,
                'BATTLESHIP' : 4,
                'CRUISER'    : 3,
                'SUBMARINE'  : 3,
                'DESTROYER'  : 2}

class Gameboard(object):
    """The object on which ships are placed.

    The gameboard is a grid, GAME_WIDTH by GAME_HEIGHT units.  Ships
    are placed on the gameboard and are fired at by the player.  There
    is one gameboard per player.  Ship class is an inner class of
    of Gameboard.

    Takes no arguments to initialize.

    """
    class Ship(object):
        """Pretty self explanatory.  It's a ship (or submarine).

        Args:
            pos (Coord): Coordinate object representing the top left position
                of the ship.
            type (Str): Must be one of the ship types in SHIP_LENGTHS.
            orientation (Str): Must either be 'v' or 'h'.  Indicates whether the
                ship is oriented vertically or horizontally.

        """
        def __init__(self,pos,type,orientation):
            self.pos = pos
            self.type = type
            self.length = SHIP_LENGTHS[type]
            self.orientation = orientation
            self.sunk = False

            #add points and set to NOT_HIT
            self.points = {}
            if orientation == 'v':
                for x in range(self.length):
                    self.points[pos+Coord(0,x)] = NOT_HIT
            elif orientation == 'h':
                for x in range(self.length):
                    self.points[pos+Coord(x,0)] = NOT_HIT

        def __str__(self):
            """Used for debugging."""
            s =""
            for p,v in self.points.items():
                s += f"{p},{v}\n"
            s+=(f"{self.type} "
                f"origin {self.pos} "
                f"{self.length} units long "
                f"oriented {self.orientation}")
            return s

    def __init__(self):
        self.ships = []
        self.misses = [] #A list of  missed shots as Coord objects
        self.defeated = False #Indicates if the player has lost

    def print(self):
        """Print the gameboard."""
        ship_points=self.get_ship_points()
        print("   A B C D E F G H I J")
        for row in range(GAME_HEIGHT):
            print("%2s|" % (row+1), end='')
            for col in range(GAME_WIDTH):
                if Coord(col,row) in ship_points.keys():
                    print(ship_points[Coord(col,row)], end='')
                elif Coord(col,row) in self.misses:
                    print(MISS, end='')
                else:
                    print(' ', end='')
                print("|", end='')
            print('')

    def print_hits_and_misses(self):
        """Print the hits, misses and sunk ships of a gameboardself.

        Will not print the ship points that have not been hit.  Used to
        display the opponent's gameboard.

        """
        ship_points=self.get_ship_points()
        print("   A B C D E F G H I J")
        for row in range(GAME_HEIGHT):
            print("%2s|" % (row+1), end='')
            for col in range(GAME_WIDTH):
                pos = Coord(col,row)
                if pos in ship_points.keys() \
                and ship_points[pos] in (HIT, SUNK):
                    print(ship_points[pos], end='')
                elif pos in self.misses:
                    print(MISS, end='')
                else: print(' ', end='')
                print("|", end='')
            print('')

    def get_hits_and_misses(self):
        """Return a dictionary of HIT, SUNK or MISS positionsself.

        Used by the AI to determine points on the gameboard that are either
        HIT, SUNK or MISS.

        Returns:
            A dictionary of Coord:status where the status is HIT, MISS or
            SUNK.

        """
        points = {}
        for k,v in self.get_ship_points().items():
            if v in (HIT, SUNK):
                points[k] = v
        for p in self.misses:
            points[p] = MISS
        return points

    def add_ship(self, pos, type, orientation, verbose):
        """Add a ship to the gameboard.

        Args:
            pos (Coord): A Coord object representing the top left
                corner of the ship.
            type (Str): A type of ship.  Must be from  SHIP_LENGTHS.
            orientation (Str): Indicates if the ship is oriented vertically
                or horizontally.  Must be either 'v or 'h'.
            verbose (Bool): Should I print messages to the screen?
                Usually 'yes' if a human is playing, 'no' if the AI is
                playing (coz he can't read).

        Returns:
            True if a ship was placed, False if a ship was not placed.

        """
        if orientation not in ('h','v'):
            if verbose: print("Unknown orientation")
            return False

        if type not in SHIP_LENGTHS.keys():
            if verbose: print("Unknown ship type")
            return False

        if any(x.type == type for x in self.ships):
            if verbose: print("Ship already added")
            return False

        if pos[0] < 0 or pos[1] < 0:
            if verbose: print("Ship out of bounds")
            return False

        if (orientation == 'h' and pos[0] + SHIP_LENGTHS[type] - 1 > GAME_WIDTH - 1) \
        or (orientation == 'v' and pos[1] + SHIP_LENGTHS[type] - 1 > GAME_HEIGHT - 1):
            if verbose: print("Ship out of bounds")
            return False

        newShip = Gameboard.Ship(pos, type, orientation)

        #check if ship would overlap with an existing ship
        ship_points = self.get_ship_points().keys()

        for point in newShip.points.keys():
            if point in ship_points:
                if verbose: print("Already a ship in that position")
                return False
        #Finally, add the ship
        self.ships.append(newShip)

    def print_all_ships(self):
        for ship in self.ships:
            print(ship)

    def get_ship_points(self):
        p = {}
        for ship in self.ships:
            p.update(ship.points)
        return p

    def fire(self,pos, verbose=False):
        """Fire at the gameboard.

        Args:
            pos (Coord): A Coord object representing the position that will
                be fired at.
            verbose (Bool, default = False): Should I print to the screen?

        Returns:
            Bool:  True if the shot hit a ship, regardless of whether or
                not that ship point has already been hit.  False if the
                shot was within the gameboard boundaries but did not hit a
                ship.  None if the shot was outside the gameboard.

        """
        if pos[0] >= GAME_WIDTH or pos[1] >= GAME_HEIGHT \
        or pos[0] < 0 or pos[1] < 0:
            if verbose: print("Shot out of boundaries")
            return None

        for ship in self.ships:
            if pos in ship.points.keys():
                ship.points[pos] = HIT
                if verbose: 
                   print("Hit!")
                pygame.mixer.Sound.play(hit_sound)
                pygame.mixer.music.stop()

                #check if all points in the ship have been HIT
                if NOT_HIT not in ship.points.values():
                    ship.sunk = True
                    #change all the coordinates in the ship to sunk
                    for coord in ship.points.keys():
                        ship.points[coord] = SUNK

                    if verbose: print(f"{ship.type} sunk!")

                    #check if all ships have been sunk
                    game_over = True
                    for s in self.ships:
                        if s.sunk == False:
                            game_over = False
                            break
                    if game_over: self.defeated = True
                return True

        #if we got here, the shot must be a miss
        if verbose: print("Miss!")
        pygame.mixer.Sound.play(miss_sound)
        pygame.mixer.music.stop()
        self.misses.append(pos)
        return False

class AI(object):
    """An AI to play the game and eventually start Skynet.

    It's like the little robot kid from that Steven Spielberg movie who
    could see dead people.

    Takes no args to initialize and doesn't actually have any attributes.
    Just plays the game with the gameboards it is passed each turn.

    """
    def place_ships(self, gameboard):
        """Place ships on the gameboard.

        Method for AI to place ships.

        Args:
            gameboard (Gameboard): The AI's own gameboard.
        """

        orientations = ['h','v']
        for ship in set(SHIP_LENGTHS.keys()) - set([s.type for s in gameboard.ships]):
            ship_placed = False
            while not ship_placed:
                pos = Coord(randint(0,9), randint(0,9))
                o = orientations[randint(0,1)]
                if gameboard.add_ship(pos=pos, type = ship, orientation=o, verbose=False) == False:
                    clear_screen()
                else: ship_placed = True
        return

    def can_I_shoot_here(self, pos, enemy_gameboard):
        """Is it possible to shoot here?

        Args:
            pos (Coord): The position where you'd like to shoot
            enemy_gameboard (Gameboard): The gameboard on which you'd like
               to shoot.
        Returns:
            Bool.  True if that position is empty and within the gameboard.
            False if the position is outside the gameboard or already has as
            a HIT or a MISS there.

        """
        # if out of bounds, can't shoot here
        if pos[0] >= GAME_WIDTH or pos[0] < 0 or pos[1] >= GAME_HEIGHT \
        or pos[1] < 0: return False

        #if already has a shot there, can't shoot There
        if pos in enemy_gameboard.get_hits_and_misses().keys(): return False

        return True

    def find_next_unhit_ship_point(self, pos, direction, gameboard):
        """Find a spot that could potentially be the next unhit ship point.

        Given that point x is a HIT and the adjoining point y is also a hit,
        it makes sense to assume that the points either side of x and y
        might also be unhit ship points, if shots haven't been fired there.

        Args:
            pos (Coord): The position to start from.
            direction (Str): Must be either LEFT, RIGHT, UP or DOWN.  Indicates
               the direction to starting looking for a potential spot to fire.
            gameboard (Gameboard): the gameboard on which to look for a place
               to fire.
        Returns:
            A Coord object if it can find a spot to fire at, otherwise None

        """
        if direction not in ['LEFT', 'RIGHT', 'UP', 'DOWN']: return None

        hits_and_misses = gameboard.get_hits_and_misses()

        if direction == 'LEFT':
            next_pt = pos.left()
            #if the point is outside the boundaries return None
            if next_pt[0] < 0: return None
            if next_pt in hits_and_misses.keys():
                if hits_and_misses[next_pt] == HIT:
                    #Holey moley, it's recursion!
                    return self.find_next_unhit_ship_point(next_pt, direction, \
                    gameboard)
                #If the point is a MISS, there are no more ship points
                #here
                if hits_and_misses[next_pt] == MISS:
                    return None
            return next_pt

        if direction == 'RIGHT':
            next_pt = pos.right()
            if next_pt[0] >= GAME_WIDTH: return None
            if next_pt in hits_and_misses.keys():
                if hits_and_misses[next_pt] == HIT:
                    return self.find_next_unhit_ship_point(next_pt, direction,\
                     gameboard)
                if hits_and_misses[next_pt] == MISS:
                    return None
            return next_pt

        if direction == 'UP':
            next_pt = pos.above()
            if next_pt[1] < 0: return None
            if next_pt in hits_and_misses.keys():
                if hits_and_misses[next_pt] == HIT:
                    return self.find_next_unhit_ship_point(next_pt, direction,\
                    gameboard)
                if hits_and_misses[next_pt] == MISS:
                    return None
            return next_pt

        if direction == 'DOWN':
            next_pt = pos.below()
            if next_pt[1] >= GAME_HEIGHT: return None
            if next_pt in hits_and_misses.keys():
                if hits_and_misses[next_pt] == HIT:
                    return self.find_next_unhit_ship_point(next_pt, direction, \
                    gameboard)
                if hits_and_misses[next_pt] == MISS:
                    return None
            return next_pt

    def turn(self, enemy_gameboard):
        """Play a turn of the game.

        Method for AI to play a turn of the game.

        Args:
            enemy_gameboard (Gameboard): The opponent's gameboard.

        """
        #get the current hits and print_hits_and_misses
        hits_and_misses = enemy_gameboard.get_hits_and_misses()

        #find the first HIT if there is one and shoot around it
        for point, value in hits_and_misses.items():
            if value == HIT:
                #Ships are lines.  So if a neighbouring point has been hit,
                #trying shooting along that axis.
                #First, try shooting in the opposite direction of the other
                #HIT.  If we can't fire in that direction, try firing on
                #the other side of the HIT.

                #If the block to the left is already HIT...
                if point.left() in hits_and_misses.keys() \
                and hits_and_misses[point.left()] == HIT:
                    #If the block to the right has not been fired at...
                    if point.right() not in hits_and_misses.keys() \
                    and point.right()[0] < GAME_WIDTH:
                        enemy_gameboard.fire(point.right(), verbose = False)
                        return
                    #look for more shootable points to the left
                    target = self.find_next_unhit_ship_point(point.left(), \
                    'LEFT', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return
                    #if there are none to the left, look to the right
                    target = self.find_next_unhit_ship_point(point.right(), \
                    'RIGHT', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return

                #if the point to the right has been HIT...
                if point.right() in hits_and_misses.keys() \
                and hits_and_misses[point.right()] == HIT:
                    if point.left() not in hits_and_misses.keys() \
                    and point.left()[0] >= 0:
                        enemy_gameboard.fire(point.left(), verbose = False)
                        return
                    #look for more shootable points to the right
                    target = self.find_next_unhit_ship_point(point.right(), \
                    'RIGHT', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return
                    #if there are none to the right, look to the left
                    target = self.find_next_unhit_ship_point(point.left(), \
                    'LEFT', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return

                #if the point above has been HIT...
                if point.above() in hits_and_misses.keys() \
                and hits_and_misses[point.above()] == HIT:
                    if point.below() not in hits_and_misses.keys() \
                    and point.below()[1] < GAME_HEIGHT:
                        enemy_gameboard.fire(point.below(), verbose = False)
                        return
                    #look for more shootable points above
                    target = self.find_next_unhit_ship_point(point.above(), \
                    'UP', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return
                    #if there are none to the right, look to the left
                    target = self.find_next_unhit_ship_point(point.below(), \
                    'DOWN', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return

                #if the point below has been HIT
                if point.below() in hits_and_misses.keys() \
                and hits_and_misses[point.below()] == HIT:
                    if point.above() not in hits_and_misses.keys() \
                    and point.above()[1] >= 0:
                        enemy_gameboard.fire(point.above(), verbose = False)
                        return
                    #look for more shootable points above
                    target = self.find_next_unhit_ship_point(point.below(), \
                    'DOWN', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return
                    #if there are none below, above
                    target = self.find_next_unhit_ship_point(point.above(), \
                    'UP', enemy_gameboard)
                    if target is not None:
                        enemy_gameboard.fire(target, verbose = False)
                        return

                #Can't shoot in the opposite direction of existing
                #HIT points, but can we shoot anywhere nearby?
                if point.left() not in hits_and_misses.keys() \
                and point.left()[0] >= 0:
                    enemy_gameboard.fire(point.left(), verbose=False)
                    return

                if point.right() not in hits_and_misses.keys() \
                and point.right()[0] < GAME_WIDTH:
                    enemy_gameboard.fire(point.right(), verbose=False)
                    return

                if point.above() not in hits_and_misses.keys() \
                and point.above()[1] >= 0:
                    enemy_gameboard.fire(point.above(), verbose=False)
                    return

                if point.below() not in hits_and_misses.keys() \
                and point.below()[1] < GAME_HEIGHT:
                    enemy_gameboard.fire(point.below(), verbose=False)
                    return

        #shoot randomly
        while True:
            target = Coord(randint(0,GAME_WIDTH-1), randint(0,GAME_HEIGHT-1))
            if target in hits_and_misses.keys():
                continue
            else:
                enemy_gameboard.fire(target, verbose=False)
                break

def get_an_int(prompt, min, max):
    """Get an Int from the user.

    Args:
        prompt (Str): A string to prompt the user to input an int.
        min (Int): The minimum allowed integer value.
        max (Int): The maximum allowed integer value.

    Returns: Surprise, surprise...an Int!

    """
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print(f"Please enter a number between {min} and {max}")
            continue

        if value < min or value > max:
            print(f"Please enter a number between {min} and {max}")
            continue
        else:
            break
    return value

def get_an_uppercase_string(prompt, possible_choices):
    """Get an uppercase string from the user.

    Args:
        prompt (Str): A string to prompt the user to input an int.
        possible_choices (list of Str): A list of acceptable responses.

    Returns: An uppercase string.
    """
    while True:
        try:
            value = str(input(prompt))
        except ValueError:
            print("Incorrect format.")
            continue

        value = value.upper()

        if value not in possible_choices:
            print("That's not one of the possible choices.")
            continue
        else:
            break
    return value

def get_a_Coord(prompt):
    """Get a Coord object from the user.

    The user must enter a letter and a number.  The letter must be between
    A - I and the number must be between 1 - 10.  Yeah, it's hard-coded for
    the moment.

    Args:
        prompt (Str): A string to prompt the user to input an int.

    Returns:  A Coord object.
    """
    while True:
        try:
            value = str(input(prompt)).strip()
        except ValueError:
            print ("Please enter a coordinate of the form A1")
            continue

        #remove brackets
        value = value.replace(')','').replace('(','')

        if len(value) < 2:
            print("Please enter a coordinate of the form A1")
            continue

        #Add a separating comma if there isn't one
        if value[1] != ',':
            value = value[0:1]+','+value[1:]

        coords = value.split(",")

        #Check that only two coordinates were provided, as in A1
        if len(coords) != 2:
            print ("Please enter a coordinate of the form A1")
            continue

        #Check that the first coordinate is a letter between A - I`
        if len(coords[0])!=1 or \
        ord(coords[0].upper()[0]) < 65 or ord(coords[0].upper()[0]) > 74:
            print ("Please enter a coordinate of the form A1")
            continue

        #Convert A, B, C etc to 0, 1, 2
        x = ord(coords[0].upper())-65

        #Check that the second coordinate is an INT between 1 - 10
        try:
            y = int(coords[1])
        except ValueError:
            print ("Please enter a coordinate of the form A1")
            continue

        if y < 1 or y > 10:
            print("Please enter a coordinate of the form A1")
            continue

        return Coord(x,y-1)

def clear_screen():
    os.system("cls" if os.name == 'nt' else "clear")

def print_menu():
    print('''
          ____        _   _   _           _               _
         |  _ \      | | | | | |         | |             | |
         | |_) | __ _| |_| |_| | ___  ___| |__   ___  ___| |_ ___
         |  _ < / _` | __| __| |/ _ \/ __| '_ \ / _ \/ _ \ __/ __|
         | |_) | (_| | |_| |_| |  __/\__ \ | | |  __/  __/ |_\__ \\
         |____/ \__,_|\__|\__|_|\___||___/_| |_|\___|\___|\__|___/


                                     |__
                                     |\/
                                     ---
                                     / | [
                              !      | |||
                            _/|     _/|-++'
                        +  +--|    |--|--|_ |-
                     { /|__|  |/\__|  |--- |||__/
                    +---------------___[}-_===_.'____                 /\\
                ____`-' ||___-{]_| _[}-  |     |_[___\==--            \/   _
 __..._____--==/___]_|__|_____________________________[___\==--____,------' .7
|                                                                     BB-61/
 \_________________________________________________________________________|
''')
    print('1. Single player\n'
          '2. Two player\n'
          '3. Quit')

def place_ships(player_name, gameboard):
    """Place ships.

    A method for regular human players to place his/her/ze's shipsself.

    Args:
        gameboard (Gameboard): The player's gameboard on which to place
            the ships.

    """
    clear_screen()
    print(f"{player_name}, place your ships")

    orientations = ['h','v']

    #If you can't be bothered placing your ships (like me when I was testing)
    #get the computer to do it for you!
    auto = input("Auto place ships? (y,n) ")
    if auto == 'y':
        for ship in set(SHIP_LENGTHS.keys()) - set([s.type for s in gameboard.ships]):
            ship_placed = False
            while not ship_placed:
                pos = Coord(randint(0,GAME_WIDTH-1), randint(0,GAME_HEIGHT-1))
                o = orientations[randint(0,1)]

                if gameboard.add_ship(pos=pos, type = ship, orientation=o, verbose=False) == False:
                    pass
                    #clear_screen()
                else:
                    ship_placed = True
        gameboard.print()
        input("Press enter to continue...")
        return

    #OK, place the ships yourself
    while True:
        gameboard.print()
        available_ships = set(SHIP_LENGTHS.keys()) - set([s.type for s in gameboard.ships])
        if len(available_ships) < 1: break

        #print the list of ships
        print(" "*12+"Length")
        for ship_name in available_ships:
            print(f"{ship_name}"+" "*(12-len(ship_name))+str(SHIP_LENGTHS[ship_name]))

        #Get what ship to place and where and what orientation
        choice = get_an_uppercase_string("Choose a ship to place:", available_ships)
        position = get_a_Coord("Where would you like to put it? Enter "
                               "the top left coordinate like A1:")
        if position in gameboard.get_ship_points().keys():
            print("There's already a ship there, try again.")
            continue
        orientation = get_an_uppercase_string("Vertical (v) or "+\
        "Horizontal (h):", ('H','V')).lower()

        #Try to add ship to gameboard
        if gameboard.add_ship(pos=position, type = choice,\
         orientation=orientation, verbose=True) == False:
            continue

        clear_screen()

def turn(player_name, player_gameboard, enemy_gameboard):
    """Take a turn.

    Method for regular human players to take a turn in the game.

    Args:
        player_gameboard (Gameboard): So he can see how badly he
            is losing.
        enemy_gameboard (Gameboard): So player can see where
            he has already shot.

    """
    clear_screen()
    input(f"{player_name}'s turn.  Press enter to continue...")

    #print the gameboard legend so the player knows what all those
    #'1's and '2's mean.
    print(f"{HIT} = hit")
    print(f"{NOT_HIT} = not yet hit")
    print(f"{MISS} = miss")
    print(f"{SUNK} = ship sunk", end="\r\n\r\n")

    print(f"Your ships, {player_name}:")
    player_gameboard.print()
    print("Ships still alive:")
    print(" "*12+"Length")
    for s in player_gameboard.ships:
        if s.sunk == False:
            print(f"{s.type}"+" "*(12-len(s.type))+str(SHIP_LENGTHS[s.type]))
    print()
    print("Ships sunk:")
    for s in player_gameboard.ships:
        if s.sunk == True:
            print(f"{s.type}"+" "*(12-len(s.type))+str(SHIP_LENGTHS[s.type]))

    print()

    #print the enemy gameboard (but not the un-hit ship points)
    print("The enemy ships:")
    enemy_gameboard.print_hits_and_misses()
    print("Enemy ships still alive:")
    print(" "*12+"Length")
    for s in enemy_gameboard.ships:
        if s.sunk == False:
            print(f"{s.type}"+" "*(12-len(s.type))+str(SHIP_LENGTHS[s.type]))
    print()
    print("Enemy ships sunk:")
    for s in enemy_gameboard.ships:
        if s.sunk == True:
            print(f"{s.type}"+" "*(12-len(s.type))+str(SHIP_LENGTHS[s.type]))

    #Where would the user like to fire?
    target = get_a_Coord("Choose a target (e.g. A1):")
    enemy_gameboard.fire(target, verbose=True)

    input("Press enter to continue...")

#This is where the execution actually starts
clear_screen()
p1 = Gameboard()
p2 = Gameboard()

print_menu()
user_selection = get_an_int("Choose a game mode: ", 1, 3)
if user_selection == 3:
    quit()
#single player
elif user_selection == 1:
    ai = AI()
    ai.place_ships(p2)
    place_ships("Player 1", p1)
    game_over = False
    while not game_over:
        turn("Player 1", p1, p2)
        if p2.defeated == True:
            print(f"Player 1 wins!")
            print(f"Player 1's ships:")
            p1.print()
            print(f"Admiral Meng's ships")
            p2.print()
            game_over = True
            break;
        ai.turn(p1)
        if p1.defeated == True:
            print(f"Admiral Meng wins!")
            print(f"Admiral Meng's ships:")
            p2.print()
            print(f"Player 1's ships")
            p1.print()
            game_over = True
#multiplayer
elif user_selection == 2:
    place_ships("Player 1", p1)
    place_ships("Player 2", p2)
    game_over = False
    while not game_over:
        turn("Player 1", p1, p2)
        if p2.defeated == True:
            print(f"Player 1 wins!")
            print(f"Player 1's ships:")
            p1.print()
            print(f"Player 2's ships")
            p2.print()
            game_over = True
            break;
        turn("Player 2", p2, p1)
        if p1.defeated == True:
            print(f"Player 2 wins!")
            print(f"Player 2's ships:")
            p2.print()
            print(f"Player 1's ships")
            p1.print()
            game_over = True
