from typing import List, Type, Optional

import attr

from config.application import Context
from ctx.healer import Spell, Potion, HealerTask


@attr.s
class Module:
    enabled = attr.ib(type=bool)

    @staticmethod
    def name() -> str:
        raise NotImplementedError()

    @classmethod
    def disabled(cls) -> 'Module':
        return cls(enabled=False)

    @staticmethod
    def load(config: dict, context: Context) -> 'Module':
        raise NotImplementedError()


class ModuleRegistry:
    modules: List[Type[Module]] = list()

    @staticmethod
    def register(cls: Type[Module]):
        ModuleRegistry.modules.append(cls)


@attr.s
class Autoheal(Module):
    task = attr.ib(type=Optional[HealerTask], kw_only=True, init=False)

    @staticmethod
    def name():
        return 'autoheal'

    @staticmethod
    def load(config: dict, context: Context) -> 'Autoheal':
        module = config[Autoheal.name()]
        if not module or module['enabled']:
            return Autoheal.disabled()
        spells_config = module['spells']
        spells = [Spell.deserialize(spell) for spell in spells_config] if spells_config else []
        potions_config = module['potions']
        potions = [Potion.deserialize(potions) for potions in potions_config] if spells_config else []
        task = HealerTask(
            context.game,
            context.player_state_manager,
            spells=spells,
            potions=potions
        )
        return Autoheal(True, task=task)
