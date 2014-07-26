from ball_class import Ball
from court import Court
from player import Player, directions, world_id, rebound_script

bob = Player(world_id)
world_id += 1

"""print bob.face_up, bob.post_up
bob.switch_up()
print bob.face_up, bob.post_up"""

tom = Player(world_id)
ball = Ball()
court = Court()

bob.court_position = [7,4]
tom.court_position = [7,3]

print bob.post_move(tom, 'back', ball, court)
print bob.court_position

