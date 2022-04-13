from ctx.ammorefill import AmmoRefillTask
from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, AttackSpell, AttackRune, ComboSwitch
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.window import WindowStateManagerTask
from domain.container import Quivers, Backpacks
from domain.game.game import Game
from domain.game.control import Keys


def mietar():
    spells = [
        Spell(Keys.F2, min_mana=6, min_health=90),
        Spell(Keys.F3, min_mana=10, min_health=80),
    ]
    potions = [
        Potion(Keys.F4, min_mana=70),
        Potion(Keys.F5, min_health=60, priority=-1),
        Potion(Keys.F6, min_health=70),
    ]
    combo = [
        AttackSpell(Keys.F7, min_mana=15, cooldown=2),
        AttackRune(Keys.F8, cooldown=2)
    ]

    game = Game('Tibia - Mietar')

    wsmt = WindowStateManagerTask(game, delay=0, on_active_only=False)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    MagicTrainingTask(game, psm, key=Keys.F3, min_mana=90)
    # MagicTrainingTask(game, psm, key=Keys.F3, min_mana=70)
    # MagicTrainingTask(game, psm, key=Keys.F10, min_mana=70)
    FoodEaterTask(game, key=Keys.F9)
    ExchangeTask(game, psm, wsmt)
    cc = ComboCaster(game, psm, combo)
    ComboSwitch(cc, key=Keys.CAPS_LOCK)
    AutoTargetTask(game)
    AmmoRefillTask(game, psm, wsmt, quiver=Quivers.BLUE, backpack=Backpacks.BEACH)

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
