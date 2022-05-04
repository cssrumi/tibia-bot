from typing import List, Type, Optional

import attr

from cfg.application import Context
from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, ComboSwitch
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import Spell, Potion, HealerTask
from ctx.loot import AutoLootTask
from ctx.magictraining import MagicTrainingTask
from ctx.refill import RefillTask
from domain.container import ContainerTypes
from domain.game.control import Keys, MouseButtons


@attr.s
class Module:
    enabled = attr.ib(type=bool)

    @staticmethod
    def name() -> str:
        raise NotImplementedError()

    @classmethod
    def load_disabled(cls) -> 'Module':
        return cls(enabled=False)

    @classmethod
    def load(cls, config: dict, context: Context) -> 'Module':
        module_config = config[cls.name()]
        if not module_config or not module_config['enabled']:
            print(cls.name(), "module disabled")
            return cls.load_disabled()
        print(cls.name(), "module enabled")
        return cls.load_enabled(module_config, context)

    @staticmethod
    def load_enabled(module_config: dict, context: Context):
        raise NotImplementedError()


class ModuleRegistry:
    modules: List[Type[Module]] = list()

    @staticmethod
    def register(cls: Type[Module]):
        ModuleRegistry.modules.append(cls)


@attr.s
class AutoHeal(Module):
    task = attr.ib(type=Optional[HealerTask], default=None, kw_only=True)

    @staticmethod
    def name():
        return 'autoheal'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'AutoHeal':
        spells_config = module_config['spells']
        spells = [Spell.deserialize(spell) for spell in spells_config] if spells_config else []
        potions_config = module_config['potions']
        potions = [Potion.deserialize(potions) for potions in potions_config] if spells_config else []
        task = HealerTask(
            context.game,
            context.player_state_manager,
            spells=spells,
            potions=potions
        )
        print(potions)
        print(spells)
        return AutoHeal(True, task=task)


ModuleRegistry.register(AutoHeal)


# TODO: COMBO
class Combo(Module):
    caster = attr.ib(type=Optional[ComboCaster], default=None, kw_only=True)
    switch = attr.ib(type=Optional[ComboSwitch], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'combo'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'Combo':
        return Combo.load_disabled()


@attr.s
class FoodEater(Module):
    task = attr.ib(type=Optional[FoodEaterTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'foodeater'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'FoodEater':
        key = Keys.from_str(module_config['key'])
        task = FoodEaterTask(context.game, key=key)
        return FoodEater(True, task=task)


ModuleRegistry.register(FoodEater)


@attr.s
class Exchange(Module):
    task = attr.ib(type=Optional[ExchangeTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'exchange'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'Exchange':
        task = ExchangeTask(
            context.game,
            context.player_state_manager,
            context.window_state_manager
        )
        return Exchange(True, task=task)


ModuleRegistry.register(Exchange)


@attr.s
class AutoTarget(Module):
    task = attr.ib(type=Optional[AutoTargetTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'autotarget'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'AutoTarget':
        task = AutoTargetTask(
            context.game,
            context.battle_state_manager
        )
        return AutoTarget(True, task=task)


ModuleRegistry.register(AutoTarget)


@attr.s
class AutoLoot(Module):
    task = attr.ib(type=Optional[AutoLootTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'autoloot'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'AutoLoot':
        kwargs = AutoLoot.optional_kwargs(module_config)
        mouse_button = MouseButtons.from_str(module_config['mouse_button'])
        task = AutoLootTask(
            context.game,
            context.player_state_manager,
            context.window_state_manager,
            mouse_button,
            **kwargs
        )
        return AutoLoot(True, task=task)

    @staticmethod
    def optional_kwargs(module_config: dict) -> dict:
        kwargs = {}
        delay = module_config.get('delay')
        if delay:
            kwargs['delay'] = delay
        loot_cooldown = module_config.get('loot_cooldown')
        if loot_cooldown:
            kwargs['loot_cooldown'] = loot_cooldown
        return kwargs


ModuleRegistry.register(AutoLoot)


@attr.s
class MagicTraining(Module):
    tasks = attr.ib(type=List[MagicTrainingTask], factory=list, kw_only=True)

    @staticmethod
    def name():
        return 'magictraining'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'MagicTraining':
        burners_config = module_config['burners']
        tasks = [MagicTraining._load_burner_task(cfg, context) for cfg in burners_config] if burners_config else []
        return MagicTraining(True, tasks=tasks)

    @staticmethod
    def _load_burner_task(cfg: dict, ctx: Context) -> MagicTrainingTask:
        key = Keys.from_str(cfg['key'])
        min_mana = cfg['min_mana']
        return MagicTrainingTask(ctx.game, ctx.player_state_manager, key=key, min_mana=min_mana)


ModuleRegistry.register(MagicTraining)


@attr.s
class Refiller(Module):
    task = attr.ib(type=Optional[RefillTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'refiller'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'Refiller':
        kwargs = Refiller.optional_kwargs(module_config)

        from_config = module_config['from']
        from_type = ContainerTypes.from_str(from_config['type'])
        from_container = from_type.from_str(from_config['container'])

        to_config = module_config['to']
        to_type = ContainerTypes.from_str(to_config['type'])
        to_container = to_type.from_str(to_config['container'])

        task = RefillTask(
            context.game,
            context.player_state_manager,
            context.window_state_manager,
            from_container=from_container,
            to_container=to_container,
            **kwargs
        )
        return Refiller(True, task=task)

    @staticmethod
    def optional_kwargs(module_config: dict) -> dict:
        kwargs = {}
        delay = module_config.get('delay')
        if delay:
            kwargs['delay'] = delay
        return kwargs


ModuleRegistry.register(Refiller)
