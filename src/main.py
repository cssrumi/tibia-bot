from typing import List, Tuple

from pynput.keyboard import Key

from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.stoneskin import StoneSkinStateManager, StoneSkinListener, StoneSkinInvoker
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
        Spell(Key.f1, min_mana=1, min_health=95),
        Spell(Key.f2, min_mana=2, min_health=70),
        Spell(Key.f3, min_mana=6, min_health=55),
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


def paler(heavy=False):
    def heavy_healing() -> Tuple[List[Spell], List[Potion]]:
        heavy_spells = [
            Spell(Key.f1, min_mana=3, min_health=92),
            Spell(Key.f2, min_mana=6, min_health=87),
            Spell(Key.f3, min_mana=10, min_health=75),
        ]
        heavy_potions = [
            Potion(Key.f4, min_mana=70),
            Potion(Key.f5, min_health=70, priority=-1),
            Potion(Key.f6, min_health=85),
        ]
        return heavy_spells, heavy_potions

    def default_healing() -> Tuple[List[Spell], List[Potion]]:
        default_spells = [
            Spell(Key.f1, min_mana=3, min_health=88),
            Spell(Key.f2, min_mana=6, min_health=75),
            Spell(Key.f3, min_mana=10, min_health=50),
        ]
        default_potions = [
            Potion(Key.f4, min_mana=70),
            Potion(Key.f5, min_health=50, priority=-1),
            Potion(Key.f6, min_health=70),
        ]
        return default_spells, default_potions

    game = Game('Tibia - Paler')

    wsmt = WindowStateManagerTask(game, delay=0)
    game.add_task(wsmt)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    spells, potions = heavy_healing() if heavy else default_healing()

    ht = HealerTask(game, psm, spells=spells, potions=potions)
    game.add_task(ht)

    sssm = StoneSkinStateManager()
    ssi = StoneSkinInvoker(game, psm, key=Key.f12, equip_at=30, skip_cycle=2)

    ssl = StoneSkinListener(sssm, ssi)
    wsmt.add_update_listener(ssl.update_listener)

    mtt = MagicTrainingTask(game, psm, key=Key.f2, min_mana=90)
    game.add_task(mtt)

    fet = FoodEaterTask(game, key=Key.f9)
    game.add_task(fet)

    et = ExchangeTask(game, psm, wsmt)
    game.add_task(et)

    return game


def paler_ss_test():
    game = Game('Tibia - Paler')

    wsmt = WindowStateManagerTask(game, delay=0)
    game.add_task(wsmt)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    sssm = StoneSkinStateManager()
    ssi = StoneSkinInvoker(game, psm, key=Key.f12, equip_at=100)
    ssl = StoneSkinListener(sssm, ssi)
    wsmt.add_update_listener(ssl.update_listener)

    return game


def main():
    # game = functional_scala()
    # game = deidara()
    game = paler()
    # game = paler_ss_test()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
