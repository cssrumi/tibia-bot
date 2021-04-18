from pynput.keyboard import Key

from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.window import WindowStateManagerTask
from domain.game.game import Game


def functional_scala():
    game = Game('Tibia - Functional Scala')

    wsmt = WindowStateManagerTask(game, delay=0)
    game.add_task(wsmt)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    spells = [Spell(Key.f1, min_mana=10, min_health=90)]
    potions = [
        Potion(Key.f4, min_mana=70, priority=1),
        Potion(Key.f5, min_health=70),
        Potion(Key.f6, min_health=40),
        Potion(Key.f7, min_health=20),
    ]
    ht = HealerTask(game, psm, spells=spells, potions=potions)
    game.add_task(ht)

    et = ExchangeTask(game, psm, wsmt)
    game.add_task(et)

    mtt = MagicTrainingTask(game, psm, key=Key.f11, min_mana=90)
    game.add_task(mtt)

    fet = FoodEaterTask(game, key=Key.f9)
    game.add_task(fet)

    return game


def deidara():
    game = Game('Tibia - Deidara')

    wsmt = WindowStateManagerTask(game, delay=0)
    game.add_task(wsmt)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    spells = [
        Spell(Key.f1, min_mana=1, min_health=92),
        Spell(Key.f2, min_mana=2, min_health=65),
        Spell(Key.f3, min_mana=6, min_health=50),
    ]
    potions = [
        Potion(Key.f4, min_mana=70)
    ]
    ht = HealerTask(game, psm, spells=spells, potions=potions)
    game.add_task(ht)

    mtt = MagicTrainingTask(game, psm, key=Key.f2, min_mana=85)
    game.add_task(mtt)
    # mana_burn = MagicTrainingTask(game, psm, key='i', min_mana=50)
    # game.add_task(mana_burn)

    et = ExchangeTask(game, psm, wsmt)
    game.add_task(et)

    fet = FoodEaterTask(game, key=Key.f9)
    game.add_task(fet)

    return game


def main():
    # game = functional_scala()
    game = deidara()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
