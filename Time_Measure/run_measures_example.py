from penguin_game import *
from Time_Measure.measure_utils import init_game, time_measure, print_measures


def do_turn(game):
    # this is to init and refresh the game object that the time measure uses
    init_game(game)
    # this is just the normal example bot in the loop, broken into simple functions and wrapped in time measure
    for my_iceberg in game.get_my_icebergs():
        destination = find_dest(game)
        handle_dest(my_iceberg, destination)
    # this is to print out the time measurements
    print_measures()


@time_measure
def find_dest(game):
    if game.get_neutral_icebergs():
        destination = game.get_neutral_icebergs()[0]
    else:
        destination = game.get_enemy_icebergs()[0]
    return destination


@time_measure
def handle_dest(my_iceberg, destination):
    my_penguin_amount = my_iceberg.penguin_amount
    destination_penguin_amount = destination.penguin_amount
    if my_penguin_amount > destination_penguin_amount:
        print my_iceberg, "sends", (destination_penguin_amount + 1), "penguins to", destination
        my_iceberg.send_penguins(destination, destination_penguin_amount + 1)
