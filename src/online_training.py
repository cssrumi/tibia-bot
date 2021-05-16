from pynput.keyboard import Key

from ctx.burner import ShadowBurner
from domain.game.game import Game
from domain.task import StoppableThread


def online_training(character: str, food_key: Key, mana_burn_key: Key):
    game = Game(f'Tibia - {character}')
    burner = ShadowBurner(
        game,
        food_key=food_key,
        mana_burn_key=mana_burn_key
    )
    game.add_task(burner)
    game.start_all()
    game.await_exit()


def online_training_thread(character: str, food_key: Key, mana_burn_key: Key):
    return StoppableThread(target=online_training, args=(character, food_key, mana_burn_key), daemon=False)


def main():
    deidara = online_training_thread(
        'Deidara',
        food_key=Key.f9,
        mana_burn_key=Key.f2
    )
    paler = online_training_thread(
        'Paler',
        food_key=Key.f9,
        mana_burn_key=Key.f2
    )
    functional_scala = online_training_thread(
        'Functional Scala',
        food_key=Key.f9,
        mana_burn_key=Key.f1
    )
    [training.start() for training in [
        deidara,
        paler,
        functional_scala
    ]]


if __name__ == '__main__':
    main()