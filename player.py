import random, math

world_id = 1


directions = {
    'north': [0,1],
    'south': [0,-1],
    'west': [-1,0],
    'east': [1,0],
    'north_west': [-1,1],
    'north_east': [1,1],
    'south_west': [-1,-1],
    'south_east': [1,-1],
    'wait': [0,0]
    }

class Player():
    #This class is designed to give a player the functions needed to operate in the game
    player_id = 0
    team_id = -1
    team_color = 'white'
    
    def __init__(self, id):
        self.player_id = id
    
    #biographical
    first_name = ""
    last_name = ""
    height = 10
    
    #personality
    ballhog =True
    lazy = True
    observent = False
    patient = False
    
    #physical skills of the player
    speed = 5
    jump = 5
    stamina = 5
    strength = 5
    rebound = 5
    hands = 5
    
    #offensive skills
    layup = 5
    dunk = False
    jump_shooting = 5
    three_modifier = 5
    ball_handle = 5
    passing = 5
    shooting_traffic = 5
    post_skill = 5
    
    #defensive skills
    onball_def = 5
    post_def = 5
    steal = 5
    block = 5
    
    #playstyle
    stealer = False
    slasher = False
    point_man = False
    post_man = False
    three_shooter = False
    traffic_shooter = False
    
    #game variables
    has_ball = False
    hot = False
    cold = False
    shot_blocked = False
    court_position = [0,0]
    destination = [0,0]
    face_up = True
    post_up = False
    move_count = 0
    on_defense = False
    def_focus = 0
    post_defender = 0
    
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #The 'Brain'
    
    #these attributes are for the AI; they are collectively called the brain; the ledger 'remembers' the actions taken leading up to the end of a possession
    #so after a possession the actions can be reinforced with the results; the actions list is the list of all possible actions the player can take off ball and keep
    #this is to be used to populate new keys in the dictionaries.
    keep_dict = {}
    pass_dict = {}
    shoot_dict = {}
    defense_dict = {}
    off_ball_dict = {}
    ledger = 0
    post_actions = ['back', 'left', 'right', 'go_to_faceup']
    face_actions = ['go_to_post']
    for x in directions:
        face_actions.append(x)
    
    #This method takes the sense input for passes and returns the expected value for that key; it also adds the key if the key is not present
    def pass_value_retrieve(self, key):
        if key not in self.pass_dict:
            self.pass_dict[key] = (1,1)
        return float(self.pass_dict[key][0])/float(self.pass_dict[key][1])
    
    #this method takes the sense input for shooting and returns the expected value for that key
    def shoot_value_retrieve(self, key):
        if key not in self.shoot_dict:
            self.shoot_dict[key] = (1,1)
        return float(self.shoot_dict[key][0])/float(self.shoot_dict[key][1])
        
    #this method takes the sense input for keep/drive ball and compares all the expected values; it returns the highest expected value and the action corresponding.
    #[action, expected value]
    def keep_value_retrieve(self, key):
        if key not in self.keep_dict:
            start_value = {}
            for action in self.post_actions:
                start_value[action] = (1,1)
            for x in self.face_actions:
                start_value[x] = (1,1)
            self.keep_dict[key] = start_value
        
        current_action = [0,-10000]
        for k,v in self.keep_dict[key].iteritems():
            x_value = float(v[0])/float(v[1])
            if self.post_up == True and k in self.post_actions:
                if current_action[1] < x_value or current_action[1] == 0:
                    current_action[0], current_action[1] = k, x_value
            elif self.post_up == False and k in self.face_actions:
                if current_action[1] < x_value or current_action[1] == 0:
                    current_action[0], current_action[1] = k, x_value
        
        return current_action
        
    #this method is determine the the off_ball key value and actions
    def off_ball_value_retrieve(self, key):
        if key not in self.off_ball_dict:
            start_value = {}
            for action in self.post_actions:
                start_value[action] = (1,1)
            for x in self.face_actions:
                start_value[x] = (1,1)
            self.off_ball_dict[key] = start_value
        
        current_action = [0,-10000]
        for k,v in self.off_ball_dict[key].iteritems():
            x_value = float(v[0])/float(v[1])
            if self.post_up == True and k in self.post_actions:
                if current_action[1] < x_value or current_action[1] == 0:
                    current_action[0], current_action[1] = k, x_value
            elif self.post_up == False and k in self.face_actions:
                if current_action[1] < x_value:
                    current_action[0], current_action[1] = k, x_value
        
        return current_action
        
    #this method is to be used to take the pass_key of the players team-mates and return the highest expected value of the two. It returns the key, player_id of target, 
    #and the expected value. [key, player_id, expected value]
    def pass_expected_value(self, court, ball, shot_clock, time):
        possible = []
        for id,player in court.players.iteritems():
            if player.player_id != self.player_id and player.team_id == self.team_id:
                #appends a list with the [sense_key, player_id]
                possible.append([court.pass_key(self, player, ball, shot_clock, time), player.player_id])
        
        best_opt = 0
        for options in possible:
            options.append(self.pass_value_retrieve(options[0]))
            if best_opt == 0 or options[2] > best_opt[2]:
                best_opt = options
        return best_opt
            
        
    #this is the offensive brain of the player; here is were the sense keys are generated, used to come up with a decision, and then sent to the controller.
    def offense_brain(self, ball, court, shot_clock, time):
        #[identifier, key, action(only for keep), expected value]
        keep = ['keep',0,0,0]
        passs = ['pass',0,0]
        shoot = ['shoot',0,0]
        #generating keys
        keep[1] = court.proximity_key(self, ball, shot_clock, time)
        shoot[1] = court.proximity_key(self, ball, shot_clock, time, True)
        shoot[2] = self.shoot_value_retrieve(shoot[1])
        
        #here I am applying the pass and keep expected values to the comparative lists above.
        keep_act = self.keep_value_retrieve(keep[1])
        keep[2], keep[3] = keep_act[0], keep_act[1]
        
        pass_stuff = self.pass_expected_value(court, ball, shot_clock, time)
        pass_target = pass_stuff[1]
        passs[1], passs[2] = pass_stuff[0], pass_stuff[2]
        
        #print keep[3], passs[2], shoot[2]
        #here is where the program will compare the expected values of the actions and make a decision based on the highest expected value.
        choice = passs
        expected = passs[2]
        if passs[2] > expected and ball.picked_up_dribble == False:
            choice = keep
            expected = keep[3]
        if shoot[2] > expected and ball.team_id_possession == self.team_id:
            choice = shoot
        
        #the decision is being sent to the controller
        if choice[0] == 'keep':
            if choice[2] != 'left' or choice[2] != 'back' or choice[2] != 'right':
                self.off_controller(keep[2], ball, court)
            else:
                self.off_controller('post', ball, court, keep[2])
            self.ledger.append((choice[0],choice[1],choice[2]))
        elif choice[0] == 'pass':
            self.off_controller('pass', ball, court, court.players[pass_target])
            self.ledger.append((choice[0],choice[1]))
        else:
            self.off_controller('shoot', ball, court)
            self.ledger.append((choice[0],choice[1]))
            
    #this is the defensive brain of the player; here the keys are generated, decisions made, and sent to the controller
    def defence_brain(self, ball, court, shot_clock, time):
        opponent = court.players[court.defense_pairs[self.player_id]]
        ball_car = court.players[ball.last_possession]
        key = court.def_key(self, opponent, ball, ball_car, shot_clock, time)
        if key not in self.defense_dict:
            self.defense_dict[key] = {
                'off':(1,1),
                'tight': (1,1),
                'off_ball': (1,1),
                'tight_ball': (1,1)
                }
                
        choice = [0,key,0]
        for key,value in self.defense_dict[key].iteritems():
            x_value = float(value[0])/float(value[1])
            if choice[2] == 0 or x_value > choice[2]:
                choice[0], choice[2] = key, x_value
                
        self.def_controller(choice[0], opponent, ball, court, ball_car)
        self.ledger.append(['defense', choice[1], choice[0]])
        
    #this is the off_ball brain; well you get it...
    def off_ball_brain(self, ball, court, shot_clock, time):
        the_key = court.proximity_key(self, ball, shot_clock, time)
        action = self.off_ball_value_retrieve(the_key)
        if action[0] == 'back' or action[0] == 'left' or action[0] == 'right':
            self.off_ball_controller('post', ball, court, action[0])
        else:
            self.off_ball_controller(action[0], ball, court)
        self.ledger.append(['off_ball', the_key, action[0]])

    #this method is used to take the player's 'ledger' and adds the plays result to the corresponding dictionaries
    def ledger_reader(self, court):
        for event in self.ledger:
            key = event[1]
            new = [0,0]
            old_points = court.points_last
            if event[0] == 'shoot':
                if court.points_last == 0:
                    court.points_last = -1
                new[0], new[1] = self.shoot_dict[key][0] + court.points_last, self.shoot_dict[key][1] + 1
                self.shoot_dict[key] = (int(new[0]),int(new[1]))
            elif event[0] == 'pass':
                if court.points_last > 0:
                    court.points_last += 1
                new[0], new[1] = self.pass_dict[key][0] + court.points_last, self.pass_dict[key][1] + 1
                self.pass_dict[key] = (int(new[0]),int(new[1]))
            elif event[0] == 'defense':
                new[0], new[1] = self.defense_dict[key][event[2]][0] + court.points_last, self.defense_dict[key][event[2]][1] + 1
                self.defense_dict[key][event[2]] = (int(new[0]),int(new[1]))
            elif event[0] == 'off_ball':
                new[0], new[1] = self.off_ball_dict[key][event[2]][0] + court.points_last, self.off_ball_dict[key][event[2]][1] + 1
                self.off_ball_dict[key][event[2]] = (int(new[0]),int(new[1]))
            elif event[0] == 'keep':
                new[0], new[1] = self.keep_dict[key][event[2]][0] + court.points_last, self.keep_dict[key][event[2]][1] + 1
                self.keep_dict[key][event[2]] = (int(new[0]),int(new[1]))
            court.points_last = old_points
            self.ledger = 0
            
            
            
        
    
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #Play Functions
    
    #This is a function to move the player around the court
    #court_position is an two item array 
    #listing the position of the player, i.e. [x,y]
    def move(self, direction):
        self.court_position[0] += directions[direction][0]
        self.court_position[1] += directions[direction][1]
            
    #This is the function to check if a defender steals the ball from the ball_handler        
    def hand_check(self, opponent, ball, court):
        steal_check = random.randint(1,self.steal*2)
        grab_check = random.randint(1,100)
        if steal_check >= opponent.ball_handle:
            opponent.has_ball = False
            ball.is_steal = True
            ball.last_touch = self.player_id
            if self.hands <= grab_check:
                ball.poss_change(self, court)
            else:
                ball.bounce(2,opponent.court_position)
        
            
    #This is the function for the player to pass the ball to a team-mate
    #first a 'pass' check from the player with the ball, to check for a good pass
    #then a 'hand' check to see if the receiver catches the ball
    def pass_ball(self, target, ball, court):
        print 'Pass attempted'
        ball.picked_up_dribble = False
        fate_pass = random.randint(1,60)
        fate_catch = random.randint(1,60)
        self.has_ball = False
        tippers = court.players_between(ball, target.court_position, self.court_position)
        tipped = False
        defender = 0
        for k,v in tippers.iteritems():
            if self.team_id != court.players[v].team_id:
                tipped = court.players[v].tip_pass()
                if tipped == True:
                    defender = court.players[v]
                    break
        
        distance = self.distance_between_players(target)
        if tipped == False:
            ball.assitor = self.player_id
            if fate_pass <= 50 + self.passing/4 + target.hands/4:
                ball.poss_change(target, court)
                ball.court_position[0] = target.court_position[0]
                ball.court_position[1] = target.court_position[1]
                print 'Pass made'
            else:
                #this is for a wayward pass, hence why the focal point is on the passer; this could cause some crazy passes like 15 blocks backwards
                ball.destination[0], ball.destination[1] = self.court_position[0], self.court_position[1]
                ball.court_position[0], ball.court_position[1] = self.court_position[0], self.court_position[1]
                ball.bounce(distance*2,self.court_position)
            '''fate_pass >= 60 - (10-self.passing)
            else:
                if fate_catch < target.hands*3:
                    ball.poss_change(target, court)
                    ball.court_position[0] = target.court_position[0]
                    ball.court_position[1] = target.court_position[1]
                    print 'Pass made'
                else:
                    ball.destination[0], ball.destination[1] = target.court_position[0], target.court_position[1]
                    ball.court_position[0], ball.court_position[1] = target.court_position[0], target.court_position[1]
                    ball.bounce(distance,target.court_position)'''
        else:
            ball.is_steal = True
            ball.last_touch = defender.player_id
            if defender.has_ball == True:
                ball.poss_change(defender, court)
            else:
                distance -= defender.distance_between_players(self)
                ball.destination[0], ball.destination[1] = defender.court_position[0], defender.court_position[1]
                ball.court_position[0], ball.court_position[1] = defender.court_position[0], defender.court_position[1]
                ball.bounce(distance, defender.court_position)
                
    #This is a function for the player to shoot the ball. The basket is at [7,1]
    #the defense_modifier is the opponents height + randint(opponent.jump*0.5, opponent.jump)
    #this is why the player height is subtracted from this number; the shooters
    #height can counter the defenders height. 6/22: replaced defense_modifier with
    #true_modifier from the block_check function; 7/19: Updated the rebounding stuff and changed the layup range to utilize the distance_from_basket method
    def shoot(self, true_modifier, ball, court):
        if self.has_ball == True:
            ball.shot_att = True
            ball.picked_up_dribble = False
            court_modifier = 0
            if self.court_position[1] < 1:
                court_modifier = 25
            else:
                court_modifier = 0
            
            layup_percent = 0    
            if self.dunk == True:
                layup_percent = self.layup + 10
            else:
                layup_percent = self.layup
            
            in_layup = False
            if self.distance_from_basket() < 3:
                in_layup = True
                    
            self.has_ball = False
            if in_layup == True:
                shot_fate = random.randint(1,100)
                if shot_fate <= 35 + layup_percent - true_modifier:
                    #this is a placeholder text
                    print 'Layup made'
                    court.points_last = 1
                else:
                    ball.rebound(court)
            else:
                #Here is the place to put the jumpshot programming lines
                distance_from_basket = self.distance_from_basket()
                if distance_from_basket < 6:
                    shot_fate = random.randint(1,100)
                    if shot_fate <= 20 + self.jump_shooting - court_modifier - true_modifier:
                        #this is a placeholder text
                        print "Jump Shot made"
                        court.points_last = 1
                    else:
                        ball.rebound(court, distance_from_basket)
                else:
                    court_modifier += (7 * (distance_from_basket - 7))
                    shot_fate = random.randint(1,100)
                    if shot_fate <= self.jump_shooting + self.three_modifier - court_modifier - true_modifier:
                        #this is a placeholder text
                        print "Made the Three"
                        court.points_last = 2
                    else:
                        ball.rebound(court, distance_from_basket)
                        
    #This function is to calculate the defensive_modifier against the player
    #that this player is defending; returns the defense_modifier
    #need to add block to somewhere: 6/22: replaced the two_blocks_away boolean
    #with the opponent then a call for distance_between_players to determine
    #if the players a 2 blocks away
    def defense_jump(self, opponent):
        defense_modifier = 0
        distance = self.distance_between_players(opponent)
        if distance < 2:
            defense_modifier = (self.height + random.randint(0, self.jump))*3
        elif distance < 3:
            defense_modifier = (self.height + random.randint(0,self.jump))
            
        return defense_modifier
            
    #this function is for the player to defend the offensive player if he has
    #the ball (or in some instances off-ball defending, like in the post);
    #it keeps the player halfway between the basket and the ball carrier if
    #the ball carrier cannot shoot, if he can than it keeps the defender 75%
    #between the basket and the ball (towards the player, to get in his face);
    #it returns a "destination" for the defender to go to
    def on_ball_destination(self, offense_player, shooter, destination=[7,1]):
        if shooter == True:
            x = destination[0] + round((offense_player.court_position[0] - destination[0])*0.9)
            y = destination[1] + round((offense_player.court_position[1] - destination[1])*0.9)
            destination = [int(x),int(y)]
        else:
            x = destination[0] + round((offense_player.court_position[0] - destination[0])*0.5)
            y = destination[1] + round((offense_player.court_position[1] - destination[1])*0.5)
            destination = [int(x),int(y)]

           
        return destination
        
    #This function will call the on_ball_destination function and proceed to use it in a move_to function; 
    #this function will also call the hand_check function if the offensive player is close enough;
    #takes 3 parameters: offense_player, boolean if the player should be played tight (i.e. if he were a shooter), and the ball function
    def on_ball_d(self, offense_player, ball, court, play_tight=False):
        self.destination = self.on_ball_destination(offense_player, play_tight)
        
        self.move_to(ball, court)
        court.update_player_pos()
        self.def_cutoff(offense_player, ball, court)
        
        if self.distance_between_players(offense_player) < 2 and self.stealer == True:
            self.hand_check(offense_player, ball)
        
        
    #this is a function to determine the distance between two players; this is used
    #for things like hand-check and jump for there distance components
    def distance_between_players(self, other_player, integer=True):
        x = math.sqrt(((self.court_position[0]-other_player.court_position[0])**2)+((self.court_position[1]-other_player.court_position[1])**2))
        if integer == True:
            return int(x)
        else:
            return x
        
    #the players distance from basket
    def distance_from_basket(self):
        return int(math.sqrt(((self.court_position[0]-7)**2)+((self.court_position[1]-1)**2)))
        
    #this is a function to determine the modifier on the shot; this is pulling the
    #'true modifier' portion of the shooting function and making its own, allowing
    #for the incorporation of a blocking mechanic
    def block_check(self, opponent):
        true_modifier = self.defense_jump(opponent) - (opponent.shooting_traffic + opponent.height)
        #print true_modifier
        if true_modifier < 0:
            true_modifier = 0
        
        #this will take the difference between the two modifiers and if it is greater
        #than 20 - block, it will be a block
        if true_modifier >= 25 - self.block:
            #this is to insure that the shot is missed; the shot function needs
            #to be used because a block is a missed shot, so it needs to count
            #as such
            true_modifier = 1000
            #this is to signal the rebound function that the ball has taken the
            #direction of a block, that is to say it probably isn't around the rim
            opponent.shot_blocked = True
        
        if true_modifier < 0:
            true_modifier = 0
        return true_modifier
    
    #this is a function to see if a player is in-between a player passing the ball
    #to another; if he is he attempts to tip the ball away
    def tip_pass(self):
        fate = random.randint(0,100)
        if fate < self.hands:
            if fate < self.hands/2:
                self.has_ball = True
            return True
        else:
            return False
        
                                        
    #This function if for the player to box out his counterpart from the rebound;
    #the player being boxed out cannot advance closer to the basket
    def box_out(self, opponent):
        if self.distance_between_players(opponent) < 2:
            #this is to tell the rebound function that the box-out occurred
            return True
        else:
            return False
            
    #this function is determine if the player is within box_out range; this is not needed with the new rebound format 7/16
    def box_out_range(self):
        if self.court_position[0] > 3 and self.court_position[0] < 11:
            if self.court_position[1] > 0 and self.court_position[1] < 4:
                return True
            else:
                return False
        else:
            return False
            
    #this function is to take the jump and rebound of the player to grab a rebound
    #the strength attributes would be used to make the opponents rebound; the number
    #returned will be compared to the opponents number in an outside rebound function
    def rebound_jump(self, rb_modifier=0):
        x = self.height+self.rebound+random.randint(0,self.jump)-rb_modifier
        if x < 0:
            x = 0
        return x

    #this is the function to set a screen against an opponent; side is a cardinal direction for the 'directions' dictionary;
    #the possible sides can only be the five facing the basket, i.e. south,east,west,south_west,south_east for up top or
    #north, south,west,north_west,south_west for the right corner; this is staying untested, and to be implemented later 7/11/2014
    def screen_player(self, opponent, side):
        self.destination[0] = opponent.court_position[0] + directions[side][0]
        self.destination[1] = opponent.court_position[1] + directions[side][1]
        
    #this function is to move the player from their current position to their destination
    #while checking to see if their are any player is the way; for right now I am presuming
    #that the player will ONLY MOVE ONE BLOCK; 7/13 this function can now operate with a destination greater than one block away
    def move_to(self, ball, court):
        check_array = [0,0]
        check_array[0] = self.destination[0] - self.court_position[0]
        check_array[1] = self.destination[1] - self.court_position[1]

        slope = 0
        x_unit = 1
        if check_array[0] < 0:
            x_unit = -1

        #this is to check if the ball is moving straight forward or backwards; i.e. no change in x
        if check_array[0] != 0:
            slope = check_array[1]/abs(check_array[0])
            if slope > 1:
                slope = 1
            elif slope < -1:
                slope = -1
        else:
            x_unit = 0
            if check_array[1] < 0:
                slope = -1
            elif check_array[1] > 0:
                slope = 1
            else:
                slope = 0

        final_check = [0,0]
        final_check[0] = x_unit
        final_check[1] = int(slope)
        des_check = [0,0]
        des_check[0] = self.court_position[0]+final_check[0]
        des_check[1] = self.court_position[1]+final_check[1]
        if court.spot_open(des_check, ball) == True:
            for x in directions:
                if final_check == directions[x]:
                    self.move(x)
                
            court.update_player_pos()

        if self.has_ball == False:
            self.pick_up_ball(ball, court)
        else:
            ball.update_pos(self.court_position)

    def pick_up_ball(self, ball, court):
        pick_up = False
        if self.court_position == ball.court_position:
            pick_up = True
        else:
            for x in directions:
                if self.court_position[0] + directions[x][0] == ball.court_position[0] and self.court_position[1] + directions[x][1] == ball.court_position[1]:
                    pick_up = True

        if pick_up == True:
            ball.poss_change(self, court)
            
    #This method takes the ball carrier's defender and runs his on_ball_d attribute against the ball carrier's ball_handle to determine if the
    #ball carrier will receive a 1 move advantage; This is from the perspective of the offensive player
    def dribble_move_check(self, opponent):
        if self.distance_between_players(opponent) < 2:
            check = random.randint(1, self.ball_handle) - random.randint(1,opponent.onball_def) 
            if check > 0:
                return True
            else:
                return False   
        else:
            return False
            
    #this method will check to see which player can be hit by a dribble move and adjust his move count to 0 if the dribble check passes; 
    #effectively dropping his jock/putting him on skates.
    def dribble_move(self, ball, court):
        possible = court.players_between(ball, self.court_position)
        if '1' in possible:
            if self.dribble_move_check(court.players[possible['1']]) == True and court.players[possible['1']].def_focus == self.player_id and self.move_count >= court.players[possible['1']].move_count:
                court.players[possible['1']].move_count -= 1
    
    #this method will determine if the player 'jumps' the offensive player successfully; this is from the perspective of the defender
    def def_cutoff_check(self, opponent):
        check = (self.strength/2) + self.onball_d - opponent.strength - random.randint(1, opponent.ball_handle)
        if check >= 0:
            return True
        else:
            return False
            
    #this method is used to determine if the offensive player is forced to pick up the ball from dribble after his counter part has jumped him; this if from
    #the perspective of the offensive player
    def pick_up_dribble_check(self, opponent):
        check = self.strength - opponent.strength - (10 - random.randint(0, self.ball_handle))
        if check >= 0:
            return False
        else:
            return True
            
    #this method is to determine if a player can attempt a defensive cut-off of his opponent; if the initial check passes than a second check is attempted to determine if the
    #dribble has be picked up; this can only be attempted if the offensive player has the ball. If the cut-off passes the focus' move_count is set to 0; effectively stone-walling
    #and keeping him out of the defender's house.
    def def_cutoff(self, focus, ball, court):
        if focus.has_ball == True and self.move_count >= focus.move_count:
            possible = court.players_between(ball, focus.court_position)
            if '1' in possible:
                if possible['1'] == self.player_id and self.distance_between_players(focus) < 2:
                    if self.def_cutoff_check(focus) == True:
                        focus.move_count -= 1
                        if focus.pick_up_dribble_check(self) == True:
                            ball.picked_up_dribble = True
                            
            
    #this method will take the player and the opponent to determine if the player successfully backs-down the defender; this is used while in post-up mode
    def back_down_check(self, opponent):
        check = random.randint(1, self.strength) - random.randint(1, opponent.strength)
        if check > 0:
            return True
        else:
            return False
            
    #this method will take the player and the defender to determine if the player uses speed in the post to beat his opponent, ala Hakeem; this is used while in post-up mode
    def speed_post_check(self, opponent):
        check = (self.post_skill + random.randint(1, self.speed)) - (opponent.post_def + random.randint(1, opponent.speed))
        if check > 0:
            return True
        else:
            return False
            
    #This method actually proceeds with the player backing down the opponent
    def back_down(self, opponent, ball, court):
        difference = [opponent.court_position[0] - self.court_position[0], opponent.court_position[1] - self.court_position[1]]
        the_direction = ' '
        for direction in directions:
            if directions[direction] == difference:
                the_direction = direction
                
        test_spot = [opponent.court_position[0] + directions[the_direction][0], opponent.court_position[1] + directions[the_direction][1]]
        
        if court.spot_open(test_spot, ball) and self.back_down_check(opponent):
            opponent.move(the_direction)
            self.move(the_direction)
            
    #This method takes the players current position along with the defenders position and determines which directions key is correlated with back_down,
    #spin right, spin left post moves
    def post_possible(self, opponent):
        if self.distance_between_players(opponent) < 2:
            post_poss = {
                'back': 0,
                'right': 0,
                'left': 0
                }
                
            back_d = [opponent.court_position[0] - self.court_position[0], opponent.court_position[1] - self.court_position[1]]
            for direction,code in directions.iteritems():
                if code == back_d:
                    post_poss['back'] = direction
            
            if back_d[0] == 0:
                for direction,code in directions.iteritems():
                    if code == [-1, back_d[1]]:
                        post_poss['right'] = direction
                    if code == [1, back_d[1]]:
                        post_poss['left'] = direction
            elif back_d[1] == 0:
                for direction,code in directions.iteritems():
                    if code == [back_d[0], -1]:
                        post_poss['right'] = direction
                    if code == [back_d[0], 1]:
                        post_poss['left'] = direction
            else:
                for direction,code in directions.iteritems():
                    if code == [back_d[0], 0]:
                        post_poss['right'] = direction
                    if code == [0, back_d[1]]:
                        post_poss['left'] = direction
            
            return post_poss
        else:
            return False
            
    #This method is to switch the player from face_up mode to post_up mode, and vice versa
    def switch_up(self):
        self.face_up, self.post_up = self.post_up, self.face_up
        
    #this method checks if the opponent of the offense_player is within post up range to post-up
    def go_post(self, ball, court):
        _temp = court.players_between(ball, self.court_position)
        for k,v in _temp.iteritems():
            if court.players[v].def_focus == self.player_id and self.distance_between_players(court.players[v]) < 2:
                self.post_defender = v
                self.switch_up()
        
    #This method is to take the player, opponent, and a post direction (back, left, right) and process this into a movement; with a return
    #value on the speed post moves to determine mimicry.
    def post_move(self, the_move, ball, court):
        opponent = court.players[self.post_defender]
        moves = self.post_possible(opponent)
        if moves != False:
            speed_move = False
            if the_move == 'back':
                self.back_down(opponent, ball, court)
            else:
                self.destination[0] = self.court_position[0] + directions[moves[the_move]][0]
                self.destination[1] = self.court_position[1] + directions[moves[the_move]][1]
                if court.spot_open(self.destination, ball):
                    self.move_to(ball, court)
                    speed_move = self.speed_post_check(opponent)
                    return speed_move
            
    #this method is for the chasing of the ball
    def chase_ball(self, ball, court):
        self.destination[0] = ball.court_position[0]
        self.destination[1] = ball.court_position[1]
        self.move_to(ball, court)
        
    #This method is the controller of the players action; that is to say the 'brain' will output a string which will then go into this method
    #where the corresponding action will be executed.
    def off_controller(self, command, ball, court, sub_command=None):
        if command in directions:
            self.destination[0] = self.court_position[0] + directions[command][0]
            self.destination[1] = self.court_position[1] + directions[command][1]
            self.move_to(ball, court)
            self.dribble_move(ball, court)
        elif command == 'post':
            if self.post_up == True:
                return self.post_move(sub_command, ball, court)
        elif command == 'go_to_post':
            if self.post_up == False:
                self.go_post(ball, court)
        elif command == 'go_to_faceup':
            if self.face_up == False:
                self.switch_up()
        elif command == 'shoot':
            defense = court.defense_modifier(self)
            self.shoot(defense, ball, court)
        elif command == 'pass':
            self.pass_ball(sub_command, ball, court)
            
    #this method is the controller for the defensive actions; it also sets which player the defender is focusing on, making them susceptible to dribble moves.
    def def_controller(self, command, opponent, ball, court, ball_handler=None):
        if command == 'off':
            self.def_focus = opponent.player_id
            self.on_ball_d(opponent, ball, court)
        elif command == 'tight':
            self.def_focus = opponent.player_id
            self.on_ball_d(opponent, ball, court, True)
        elif command == 'ball_off':
            self.def_focus = ball_handler.player_id
            self.on_ball_d(ball_handler, ball, court)
        elif command == 'ball_tight':
            self.def_focus = ball_handler.player_id
            self.on_ball_d(ball_handler, ball, court, True)
            
    #this method is the controller for the off_ball actions of a player
    def off_ball_controller(self, command, ball, court, sub_command=None):
        if command in directions:
            self.destination[0] = self.court_position[0] + directions[command][0]
            self.destination[1] = self.court_position[1] + directions[command][1]
            self.move_to(ball, court)
        elif command == 'post':
            if self.post_up == True:
                return self.post_move(sub_command, ball, court)
        elif command == 'go_to_post':
            if self.post_up == False:
                self.go_post(ball, court)
        elif command == 'go_to_faceup':
            if self.face_up == False:
                self.post_defender = 0
                self.switch_up
        
        
        
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

#Independent Functions       
    
    
    
    
    
#this function is to to see if a player and his counterpart are within the typical 
#rebound zone, i.e. near the basket; if they are it proceeds through the box-out function
#and compares the two rebound_jumps to determine which player comes out with the ball;
#this is the first appearance of the players global dictionary in the game 7/16/2014
def rebound_script(rebounders, ball, court):
    insidepl = court.players[rebounders[1]]
    outsidepl = False
    if 2 in rebounders:
        outsidepl = court.players[rebounders[2]]
    
    boxed_out = False
    if outsidepl != False:
        boxed_out = insidepl.box_out(outsidepl)
        
    
    #this portion of the function is for the outside player to 'fight' in front of 
    #the box-out, becoming the inside player
    if boxed_out == True:
        if insidepl.strength + 8 < outsidepl.strength + random.randint(0, outsidepl.speed):
            #this is the flipping for the local variables
            insidepl = court.players[rebounders[2]]
            outsidepl = court.players[rebounders[1]]
            #This flips the court position of the two players, in order for the rendering and position stuff
            outsidepl.court_position, insidepl.court_position = insidepl.court_position, outsidepl.court_position
            
            
        
    reb_modifier = 0
    if boxed_out == True:
        reb_modifier = 10
        
        
    reb_check = 0
    if boxed_out == False:
        ball.poss_change(insidepl, court)
    else:
        reb_check += insidepl.rebound_jump()
        reb_check -= outsidepl.rebound_jump(reb_modifier)
        
    if reb_check >= 0:
        ball.poss_change(insidepl, court)
    else:
        ball.poss_change(outsidepl, court)