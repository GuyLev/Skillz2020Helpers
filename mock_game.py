import time
import traceback


class BaseObject(object):
    _game = None
    _objectId = None

    def __init__(self):
        self._objectId = time.time()

    def equals(self, other):
        if not isinstance(other, BaseObject):
            return False
        return other._objectId == self._objectId

    def hashCode(self):
        return self._objectId

    def toString(self):
        return u"An object of type " + str(type(self)) + u"."

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return (not self.equals(other))

    def __hash__(self):
        return self.hashCode()

    def __repr__(self):
        return self.toString()


class MapObject(BaseObject):
   pass


class GameObject(MapObject):
    unique_id = None
    id = None
    owner = None
    already_acted = False

    def __init__(self, game, owner, id, unique_id):
        self._game = game
        self.owner = owner
        self. id = id
        self.unique_id = unique_id

    def equals(self, other):
        if not isinstance(other, GameObject):
            return False
        return other.unique_id == self.unique_id

    def hashCode(self):
        return self.unique_id

    def toString(self):
        return u"{" + str(type(self)) + u" Id: " + str(self.id) + u", Owner: " + str(self.owner.id) + u"}"


class Iceberg(GameObject):
    penguin_amount = 0
    level = 0
    cost_factor = 0
    penguins_per_turn = 0
    upgrade_cost = 0
    upgrade_level_limit = 0
    unique_id_to_distance = None

    def __init__(self, game, owner, id, unique_id,
                 penguin_amount, level, cost_factor, penguins_per_turn, upgrade_cost, upgrade_level_limit,
                 unique_id_to_distance):
        super(Iceberg, self).__init__(game, owner, id, unique_id)
        self.penguin_amount = penguin_amount
        self.level = level
        self.cost_factor = cost_factor
        self.penguins_per_turn = penguins_per_turn
        self.upgrade_cost = upgrade_cost
        self.upgrade_level_limit = upgrade_level_limit
        self.unique_id_to_distance = unique_id_to_distance

    def get_turns_till_arrival(self, destination):
        return self.unique_id_to_distance[destination.unique_id]

    def can_send_penguins(self, destination, penguinAmount):
        return (isinstance(destination, Iceberg) and
                destination != self and
                self.penguin_amount > penguinAmount > 0)

    def send_penguins(self, destination, penguinAmount):
        if not isinstance(destination, Iceberg):
            print u"The destination is not a Iceberg!, Check your parameters"
            return
        if penguinAmount <= self.penguin_amount:
            self.penguin_amount -= penguinAmount
        orderArgs = u"\"destination\": " + str(destination.unique_id) + u", \"penguin_amount\": " + str(penguinAmount)
        self._game._addOrder(u"send_penguins", self, orderArgs)

    def can_upgrade(self):
        return self.upgrade_cost < self.penguin_amount and self.level < self.upgrade_level_limit

    def upgrade(self):
        self._game._addOrder(u"upgrade", self)


class PenguinGroup(GameObject):
    def __init__(self, game, owner, id, unique_id,
                 destination, penguin_amount, source, turns_till_arrival):
        super(PenguinGroup, self).__init__(game, owner, id, unique_id)
        self.destination = destination
        self.penguin_amount = penguin_amount
        self.source = source
        self.turns_till_arrival = turns_till_arrival


class Player(BaseObject):
    def __init__(self, bot_name, pid, score):
        self.bot_name = bot_name
        self.icebergs = list()
        self.id = pid
        self.penguin_groups = list()
        self.score = score

    def equals(self, other):
        if not isinstance(other, Player):
            return False
        return other.id == self.id

    def hashCode(self):
        return self.id

    def toString(self):
        return u"{Player " + str(self.id) + u", score: " + str(self.score) + u", bot name: " + str(self.bot_name) + u"}"


def game_state_dump(game):
    game_state = {}
    # game data
    game_state.update(
        {
            'turn': game.turn,
            'max_turns': game.max_turns,
            'max_points': game.max_points,
            'turn_time': game.get_max_turn_time()})
    # player data
    for type_str, player in [('enemy', game.get_enemy()), ('myself', game.get_myself()), ('neutral', game.get_neutral())]:
        penguin_group_data = [
            {
                'id': pg.id,
                'unique_id': pg.unique_id,
                'destination': pg.destination.unique_id,
                'penguin_amount': pg.penguin_amount,
                'source': pg.source.unique_id,
                'turns_till_arrival': pg.turns_till_arrival
            } for pg in player.penguin_groups]
        game_state.update(
            {
                type_str:
                    {
                        'bot_name': player.bot_name,
                        'pid': player.id,
                        'score': player.score,
                        'penguin_groups': penguin_group_data
                    }
            })
    # iceberg data
    icebergs = game.get_all_icebergs()
    icebergs_data = []
    for src in icebergs:
        unique_id_to_distance = {dst.unique_id: src.get_turns_till_arrival(dst) for dst in icebergs}
        icebergs_data.append({
            'owner': src.owner.id,
            'id': src.id,
            'unique_id': src.unique_id,
            'penguin_amount': src.penguin_amount,
            'level': src.level,
            'cost_factor': src.cost_factor,
            'penguins_per_turn': src.penguins_per_turn,
            'upgrade_cost': src.upgrade_cost,
            'upgrade_level_limit': src.upgrade_level_limit,
            'unique_id_to_distance': unique_id_to_distance})
    game_state.update({'icebergs': icebergs_data})

    return game_state

class Game(BaseObject):
    # todo - load turn params to right place and init
    def __init__(self, turn_dict):
        self.neutral = self._generate_player(turn_dict['neutral'])
        self.enemy = self._generate_player(turn_dict['enemy'])
        self.myself = self._generate_player(turn_dict['myself'])
        self.player_by_id = {
            self.enemy.id: self.enemy,
            self.myself.id: self.myself,
            self.neutral.id: self.neutral,
        }
        self.all_icebergs = self._generate_icebergs(turn_dict['icebergs'])
        self.unique_id_to_iceberg = {ice.unique_id: ice for ice in self.all_icebergs}
        self._setup_player_icebergs()
        self._setup_player_penguin_groups(self.enemy, turn_dict['enemy'])
        self._setup_player_penguin_groups(self.myself, turn_dict['myself'])

        self.orders = list()
        self.turn = turn_dict['turn']
        self.max_turns = turn_dict['max_turns']
        self.max_points = turn_dict['max_points']
        self.turnTime = turn_dict['turn_time']
        self.turnStartTime = time.time()

    def _generate_iceberg(self, iceberg_data):
        return Iceberg(
            self, self.player_by_id[iceberg_data['owner']], iceberg_data['id'], iceberg_data['unique_id'],
            iceberg_data['penguin_amount'], iceberg_data['level'], iceberg_data['cost_factor'],
            iceberg_data['penguins_per_turn'], iceberg_data['upgrade_cost'], iceberg_data['upgrade_level_limit'],
            iceberg_data['unique_id_to_distance'])

    def _generate_icebergs(self, icebergs_data):
        return [self._generate_iceberg(ice) for ice in icebergs_data]

    def _setup_player_icebergs(self):
        for ice in self.all_icebergs:
            ice.owner.icebergs.append(ice)

    def _generate_player(self, player_data):
        return Player(player_data['bot_name'], player_data['pid'], player_data['score'])

    def _generate_penguin_group(self, owner, penguin_group_data):
        return PenguinGroup(
            self, owner, penguin_group_data['id'], penguin_group_data['unique_id'],
            self.unique_id_to_iceberg[penguin_group_data['destination']], penguin_group_data['penguin_amount'],
            self.unique_id_to_iceberg[penguin_group_data['source']], penguin_group_data['turns_till_arrival'])

    def _setup_player_penguin_groups(self, player, player_data):
        player_penguin_groups = [self._generate_penguin_group(player, pg) for pg in player_data['penguin_groups']]
        player.penguin_groups = player_penguin_groups

    def _addOrder(self, orderType, actor, args=u""):
        if (args is None):
            args = u""
        actor.already_acted = True
        cs = traceback.extract_stack()
        item = cs[-3]
        line = item[1]
        file_name = item[0]
        orderOriginPosition = u"{ \"file_name\": \"" + str(file_name) + u"\", \"line_number\": " + str(line) + u" }"
        order = ((((((((u"{ \"order_type\": \"" + (u"null" if orderType is None else orderType)) + u"\", \"actor\": ") + str(actor.unique_id)) + u", \"order_args\": {") + (u"null" if args is None else args)) + u"}, \"position\": ") + (u"null" if orderOriginPosition is None else orderOriginPosition)) + u" }")
        self.orders.append(order)

    # # todo - change implementation
    # def _addMoveOrder(self,order,actor,dest):
    #     orderArgs = ((((u"\"destination\": [" + Std.string(dest._hx___getLocation().row)) + u", ") + Std.string(dest._hx___getLocation().col)) + u"]")
    #     self._addOrder(order,actor,orderArgs)

    # # todo - change implementation
    # def _moveOrder(self,mover,destination):
    #     BaseObject._game._addMoveOrder(u"vectoric_per_actor_move",mover,destination)

    # # todo - change implementation
    # def _getActions(self):
    #     self._hx___nativeAPI.writeLine(u"\nBOT_DEBUG_END_FLAG_FOR_ENGINE_USAGE")
    #     _this = self._hx___orders
    #     return ((u"{\"orders\": [" + HxOverrides.stringOrNull(u",".join([python_Boot.toString1(x1,u'') for x1 in _this]))) + u"]}")

    def debug(self, arg):
        print arg

    def get_myself(self):
        return self.myself

    def get_enemy(self):
        return self.enemy

    def get_neutral(self):
        return self.neutral

    def get_all_players(self):
        return [self.myself, self.enemy, self.neutral]

    def get_time_remaining(self):
        return self.turnTime - (time.time() - self.turnStartTime)

    def get_max_turn_time(self):
        return self.turnTime

    def get_all_penguin_groups(self):
        penguinGroups = list()
        penguinGroups.extend(self.get_enemy_penguin_groups())
        penguinGroups.extend(self.get_my_penguin_groups())
        return list(penguinGroups)

    def get_my_penguin_groups(self):
        return list(self.myself.penguin_groups)

    def get_enemy_penguin_groups(self):
        return list(self.enemy.penguin_groups)

    def get_all_icebergs(self):
        return list(self.all_icebergs)

    def get_neutral_icebergs(self):
        return list(self.neutral.icebergs)

    def get_my_icebergs(self):
        return list(self.neutral.icebergs)

    def get_enemy_icebergs(self):
        return list(self.enemy.icebergs)
