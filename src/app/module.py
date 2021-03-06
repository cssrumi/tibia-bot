from typing import List, Type, Optional

import attr

from app.context import Context
from app.logger import Logger
from ctx.autocast import AutoCastTask
from ctx.autotarget import AutoTargetTask
from ctx.combo import ComboCaster, ComboSwitch, AttackTypes
from ctx.exchange import ExchangeTask
from ctx.foodeater import FoodEaterTask
from ctx.healer import Spell, Potion, HealerTask
from ctx.loot import AutoLootTask, LootAction, LootListener, LootType
from ctx.magictraining import MagicTrainingTask
from ctx.randomization import Randomization, PlayerBasedRandomization
from ctx.refill import RefillTask
from domain.cast import Cast
from domain.container import ContainerTypes
from domain.game.control import Keys, MouseButtons
from util.switch import Switchable
from ctx.chat import Chat as ChatHandler


@attr.s
class Module(Switchable):
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
            Logger.log(cls.name() + " module disabled")
            return cls.load_disabled()
        Logger.log(cls.name() + " module enabled")
        return cls.load_enabled(module_config, context)

    @staticmethod
    def load_enabled(module_config: dict, context: Context):
        raise NotImplementedError()

    def switch(self):
        if self.enabled:
            super().switch()
            self._switch_enabled()
            Logger.log(f"{self.name()} module switched!")
        else:
            Logger.log(f"Unable to switch disabled module: {self.name()}")

    def _switch_enabled(self):
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
        Logger.log(potions)
        Logger.log(spells)
        return AutoHeal(True, task=task)

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


ModuleRegistry.register(AutoHeal)


@attr.s
class Combo(Module):
    caster = attr.ib(type=Optional[ComboCaster], default=None, kw_only=True)
    _switch = attr.ib(type=Optional[ComboSwitch], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'combo'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'Combo':
        attacks_config = module_config['attacks']
        attacks = [Combo._deserialize_attack(attack_cfg) for attack_cfg in attacks_config] if attacks_config else []
        randomization = Combo._deserialize_randomization(module_config['randomization'], context)
        caster = ComboCaster(
            context.game,
            context.player_state_manager,
            context.battle_state_manager,
            attacks,
            randomization=randomization
        )
        switch_key = Keys.from_str(module_config['switch']['key'])
        switch = ComboSwitch(
            caster,
            key=switch_key
        )
        return Combo(True, caster=caster, switch=switch)

    @staticmethod
    def _deserialize_attack(attack_config: dict) -> Cast:
        attack_type = AttackTypes.from_str(attack_config['type'])
        attack_config = attack_config.copy()
        attack_config.pop('type')
        return attack_type.deserialize(attack_config)

    @staticmethod
    def _deserialize_randomization(randomization_config: dict, context: Context) -> Randomization:
        if not randomization_config or not randomization_config.get('enabled', False):
            return Randomization.disabled()
        return PlayerBasedRandomization(**randomization_config, psm=context.player_state_manager)

    def _switch_enabled(self):
        if self.caster:
            self.caster.switch()


ModuleRegistry.register(Combo)


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

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


ModuleRegistry.register(FoodEater)


@attr.s
class AutoCast(Module):
    task = attr.ib(type=Optional[AutoCastTask], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'autocast'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'AutoCast':
        key = Keys.from_str(module_config['key'])
        kwargs = AutoCast.optional_task_kwargs(module_config)
        task = AutoCastTask(context.game, key=key, **kwargs)
        return AutoCast(True, task=task)

    @staticmethod
    def optional_task_kwargs(module_config: dict) -> dict:
        kwargs = {}
        delay = module_config.get('delay') or module_config.get('action_delay')
        if delay:
            kwargs['action_delay'] = delay
        return kwargs

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


ModuleRegistry.register(AutoCast)


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

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


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

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


ModuleRegistry.register(AutoTarget)


@attr.s
class AutoLoot(Module):
    task = attr.ib(type=Optional[AutoLootTask], default=None, kw_only=True)
    listener = attr.ib(type=Optional[LootListener], default=None, kw_only=True)

    @staticmethod
    def name() -> str:
        return 'autoloot'

    @staticmethod
    def load_enabled(module_config: dict, context: Context) -> 'AutoLoot':
        action_kwargs = AutoLoot.optional_action_kwargs(module_config)
        mouse_button = MouseButtons.from_str(module_config['mouse_button'])
        action = LootAction(
            context.game,
            context.window_state_manager,
            mouse_button,
            **action_kwargs
        )
        task = None
        listener = None
        loot_type = LootType.from_str(module_config.get('type', LootType.REPEATABLE.name))
        if loot_type == LootType.REPEATABLE:
            task_kwargs = AutoLoot.optional_task_kwargs(module_config)
            task = AutoLootTask(
                context.game,
                context.player_state_manager,
                context.window_state_manager,
                action,
                **task_kwargs
            )
        if loot_type == LootType.ON_KEY:
            key = module_config['key']
            loot_key = Keys.from_str(key)
            listener = LootListener(action, loot_key, is_stopped=False)

        return AutoLoot(True, task=task, listener=listener)

    @staticmethod
    def optional_action_kwargs(module_config: dict) -> dict:
        kwargs = {}
        loot_cooldown = module_config.get('loot_cooldown')
        if loot_cooldown:
            kwargs['loot_cooldown'] = loot_cooldown
        return kwargs

    @staticmethod
    def optional_task_kwargs(module_config: dict) -> dict:
        kwargs = {}
        loot_cooldown = module_config.get('loot_cooldown')
        if loot_cooldown:
            kwargs['loot_cooldown'] = loot_cooldown
        delay = module_config.get('delay') or module_config.get('action_delay')
        if delay:
            kwargs['action_delay'] = delay
        return kwargs

    def _switch_enabled(self):
        if self.task:
            self.task.switch()
        if self.listener:
            self.listener.switch()


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
        delay = cfg.get('delay') or cfg.get('action_delay')
        delay_kwarg = {} if delay is None else {'action_delay': delay}
        return MagicTrainingTask(ctx.game, ctx.player_state_manager, key=key, min_mana=min_mana, **delay_kwarg)

    def _switch_enabled(self):
        if self.tasks:
            [task.switch() for task in self.tasks]


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
        delay = module_config.get('delay') or module_config.get('action_delay')
        if delay:
            kwargs['action_delay'] = delay
        return kwargs

    def _switch_enabled(self):
        if self.task:
            self.task.switch()


ModuleRegistry.register(Refiller)


@attr.s
class Chat(Module):
    chat_handler = attr.ib(type=ChatHandler)

    @staticmethod
    def name() -> str:
        return 'chat'

    @classmethod
    def load(cls, config: dict, context: Context) -> 'Chat':
        ch = ChatHandler(context.game, context.player_state_manager)
        return cls(True, ch)

    @staticmethod
    def load_enabled(module_config: dict, context: Context):
        pass

    def _switch_enabled(self):
        pass


ModuleRegistry.register(Chat)
