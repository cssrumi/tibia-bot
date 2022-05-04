from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, AttackSpell, AttackRune, ComboSwitch
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import HealerTask, Spell, Potion
from ctx.loot import AutoLootTask
from ctx.magictraining import MagicTrainingTask
from ctx.player import PlayerStateManager, PlayerImageListener
from ctx.refill import RefillTask
from ctx.window import WindowStateManager
from domain.battle import BattleList, BattleListStateManager
from domain.cave import CaveConfig, Caves, CaveTask
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
        AttackSpell(Keys.F7, min_mana=15, delay=2),
        AttackRune(Keys.F8, delay=2)
    ]

    game = Game('Tibia - Mietar')

    wsmt = WindowStateManager(game, delay=0)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    FoodEaterTask(game, key=Keys.F9)

    # -- EXP --
    MagicTrainingTask(game, psm, key=Keys.F3, min_mana=90)
    MagicTrainingTask(game, psm, key=Keys.F10, min_mana=90)
    ExchangeTask(game, psm, wsmt)
    RefillTask(game, psm, wsmt, from_container=Backpacks.CRYSTAL, to_container=Quivers.BLUE)
    # AutoLootTask(game, psm, wsmt, MouseButtons.RIGHT, delay=10)
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
        AttackSpell(Keys.N1, min_mana=5, delay=2),
    ]

    game = Game('Tibia - Pythonista')

    wsmt = WindowStateManager(game, delay=0)
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
    cave_config = CaveConfig.read(*Caves.CYCLOPS)
    CaveTask(cave_config, battle)

    return game


def zaraki():
    spells = [
        Spell(Keys.F1, min_mana=5, min_health=92),
    ]
    potions = [
        Potion(Keys.F4, min_mana=30),
        Potion(Keys.F5, min_health=78),
    ]
    combo = [
        AttackSpell(Keys.N3, min_mana=30, delay=0.1),
        AttackSpell(Keys.F7, min_mana=20, delay=2),
        AttackSpell(Keys.N2, min_mana=20, delay=0.1),
        AttackSpell(Keys.F8, min_mana=20, delay=2),
    ]

    game = Game('Tibia - Zaraki Kenpachi')

    wsmt = WindowStateManager(game, delay=0)
    psm = PlayerStateManager()
    pil = PlayerImageListener(psm)
    wsmt.add_update_listener(pil.update_listener)

    HealerTask(game, psm, spells=spells, potions=potions)
    FoodEaterTask(game, key=Keys.F9)
    MagicTrainingTask(game, psm, key=Keys.F1, min_mana=90)
    ExchangeTask(game, psm, wsmt)
    AutoLootTask(game, psm, wsmt, MouseButtons.RIGHT, delay=10)

    battle = BattleList(game, wsmt)
    blsmt = BattleListStateManager(battle)
    cc = ComboCaster(game, psm, blsmt, combo)
    ComboSwitch(cc, key=Keys.CAPS_LOCK)
    AutoTargetTask(game, blsmt)
    # cave_config = CaveConfig.read(*Caves.CYCLOPS)
    # CaveTask(cave_config, battle)

    return game


def main():
    # game = pythonista()
    # game = mietar()
    game = zaraki()
    game.start_all()
    game.await_exit()


if __name__ == '__main__':
    main()
