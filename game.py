import player
import card_utils
import numpy.random as random

class FishGame:
    """
    An instance of a fish game between 6 players.
    """
    def __init__(self, player_cards, start):
        """
        Initializes a game with user defined starting hands
        Also makes sure that the starting configuration is valid 
        (no duplicate cards, all card strings are valid)

        player_cards: a length 6 list, each element is a list of cards
        List is [p1cards, p2cards, etc...]
        """
        cards_seen_dict = {c: 0 for c in card_utils.gen_all_cards()}
        self.players = []
        for i, cards in enumerate(player_cards):
            player = Player.player_start_of_game(i, cards)
            self.players.append(player)
            for c in cards:
                if c in cards_seen_dict:
                    cards_seen_dict[c] += 1
                else:
                    raise Exception("Not a valid card string!")
        for count in cards_seen_dict.values():
            if count > 1:
                raise Exception("There is a duplicate card!")
        self.turn = start

    @classmethod
    def start_random_game(cls):
        """
        Deals 9 random cards to 6 players and assigns someone at random to start
        """
        all_cards = list(card_utils.gen_all_cards())
        player_cards = random.permutation(all_cards).reshape((6, 9))
        player_cards_list = [list(x) for x in player_cards]
        return cls.__init__(player_cards_list, random.randint(0, 6))

    def check_call(self):
        """
        Checks if any player wants to call a half suit. If so,
        return the half suit called and if its successful

        Format: [hs, success]
        """
        for player in players:
            call = player.check_call:
            if call:
                success = True
                for player, card in call:
                    if card not in player.own_cards():
                        success = False
                return [card_utils.find_half_suit(card), success]
        return False

    def get_move(self):
        """
        Requests a move from the player who's turn it is to move
        Returns the move in the format:

        [asker, target, card, success]
        """
        target, card = self.players[self.turn].make_optimal_play()
        success = card in self.players[target].own_cards()
        if not success:
            self.turn = target
        return asker, target, card, success

    def report_call(self, hs):
        """
        Makes each player update their info in response to a call
        """
        hs_info_dict = {ID: 0 for ID in range(6)}
        for card in card_utils.find_cards(hs):
            for ID in range(6):
                if card in self.players[ID].own_cards():
                    hs_info_dict[ID] += 1
        for player in self.players:
            player.update_call(hs, hs_info_dict)

    def report_ask(self, ID_ask, ID_target, card, success):
        for player in self.players:
            player.update_transaction(ID_ask, ID_target, card, success)



