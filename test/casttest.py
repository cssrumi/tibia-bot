from pynput.keyboard import Key

from cast import Cast
from ctx.player import Player

cast = Cast(Key.f1, min_health=50, min_mana=100)
player = Player(health=40, mana=100)
assert cast.should_cast(player)

player = Player(health=60, mana=100)
assert not cast.should_cast(player)

player = Player(health=40, mana=90)
assert cast.should_cast(player)
