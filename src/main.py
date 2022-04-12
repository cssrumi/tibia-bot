from pynput.keyboard import Key

from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, AttackSpell, AttackRune, ComboSwitch
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.window import WindowStateManagerTask
from domain.game.game import Game


def mietar():
    spells = [
        Spell(Key.f2, min_mana=6, min_health=90),
        Spell(Key.f3, min_mana=10, min_health=80),
    ]
    potions = [
        Potion(Key.f4, min_mana=70),
        Potion(Key.f5, min_health=60, priority=-1),
        Potion(Key.f6, min_health=70),
    ]
    combo = [
        AttackSpell(Key.f7, min_mana=15, cooldown=2),
        AttackRune(Key.f8, cooldown=2)
    ]

    game = Game('Tibia - Mietar')

    wsmt = WindowStateManagerTask(game, delay=0, on_active_only=True)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    MagicTrainingTask(game, psm, key=Key.f3, min_mana=90)
    # MagicTrainingTask(game, psm, key=Key.f3, min_mana=70)
    # MagicTrainingTask(game, psm, key=Key.f10, min_mana=70)
    FoodEaterTask(game, key=Key.f9)
    ExchangeTask(game, psm, wsmt)
    cc = ComboCaster(game, psm, combo)
    ComboSwitch(cc, key=Key.caps_lock)
    AutoTargetTask(game)

    # sssm = StoneSkinStateManager()
    # ssi = StoneSkinInvoker(game, psm, key=Key.f12, equip_at=30)
    # sssm.add_update_listener(lambda state: ssi.invoke(state.value))
    # ssl = StoneSkinImageListener(sssm, ssi)
    # wsmt.add_update_listener(ssl.update_listener)

    return game


def main():
    game = mietar()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
