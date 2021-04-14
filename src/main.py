from pynput.keyboard import Key

from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEater
from ctx.healer import Healer, Spell, Potion
from ctx.magictraining import MagicTraining
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.window import Window
from game.game import Game


def functional_scala():
    game = Game('Tibia - Functional Scala')

    window = Window(game, delay=0)
    game.add_task(window)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    window.add_update_listener(pil.update_listener)

    spells = [Spell(Key.f1, min_mana=10, min_health=90)]
    potions = [
        Potion(Key.f4, min_mana=70, priority=1),
        Potion(Key.f5, min_health=70),
        Potion(Key.f6, min_health=40),
        Potion(Key.f7, min_health=20),
    ]
    healer = Healer(game, psm, spells=spells, potions=potions)
    game.add_task(healer)

    gp_exchange = ExchangeTask(game, psm, window)
    game.add_task(gp_exchange)

    m_training = MagicTraining(game, psm, key=Key.f11, min_mana=90)
    game.add_task(m_training)

    food_eater = FoodEater(game, key=Key.f9)
    game.add_task(food_eater)

    return game


def deidara():
    game = Game('Tibia - Deidara')

    window = Window(game, delay=0)
    game.add_task(window)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    window.add_update_listener(pil.update_listener)

    m_training = MagicTraining(game, psm, key=Key.f2, min_mana=90)
    game.add_task(m_training)

    food_eater = FoodEater(game, key=Key.f9)
    game.add_task(food_eater)

    return game


def main():
    # game = functional_scala()
    game = deidara()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
