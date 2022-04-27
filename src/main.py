from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, AttackSpell, AttackRune, ComboSwitch
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.loot import AutoLootTask
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.refill import RefillTask
from ctx.window import WindowStateManagerTask
from domain.battle import BattleList, BattleListStateManager
from domain.container import Quivers, Backpacks, Depots
from domain.game.game import Game
from domain.game.control import Keys, MouseButtons


def mietar():
    spells = [
        Spell(Keys.F3, min_mana=3, min_health=88),
    ]
    potions = [
        Potion(Keys.F4, min_mana=70),
        Potion(Keys.F5, min_health=50, priority=-1),
    ]
    combo = [
        AttackSpell(Keys.F7, min_mana=15, cooldown=2),
        AttackRune(Keys.F8, cooldown=2)
    ]

    game = Game('Tibia - Mietar')

    wsmt = WindowStateManagerTask(game, delay=0)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    FoodEaterTask(game, key=Keys.F9)

    # -- FULL AFK EXP --
    # MagicTrainingTask(game, psm, key=Keys.F3, min_mana=90)
    # cc = ComboCaster(game, psm, combo)
    # ComboSwitch(cc, key=Keys.CAPS_LOCK)
    # AutoTargetTask(game)
    # RefillTask(game, psm, wsmt, from_container=Backpacks.CRYSTAL, to_container=Quivers.BLUE)

    # -- EXP --
    MagicTrainingTask(game, psm, key=Keys.F3, min_mana=90)
    MagicTrainingTask(game, psm, key=Keys.F10, min_mana=90)
    ExchangeTask(game, psm, wsmt)
    RefillTask(game, psm, wsmt, from_container=Backpacks.CRYSTAL, to_container=Quivers.BLUE)
    AutoLootTask(game, psm, wsmt, MouseButtons.RIGHT, delay=10)
    # -- ATTACK --
    battle = BattleList(game, wsmt)
    blsmt = BattleListStateManager(battle)
    AutoTargetTask(game, blsmt)
    cc = ComboCaster(game, psm, blsmt, combo)
    ComboSwitch(cc, key=Keys.CAPS_LOCK)


    # -- Training --
    # MagicTrainingTask(game, psm, key=Keys.F3, min_mana=70)
    # MagicTrainingTask(game, psm, key=Keys.F10, min_mana=70)
    # RefillTask(game, psm, wsmt, from_container=Depots.BOX_XVIII, to_container=Backpacks.BEACH)

    # sssm = StoneSkinStateManager()
    # ssi = StoneSkinInvoker(game, psm, key=Key.f12, equip_at=30)
    # sssm.add_update_listener(lambda state: ssi.invoke(state.value))
    # ssl = StoneSkinImageListener(sssm, ssi)
    # wsmt.add_update_listener(ssl.update_listener)

    return game


def pythonista():
    spells = [
        Spell(Keys.F1, min_mana=5, min_health=88),
    ]
    potions = [
        Potion(Keys.F4, min_mana=70),
    ]
    combo = [
        AttackSpell(Keys.N1, min_mana=5, cooldown=2),
    ]

    game = Game('Tibia - Pythonista')

    wsmt = WindowStateManagerTask(game, delay=0)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    FoodEaterTask(game, key=Keys.F9)

    MagicTrainingTask(game, psm, key=Keys.F1, min_mana=90)
    ExchangeTask(game, psm, wsmt)

    battle = BattleList(game, wsmt)
    blsmt = BattleListStateManager(battle)

    cc = ComboCaster(game, psm, blsmt, combo)
    ComboSwitch(cc, key=Keys.CAPS_LOCK)
    AutoTargetTask(game, blsmt)

    return game


def main():
    # game = mietar()
    game = pythonista()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
