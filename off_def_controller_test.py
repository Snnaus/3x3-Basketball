from player import *
from ball_class import *
from court import *

ball = Ball()
court = Court()


for x in range(2):
    for z in range(2):
        court.players[world_id] = Player(world_id)
        court.players[world_id].team_id, court.players[world_id].court_position = x+1, [7, world_id+2]
        world_id += 1

bob = 0
tom = 0
kirsti = 0
bob, tom, kristi = court.players[1], court.players[2], court.players[3]
tom.court_position[1] = 8
kristi.court_position = [1,1]
bob.court_position = [10,3]

court.update_player_pos()
court.print_court()


for x in range(6):
    kristi.def_controller('tight', tom, ball, court)
    #print bob.destination
    court.update_player_pos()
    court.print_court()

for x in range(6):
    kristi.def_controller('ball_tight', tom, ball, court, bob)
    #print bob.destination
    court.update_player_pos()
    court.print_court()

kristi.court_position = [1,1]
for x in range(6):
    kristi.def_controller('ball_tight', tom, ball, court, bob)
    #print bob.destination
    court.update_player_pos()
    court.print_court()
