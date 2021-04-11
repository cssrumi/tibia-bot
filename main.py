from pynput.keyboard import Key

from state.game import Game
from state.player import PlayerStateManager
from state.window import Window
from task.foodeater import FoodEater
from task.magictraining import MagicTraining


def main():
    game = Game('Tibia - Functional Scala')

    window = Window(game, delay=0)
    game.add_task(window)

    player = PlayerStateManager()
    window.add_update_listener(player.window_listener)

    m_training = MagicTraining(game, player, key=Key.f11, min_mana=80)
    game.add_task(m_training)

    food_eater = FoodEater(game, key=Key.f9)
    game.add_task(food_eater)

    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
