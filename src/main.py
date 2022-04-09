from typing import List, Tuple

from pynput.keyboard import Key

from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.stoneskin import StoneSkinStateManager, StoneSkinImageListener, StoneSkinInvoker
from ctx.window import WindowStateManagerTask
from domain.game.game import Game


def mietar(heavy=False):
    def heavy_healing() -> Tuple[List[Spell], List[Potion]]:
        heavy_spells = [
            Spell(Key.f1, min_mana=3, min_health=95),
            Spell(Key.f2, min_mana=6, min_health=88),
            Spell(Key.f3, min_mana=10, min_health=80),
        ]
        heavy_potions = [
            Potion(Key.f4, min_mana=70),
            Potion(Key.f5, min_health=70, priority=-1),
            Potion(Key.f6, min_health=85),
        ]
        return heavy_spells, heavy_potions

    def default_healing() -> Tuple[List[Spell], List[Potion]]:
        default_spells = [
            Spell(Key.f2, min_mana=6, min_health=90),
            Spell(Key.f3, min_mana=10, min_health=80),
        ]
        default_potions = [
            Potion(Key.f4, min_mana=70),
            Potion(Key.f5, min_health=60, priority=-1),
            Potion(Key.f6, min_health=70),
        ]
        return default_spells, default_potions

    game = Game('Tibia - Mietar')

    wsmt = WindowStateManagerTask(game, delay=0)
    game.add_task(wsmt)

    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    spells, potions = heavy_healing() if heavy else default_healing()

    ht = HealerTask(game, psm, spells=spells, potions=potions)
    game.add_task(ht)

    # sssm = StoneSkinStateManager()
    # ssi = StoneSkinInvoker(game, psm, key=Key.f12, equip_at=30)
    # sssm.add_update_listener(lambda state: ssi.invoke(state.value))
    # ssl = StoneSkinImageListener(sssm, ssi)
    # wsmt.add_update_listener(ssl.update_listener)

    mtt = MagicTrainingTask(game, psm, key=Key.f3, min_mana=90)
    game.add_task(mtt)

    fet = FoodEaterTask(game, key=Key.f9)
    game.add_task(fet)

    et = ExchangeTask(game, psm, wsmt)
    game.add_task(et)

    return game


def main():
    game = mietar()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
