from pynput.keyboard import Key

from ctx.burner import ShadowBurner, Market
from domain.game.game import Game
from util.task import StoppableThread


def online_training(character: str, food_key: Key, mana_burn_key: Key, mana_burn_key2: Key = None,
                    market_key: Key = None):
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
    if market_key:
        market = Market(
            game,
            trade_key=market_key,
            delay=60*5
        )
        game.add_task(market)
    game.start_all()
    game.await_exit()


def online_training_thread(character: str, food_key: Key, mana_burn_key: Key, mana_burn_key2: Key = None,
                           market_key: Key = None):
    return StoppableThread(target=online_training,
                           args=(character, food_key, mana_burn_key, mana_burn_key2, market_key),
                           daemon=False)


def main():
    mietar = online_training_thread(
        'Mietar',
        food_key=Key.f9,
        mana_burn_key=Key.f3
    )
    aizen = online_training_thread(
        'Aizen Sousuke',
        food_key=Key.f9,
        mana_burn_key=Key.f2,
        mana_burn_key2=Key.f11
    )
    zaraki = online_training_thread(
        'Zaraki Kenpachi',
        food_key=Key.f9,
        mana_burn_key='3',
        mana_burn_key2=Key.f1,
        # market_key='0'
    )
    zaraki_2 = online_training_thread(
        'Zaraki Kenpachi',
        food_key=None,
        mana_burn_key=Key.f7,
        mana_burn_key2=Key.f8
    )
    [training.start() for training in [
        mietar,
        # zaraki,
        # zaraki_2,
        aizen,
    ]]


if __name__ == '__main__':
    main()
