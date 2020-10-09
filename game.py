from player import Player
import card_utils
import numpy.random as random
from exceptions import InfoDictException, GameConfigException
from constants import NUM_PLAYERS

class FishGame:
    """
    An instance of a fish game between NUM_PLAYERS players.

    There are 2 teams:
    Team 1: Players 1, 3, and 5
    Team 0: Players 0, 2, and 4
    """
    def __init__(self, player_cards, models, start, team1_score, team0_score, train=True):
        """
        Initializes a game with user defined starting hands
        Also makes sure that the starting configuration is valid 
        (no duplicate cards, all card strings are valid)
        :param player_cards: a length NUM_PLAYERS list, each element is a list of cards
        List is [p1cards, p2cards, etc...]
        :param models: a list of models, in the same order as player_cards
        """
        cards_seen_dict = {c: 0 for c in card_utils.gen_all_cards()}
        self.players = []
        self.player_cards = {ID: player_cards[ID] for ID in range(NUM_PLAYERS)}
        for i, cards in enumerate(player_cards):
            player = Player.player_start_of_game(i, cards, models[i], train=train)
            self.players.append(player)
            for c in cards:
                if c in cards_seen_dict:
                    cards_seen_dict[c] += 1
                else:
                    raise GameConfigException("Not a valid card string!")
        for count in cards_seen_dict.values():
            if count > 1:
                raise GameConfigException("There is a duplicate card!")
        self.turn = start
        self.team1_score = team1_score
        self.team0_score = team0_score

    @classmethod
    def start_random_game(cls, models, train=True):
        """
        Deals 9 random cards to NUM_PLAYERS players and assigns someone at random to start
        :param models: list of models for players
        """
        all_cards = list(card_utils.gen_all_cards())
        player_cards = random.permutation(all_cards).reshape((NUM_PLAYERS, 9))
        player_cards_list = [list(x) for x in player_cards]
        return cls(player_cards_list, models, random.randint(0, NUM_PLAYERS), 0, 0, train=train)

    def check_call(self):
        """
        Checks if any player wants to call a half suit. If so,
        return the half suit called and if its successful.
        Otherwise return False

        Format: [hs, team, success]
        """
        for caller in self.players:
            call = caller.check_call()
            if call:
                return self.check_call_correct(call, caller.ID)
        return False

    def check_call_correct(self, call, ID):
        """
        Checks if a call is correct
        :param call: a call list of tuples
        :param ID: ID of player calling
        :return: hs, team, success
        """
        success = True
        for ID, card in call:
            if card not in self.player_cards[ID]:
                success = False
        return [card_utils.find_half_suit(card), ID % 2, success]

    def get_move(self):
        """
        Requests a move from the player who's turn it is to move
        Also updates who's turn it is

        :return: [asker, target, card, success]
        """
        asker = self.turn
        target, card = self.players[self.turn].make_optimal_ask()
        success = False
        if card in self.player_cards[target]:
            success = True
        if not success:
            self.turn = target
        return asker, target, card, success

    def report_call(self, hs):
        """
        Updates the player_cards dict
        Makes each player update their info in response to a call
        :param hs: half suit being called
        """
        hs_info_dict = {ID: 0 for ID in range(NUM_PLAYERS)}
        for card in card_utils.find_cards(hs):
            for ID in range(NUM_PLAYERS):
                if card in self.player_cards[ID]:
                    self.player_cards[ID].remove(card)
                    hs_info_dict[ID] += 1
        for player in self.players:
            player.update_call(hs, hs_info_dict)

    def report_ask(self, ID_ask, ID_target, card, success):
        """
        Updates the player_cards dict
        Makes each player update their info in response to an ask
        :param ID_ask: ID of player asking for the card
        :param ID_target: ID of player being asked
        :param card: card being asked
        :param success: True if ask was successful
        """
        if success:
            self.player_cards[ID_ask].append(card)
            self.player_cards[ID_target].remove(card)
        for player in self.players:
            player.update_transaction(ID_ask, ID_target, card, success)

    def run_whole_game(self, verbose = 0, max_turns = 1000):
        """
        Makes the players play through an entire game. This consists of first
        asking for anyone who wants to call on each round. Then, if no one
        wants to call, the game asks for the player who has the turn to request
        a card. Plays until everyone is out of cards
        :param max_turns: longest a game can go on before game is forced to end
        :param verbose: Prints nothing if 0, prints the final score if 1,
        prints all calls if 2, prints all transactions and calls if 3
        :return: True if game goes on longer than 1000 turns and False otherwise
        """
        turns = 0
        if verbose not in [0, 1, 2, 3]:
            raise Exception("Verbosity must be 0, 1, 2, or 3!")
        while not self.check_game_finished():
            if turns > max_turns:
                break
            # First check for calls
            call = self.check_call()
            while call:
                hs, team, success = call
                if verbose >= 2:
                    if success:
                        print ("Team {} successfully called half suit {}".format(team, hs))
                    else:
                        print ("Team {} unsuccessfully called half suit {}".format(team, hs))
                try:
                    self.report_call(hs)
                except InfoDictException as err:
                    print(err)
                    print ("Failed in updating calling")
                    for i in range(NUM_PLAYERS):
                        print (self.player_cards[i], self.players[i].own_cards())
                    break
                if success and team == 1 or not success and team == 0:
                    self.team1_score += 1
                else:
                    self.team0_score += 1
                call = self.check_call()

            # When there is 1 team left with cards, they are forced to call (for now game ends)
            num_cards = self.players[0].num_cards
            if num_cards[0] == 0 and num_cards[2] == 0 and num_cards[4] == 0:
                if verbose >= 2:
                    print ("Forcing calls for team 1")
                self.force_calls(1)
                break
            if num_cards[1] == 0 and num_cards[3] == 0 and num_cards[5] == 0:
                if verbose >= 2:
                    print ("Forcing calls for team 0")
                self.force_calls(0)
                break
            # If it's a player's turn and they have no cards, pass to the teammate on their right
            while len(self.players[self.turn].own_cards()) == 0:
                self.turn = (self.turn + 2) % NUM_PLAYERS

            # Now get the player who has turn's request
            if not self.check_game_finished():
                ID_ask, ID_target, card, success = self.get_move()
                if verbose == 3:
                    if success:
                        print ("Player {} successfully took {} from {}".format(ID_ask, card, ID_target))
                    else:
                        print ("Player {} did not take {} from {}".format(ID_ask, card, ID_target))
                try:
                    self.report_ask(ID_ask, ID_target, card, success)
                except InfoDictException as err:
                    print (err)
                    print ("Failed in updating ask")
                    for i in range(NUM_PLAYERS):
                        print(self.player_cards[i], self.players[i].own_cards())
                    break
                turns += 1
        if verbose >= 1:
            print ("Final Score:")
            print ("Team 0: " + str(self.team0_score))
            print ("Team 1: " + str(self.team1_score))
            print ("Game went on for {} turns".format(turns))
        self.report_win()
        return turns > max_turns

    def check_game_finished(self):
        """
        Returns true if the game is finished, (no players have cards)
        """
        for player in self.players:
            if player.own_cards():
                return False
        return True

    def force_calls(self, team):
        """
        Forces players on a team to call
        :param team: team number being forced to call
        """
        players = [self.players[2 * i + team] for i in range(3)]
        remaining_hs = self.players[0].remaining_hs
        for hs in remaining_hs:
            for player in players:
                call = player.check_call()
                if call:
                    hs, team, success = self.check_call_correct(call, player.ID)
                    if success and team == 0 or not success and team == 1:
                        self.team0_score += 1
                    else:
                        self.team1_score += 1
                    self.report_call(hs)
                    break
            call = players[0].force_call(hs)
            hs, team, success = self.check_call_correct(call, players[0].ID)
            if success and team == 0 or not success and team == 1:
                self.team0_score += 1
            else:
                self.team1_score += 1
            self.report_call(hs)

    def report_win(self):
        """
        Reports a win or loss to the player who has turn
        """
        win = False
        if self.turn % 2 == 0 and self.team0_score > self.team1_score:
            win = True
        if self.turn % 2 == 1 and self.team1_score > self.team0_score:
            win = True
        self.players[self.turn].update_gameover(win)