import random, math
from tkinter_stuff import *
from player import *



class Court:
    #This class is designed to give a dictionary of all the potential court positions; it will hold the players ID in the box that the player is in;
    #This is the 'Board'
    positions = {}
    
    #This is a dictionary of Players on the court; This is where the player objects will be held for the simulation.
    #I need to add a method which populates this; I also need a way to identify whose on which team and whose on the court and whose a sub,
    #but these may be added later once I get to the point of adding teams 
    players = {}
    
    #this is a dictionary telling the game which player is defending which; the dictionary key is the team_id, which will lead to the dictionary of
    #the specific team; the key for that dictionary is the player_id, the value is the player_id of the player he is defending.
    defense_pairs = {}
    
    #this dictionary is for each teams respective point guard; the key will relate to the players team_id and the value will be the players id
    point_guards = {}
    
    #this attribute tells the game how many points the last possession generated.
    points_last = 0
    score = 0
    
    #this is filling the dictionary with the position keys, AKA 'the board'; I had to make this bigger because of a keyerror when rebounds went out of bounds
    def __init__(self):
        for x in range(15):
            for y in range(12):
                self.positions[x,y] = 0
            
    #this function receives and array 'spot', which are coordinates (i.e. court_position); it then converts those coordinates to a tuple and checks if the spot is == to zero or ball
    #in the positions hash; returning True or False respectively
    def spot_open(self, spot, ball):
        is_open = False
        the_spot = spot[0],spot[1]
        
        if ball.out_of_bounds_check(spot) == False:
            if self.positions[the_spot] == 0 or self.positions[the_spot] == 'B':
                is_open = True
            
        return is_open
        
    #this method is for the sensory keys of the brains, specifically the 9 court positions. This takes a players court_position as the parameter/input.
    def nine_court_key(self, spot):
        if spot[0] <= 1:
            if spot[1] <= 3:
                return 1
            elif spot[1] <= 8:
                return 6
            else:
                return 9
        elif spot[0] <= 4:
            if spot[1] <= 3:
                return 2
            elif spot[1] <= 8:
                return 6
            else:
                return 9
        elif spot[0] <= 9:
            if spot[1] <= 3:
                return 3
            elif spot[1] <= 8:
                return 7
            else:
                return 'A'
        elif spot[0] <= 12:
            if spot[1] <= 3:
                return 4
            elif spot[1] <= 8:
                return 8
            else:
                return 'B'
        elif spot[0] <= 14:
            if spot[1] <= 3:
                return 5
            elif spot[1] <= 8:
                return 8
            else:
                return 'B'
    
    #this method is to create the proximity sensory key. It takes the players court_position as the input. This is for the offensive and off_ball controllers.
    def proximity_key(self, player, ball, shot_clock, time, shot=False):
        key = ''
        key = key + str(self.nine_court_key(player.court_position))
        if shot == False:
            for k,v in directions.iteritems():
                test_position = [0,0]
                test_position[0] = player.court_position[0] + v[0]
                test_position[1] = player.court_position[1] + v[1]
                digit = self.spot_open(test_position, ball)
                if digit == True:
                    key = key + '1'
                else:
                    key = key + '0'
        else:
            for k,v in directions.iteritems():
                test_position = [0,0]
                test_position[0] = player.court_position[0] + v[0]
                test_position[1] = player.court_position[1] + v[1]
                digit = self.spot_open(test_position, ball)
                if (test_position[0], test_position[1]) in self.positions:
                    if digit == True:
                        key = key + '1'
                    else:
                        if self.positions[test_position[0],test_position[1]] != 0:
                            if player.team_id == self.players[self.positions[test_position[0],test_position[1]]].team_id:
                                key = key + '1'
                            else:
                                key = key + '0'
                        else:
                            key = key + '0'
                else:
                    key = key + '0'
        key = self.ball_key(player, ball, key)
        key = self.time_key(shot_clock, time, key)
        return key
            
    
    #this method is used to attach the time portion of the sense key
    def time_key(self, shot_clock, time, key):
        key_time = 0
        if shot_clock < time:
            key_time = shot_clock
        else:
            key_time = time
            
        digit = '3'
        if key_time <= 8:
            digit = '2'
        elif key_time <= 4:
            digit = '1'
        elif key_time <= 1:
            digit = '0'
            
        return key + digit
    
    #this method looks to see if the the ball needs to be cleared and if the ball has been picked up; then attaches it to the key.
    def ball_key(self, player, ball, key):
        picked = '0'
        clear = '0'
        if ball.picked_up_dribble == True:
            picked = '1'
        if player.team_id == ball.team_id_possession:
            clear = '1'
        return key + clear + picked
        
    #this is a test for the off_ball brain key.
    def off_key(self, player, ball, shot_clock, time):
        key = ''
        for id, dude in self.players.iteritems():
            if player.team_id != dude.team_id:
                key = key + str(self.nine_court_key(dude.court_position))
        key = key + str(self.nine_court_key(player.court_position))
        key = self.ball_key(player, ball, key)
        key = self.time_key(shot_clock, time, key)
        return key
    
    #this method is to generate the passing sense key.
    def pass_key(self, player, receiver, ball, shot_clock, time):
        key = str(self.nine_court_key(player.court_position)) + str(self.nine_court_key(receiver.court_position))
        between = self.players_between(ball, receiver.court_position, player.court_position)
        between_bin = '0'
        for k,v in between.iteritems():
            if self.players[v].team_id != player.team_id:
                between_bin = '1'
                break
        key = key + between_bin
        key = self.ball_key(player, ball, key)
        key = self.time_key(shot_clock, time, key)
        return key
     
    #this method is to generate the defensive sense key.
    def def_key(self, player, opponent, ball, ball_car, shot_clock, time):
        key = str(self.nine_court_key(player.court_position)) + str(self.nine_court_key(opponent.court_position)) + str(self.nine_court_key(ball_car.court_position))
        key = self.ball_key(player, ball, key)
        return self.time_key(shot_clock, time, key)
        
    #This function takes two inputs relating to two positions on the court; it will then return the number or players between those two positions and the ids of the players;
    #this is used for the rebounding script, and potentially the tip pass function; the players id is stored in a dictionary, with the first key being the inside player and
    #the second being the outside player
    def players_between(self, ball, new_position, start_position=[7,1]):
        in_out = {}
    
        x_distance = new_position[0] - start_position[0]
        y_distance = new_position[1] - start_position[1]
        slope = 1
        x_unit = 1
        if x_distance != 0:
            slope = float(new_position[1] - start_position[1]) / float(abs(x_distance))
            if x_distance < 0:
                x_unit = -1
        else:
            x_unit = 0
            x_distance = y_distance
            if new_position[1] - start_position[1] < 0:
                slope = -1
        
        test_position = [0,0]
        test_position[0] = start_position[0]
        test_position[1] = start_position[1]
        player_count = 0
        for x in range(1,abs(x_distance)+1):
            test_position[0] += x_unit
            test_position[1] += int(round(slope))
            if tuple(test_position) in self.positions:
                if self.spot_open(test_position, ball) == False and player_count < 3:
                    player_count = player_count + 1
                    id = self.positions[test_position[0],test_position[1]]
                    in_out[player_count] = id
                    
        return in_out
        
    #This method is used to update a players position to the board; This needs to be done on a per player basis because of the independent movement of the players in the script;
    #this is only for players, the ball will need its own separate method; as of 7/19 this function looks at all the players in the player dictionary and updates their position
    def update_player_pos(self):
        for x in self.players:
            #taking the necessary information in order to update the board
            id = self.players[x].player_id
            new_pos = self.players[x].court_position[0],self.players[x].court_position[1]
            
            #this is setting the current position of the player to zero on the board
            for z in self.positions:
                if self.positions[z] == id:
                    if z == (7,1):
                        self.positions[z] = 'B'
                    else:
                        self.positions[z] = 0
            
            #this is setting the players new position to the board
            self.positions[new_pos] = id
            
    
    #this method is to take all the players in the players dict and roll for their initiative and sort them in order; this leads into the turn function that will take the order 
    #and proceed with the logic of the game. it returns a key for the order and player_id as the value.
    def initiative_roll(self):
        init_rolls = {}
        the_order = {}
        count = 0
        #this generates the initiative rolls for the players
        for player in self.players:
            count += 1
            init_roll = random.randint(1,self.players[player].speed)
            init_rolls[self.players[player].player_id] = init_roll
        
        #here I am sorting the initiative rolls in order, highest to lowest
        for x in range(1,7):
            current_leader = [0,0]
            for z in init_rolls:
                if init_rolls[z] > current_leader[1]:
                    current_leader[0] = z
                    current_leader[1] = init_rolls[z]
                    
            
            the_order[x] = current_leader[0]
            init_rolls[current_leader[0]] = -5
            
        
        return the_order
        
    #this method looks for the closest player to a loose ball from each team and then sets them to move towards the ball
    def loose_ball_chase(self, ball):
        team_a_chaser = 0
        team_b_chaser = 0
        for k,v in self.players.iteritems():
            if team_a_chaser == 0:
                team_a_chaser = v
            elif team_b_chaser == 0 and v.team_id != team_a_chaser.team_id:
                team_b_chaser = v
            elif team_a_chaser != 0 and team_a_chaser.team_id == v.team_id:
                if team_a_chaser.distance_between_players(ball, False) > v.distance_between_players(ball, False):
                    team_a_chaser = v
            elif team_b_chaser != 0 and team_b_chaser.team_id == v.team_id:
                if team_b_chaser.distance_between_players(ball, False) > v.distance_between_players(ball, False):
                    team_b_chaser = v
        
        if team_a_chaser.speed > team_b_chaser.speed:
            team_a_chaser.chase_ball(ball, self)
            team_b_chaser.chase_ball(ball, self)
        else:
            team_b_chaser.chase_ball(ball, self)
            team_a_chaser.chase_ball(ball, self)
            
            
    #This method is to look at every player on the court and add together their block checks to determine the true_modifier on a players shot
    def defense_modifier(self, shooter):
        the_num = 0
        for k,v in self.players.iteritems():
            if the_num < 1000 and v.team_id != shooter.team_id:
                the_num += v.block_check(shooter)
                
        return the_num
        
        
    #This method is to be used to print the court
    def print_court(self):
        total = ''
        up_low_bound = ' '
        for x in range(15):
            up_low_bound = up_low_bound + '--'
        up_low_bound = up_low_bound + ' \n'
        total = total + up_low_bound
        for y in range(12):
            line = '|'
            for x in range(15):
                if self.positions[x,y] != 0:
                    line = line + str(self.positions[x,y]) + ' '
                elif self.distance_from_basket([x,y]) == 6:
                    line = line + 'Th'
                else:
                    line = line + '  '
            line = line + '|\n'
            total = total + line
        total = total + up_low_bound
        return total
        
    #this method is to return the distance from the basket a certain point is; this may replace the players function
    def distance_from_basket(self, spot):
        return int(math.sqrt(((spot[0]-7)**2)+((spot[1]-1)**2)))
        
    #this method is for the tk animator
    def tk_frame(self):
        map = []
        for x in range(15):
            row = []
            for y in range(12):
                if self.positions[x,y] != 0:
                    row.append(self.positions[x,y])
                elif x == 7 and y == 1:
                    row.append('B')
                elif self.distance_from_basket([x,y]) == 6:
                    row.append('Th')
                elif x >= 5 and x <= 9:
                    if y >= 0 and y <= 5:
                        row.append('Pa')
                    else:
                        row.append(self.positions[x,y])
                else:
                    row.append(self.positions[x,y])
            map.append(row)
        return map
        
    #this method is to reset the players to a default position during the game; only at the start of the game, after on floor fouls, and after out of bounds
    def player_reset(self, ball, sequence):
        team = ball.team_id_possession
        one = self.players[self.point_guards[team]]
        two = 0
        three = 0
        for id,player in self.players.iteritems():
            if player.team_id == team and two == 0 and player.player_id != one.player_id:
                two = player
                player.on_defense = False
            elif player.team_id == team and three == 0 and player.player_id != one.player_id:
                three = player
                player.on_defense = False
                break
        one.court_position, two.court_position, three.court_position = [7,9], [13,7], [1,7]
        for id,teams in self.defense_pairs.iteritems():
            if id != team:
                defense = self.defense_pairs[id]
                new_position = {}
                for defender,offense in defense.iteritems():
                    self.players[defender].court_position = self.players[defender].on_ball_destination(self.players[offense],False)
        
        self.update_player_pos()
        sequence.append(self.tk_frame())
        for id,player in self.players.iteritems():
            player.has_ball = False
            if player.player_id == self.point_guards[team]:
                player.has_ball = True
                player.on_defense = False
                ball.possession = True
                ball.last_possession = player.player_id
                ball.last_touch = player.player_id
        
        
        
    #this method is to set each players move_count for the turn
    def set_move_count(self):
        highest = 0
        for id,player in self.players.iteritems():
            player.move_count = round(player.speed/4)
            if player.move_count > highest:
                highest = player.move_count
                
        return highest
            
    #this method is for the 'second' mechanic; a second (which represents the unit of time) is a bundle of turns by the players
    #this method executes those turns
    def game_second(self, ball, sequence, shot_clock, time):
        if ball.possession == False:
            for x in range(2):
                self.loose_ball_chase(ball)
        else:
            order = self.initiative_roll()
            turn_count = self.set_move_count()
            while True:
                ball.clear_out_check(self)
                for x in range(1,7):
                    #this gate is to check if the player is fast enough the move at this turn.
                    if self.players[order[x]].move_count >= turn_count:
                        current_player = self.players[order[x]]
                        if current_player.has_ball == True:
                            current_player.offense_brain(ball, self, shot_clock, time)
                        elif current_player.on_defense == True:
                            current_player.defence_brain(ball, self, shot_clock, time)
                        else:
                            current_player.off_ball_brain(ball, self, shot_clock, time)
                        self.update_player_pos()
                        current_player.move_count -= 1
                sequence.append(self.tk_frame())
                turn_count -= 1
                if turn_count <= 0:
                    break
                        
    #this is the game method; here where the game loop is found
    def game(self, ball, sequence):
        self.score = 0
        #the games last 10 mins(600 secs) with no half time
        seconds = 1200
        #this is to determine the team who starts with the ball at the beginning of the game; simulates a coin flip
        chance = random.randint(1,100)
        chance_count = 0
        for id,player in self.players.iteritems():
            player.brain_reset()
        for team in self.point_guards:
            if chance <= 50 + (chance_count*50):
                ball.team_id_possession = team
            chance_count += 1
        
        #sequence = []
        shot_clock_violation = False
        out_bounds = 0
        ball.turnt_over = False
        while True:
            #there is a 12 second shot clock
            shot_clock = 12
            self.points_last = 0
            ball.shot_att = False
            
            if shot_clock_violation == True or out_bounds == True or seconds == 1200:
                if shot_clock_violation == True or out_bounds == True:
                    for team in self.point_guards:
                        if team != self.players[ball.last_touch].team_id:
                            ball.team_id_possession = team
                            break
                self.player_reset(ball, sequence)
            shot_clock_violation = False
            out_bounds = False
            ball.turnt_over = False
            for id, player in self.players.iteritems():
                player.ledger = []
            while True:
                self.game_second(ball, sequence, shot_clock, seconds)
                out_bounds = ball.out_of_bounds_check(ball.court_position)
                shot_clock -= 1
                seconds -= 1
                if shot_clock <= 0:
                    shot_clock_violation = True
                    break
                elif seconds <= 0 or ball.turnt_over == True or out_bounds == True:
                    break
            for id,player in self.players.iteritems():
                player.ledger_reader(self)
                self.score += self.points_last
            if seconds <= 0:
                break
        print len(sequence)
        #animation = Court_Animation(sequence, self)   