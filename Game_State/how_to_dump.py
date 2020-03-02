from penguin_game import *
from mock_game import game_state_dump


def do_turn(game):
    # this is to print out the game state at a given turn (here its 66)
    if game.turn == 66:
        print game_state_dump(game)

    # this is just the normal example bot from here on
    for my_iceberg in game.get_my_icebergs():
        my_penguin_amount = my_iceberg.penguin_amount  # type: int
        if game.get_neutral_icebergs():
            destination = game.get_neutral_icebergs()[0]  # type: Iceberg
        else:
            destination = game.get_enemy_icebergs()[0]  # type: Iceberg
        destination_penguin_amount = destination.penguin_amount  # type: int
        if my_penguin_amount > destination_penguin_amount:
            print my_iceberg, "sends", (destination_penguin_amount + 1), "penguins to", destination
            my_iceberg.send_penguins(destination, destination_penguin_amount + 1)
