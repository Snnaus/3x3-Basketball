import random, math
from player import rebound_script

class Ball:
    """This is the class to make a ball object for each game of the simulation"""

    #this is the array to define the position of the ball
    court_position = [0,0]

    #this array is to determine the destination of the ball on a bounce
    destination = [0,0]

    #these attributes are to tell the pick_up function if the resulting pick_up is a steal or rebound for the player
    is_steal = False
    is_rebound = False

    #this is an attribute to determine who had the possession of the ball last; this is used to determine turnovers and assists respectively; The last touch is to determine which team gets the inbound ball
    #and to determine who gets a steal from a tip away; these take the player_id of the player
    last_posession = 0
    last_touch = 0
    assistor = 0
    assistor_timer = 0 #this counts the seconds after passing the ball; if it exceeds 3 seconds the assister does not receive an assist

    #this function is to determine the destination of the ball on a bounce; it takes the distance of the shot taken and gives it a random distance to go;
    #it should give the ball a random slope and random 'power' and then multiple that and add it to the position of the basket to get the position of the ball; The ball should
    #roll in the segments that are 1/3 the total (too match with the turns) and after one sec(3 turns) half the distance; a bad catch/pass or hand_check tip is the equivalent
    #of a mid-range rebound as far as bounce is concerned; this is complete 7/12/2014
    def bounce_destination(self, power, focal_point):
        changing_array = focal_point
        potential_places = []
        loop_range = power**2

        #this for loop looks for all coordinates in a 360 radius that are equal to the the power; it then appends the it to the potential_places

        for x in range(loop_range+1):
            new_position = 0
            neg_new = 0
            neg_x = 0
            neg_y = 0
            
            this_x = int(round(math.sqrt(loop_range - x)))
            this_y = int(round(math.sqrt(x)))

            new_position = [this_x, this_y]
            neg_new = [this_x * -1, this_y * -1]
            neg_x = [this_x * -1, this_y]
            neg_y = [this_x, this_y * -1]

            potential_places.append(new_position)
            potential_places.append(neg_x)

            #this is a if statement to see if the focal_point is the basket; if it is the ball cannot go -y; this is because cannot bounce behind the basket
            #because of this little thing called physics and a backboard
            if focal_point != [7,1]:
                potential_places.append(neg_y)
                potential_places.append(neg_new)

        #at this point a random coordinates from 'potential_places' will be taken and applied to the focal_point; this is the new destination
        pot_look = random.randint(0,len(potential_places)-1)
        new_place = potential_places[pot_look]
        
        
        
        new_destination = [0,0]
        new_destination[0] = focal_point[0] + new_place[0]
        new_destination[1] = focal_point[1] + new_place[1]
        return new_destination
            
    #this function moves the ball; Completed 7/12/2014
    def bounce(self, power, focal_point=[7,1]):
        dest = [0,0]
        dest[0] = self.destination[0]
        dest[1] = self.destination[1]
        #this checks if the ball has NO momentum; if the ball doesn't it is given a destination, otherwise the ball already has a destination
        if self.court_position == self.destination:
            self.court_position = self.bounce_destination(power, focal_point)
            #this gives the ball a similar path; this is to continue moving if no player picks up the ball 
            self.destination = self.bounce_destination(power/2, self.court_position)
        else:
            self.court_position = dest
            #this gives the ball a similar path; this is to continue moving if no player picks up the ball 
            self.destination = self.bounce_destination(power/2, self.court_position)
    
    #this method checks a specific spot on the court to determine if it is out of bounds; it defaults to the ball's position;
    #It returns True if IT IS OUT OF BOUNDS.
    def out_of_bounds_check(self, position):
        if position[0] > 14 or position[1] > 11:
            return True
        elif position[0] < 0 or position[1] < 0:
            return True
        else:
            return False
            
    def box_out_range(self):
        if self.court_position[0] > 3 and self.court_position[0] < 11:
            if self.court_position[1] > 0 and self.court_position[1] < 5:
                return True
            else:
                return False
        else:
            return False
    
    #This function looks to see if it is within box-out range ([3,1],[10,4]); if yes, it looks to see if there is player between basket and the new position;
    #if yes the rebound_script will run, with the closest defender as the outside player
    def rebound(self, court, shot_distance=3):
        self.court_position = [7,1]
        self.destination = [7,1]
        self.bounce(shot_distance)
        self.is_rebound = True
        rebounders = court.players_between(self, self.court_position, [7,1])
        
        if self.box_out_range() == True and len(rebounders) > 0:
            #this is the external rebound function found in Player.py file
            rebound_script(rebounders, court.players)
        
