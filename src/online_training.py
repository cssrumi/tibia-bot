from pynput.keyboard import Key

from ctx.burner import ShadowBurner
from domain.game.game import Game
from domain.task import StoppableThread


def online_training(character: str, food_key: Key, mana_burn_key: Key, mana_burn_key2: Key = None):
    game = Game(f'Tibia - {character}')
    burner = ShadowBurner(
        game,
        food_key=food_key,
        mana_burn_key=mana_burn_key
    )
    game.add_task(burner)
    if mana_burn_key2:
        burner2 = ShadowBurner(
            game,
            food_key=food_key,
            mana_burn_key=mana_burn_key2
        )
        game.add_task(burner2)
    game.start_all()
    game.await_exit()


def online_training_thread(character: str, food_key: Key, mana_burn_key: Key, mana_burn_key2: Key = None):
    return StoppableThread(target=online_training, args=(character, food_key, mana_burn_key, mana_burn_key2), daemon=False)


def main():
    mietar = online_training_thread(
        'Mietar',
        food_key=Key.f9,
        mana_burn_key=Key.f3
    )
    zaraki = online_training_thread(
        'Zaraki Kenpachi',
        food_key=Key.f9,
        mana_burn_key='3',
        mana_burn_key2=Key.f1
    )
    [training.start() for training in [
        mietar,
        zaraki,
    ]]


if __name__ == '__main__':
    main()