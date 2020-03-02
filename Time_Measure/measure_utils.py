from collections import Counter

game_obj = None
func_times = Counter()
func_calls = Counter()

def init_game(game):
    global game_obj
    game_obj = game

def time_measure(func):
    def wrapper(*args, **kwargs):
        func_name = str(func.__name__)
        start = game_obj.get_time_remaining()
        res = func(*args, **kwargs)
        delta = start - game_obj.get_time_remaining()
        func_times[func_name] += delta
        func_calls[func_name] += 1
        return res
    return wrapper

def print_measures():
    for func_name in func_times:
        print "func %s ran %s times and took overall %s ms" % (func_name, str(func_calls[func_name]), str(func_times[func_name]))
    func_calls.clear()
    func_times.clear()