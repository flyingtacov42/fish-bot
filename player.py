import card_utils
import random
from constants import YES, NO, UNSURE
from exceptions import InfoDictException


class Player:
    """
    The player class represents each of the players in a Fish game.
    It is responsible for storing the following information:

    id: the id of the Player (0-5)
    name: the name of the player (This is technically meaningless for the game state)
    num_cards: the number of cards that each of the 6 players have
    info: a dictionary that stores the "status" of the cards for each player
    hs_info: a dictionary that stores at least how many cards of each half suit each player has

    The structure of the info and public info dictionaries are like this:
    {
    player id: 
        {
        Card name: Status
        }
    }
    Status is either YES, NO, or UNSURE, as defined in constants

    The structure of the half suit info dictionary is like this:
    {
    player id: 
        {
        Half suit name: count
        }
    }
    Where count is the minimum number of cards a player has in a half suit

    Important methods:
    Take in a Transaction object and update the info data structure with the information
    Determine the "optimal" play that it can make
    Determine whether to call, and which half suit
    """

    def __init__(self, ID, num_cards, info, public_info, hs_info, name=None):
        """
        Initializes the player with the information:
        :param ID: a number in the range 0-5 that denotes the team of the player.
        IDs are universally agreed on by all players
        ID numbers 1, 3, and 5 are on 1 team

        :param Num_cards:
        A dictionary that stores the id of the player and how many cards each player has

        :param hs_info: A dictionary that stores the number of cards that each player has in
        each half suit

        :param Name: The name of the player. This field is not relevant to the logic in the game.

        Since each player knows their own cards, the section of the dictionary corresponding
        to their own id will be completely determined (YES or NO)
        """
        self.ID = ID
        self.name = name
        self.num_cards = num_cards
        self.info = info
        self.public_info = public_info
        self.hs_info = hs_info
        self._update_info()
        self._update_public_info()

    @classmethod
    def player_start_of_game(cls, ID, own_cards, name=None):
        """
        This initialization corresponds to the initialization at the start of a fish game
        Assumes that everyone has 9 cards
        """
        num_cards = {x: 9 for x in range(6)}
        return cls(ID, num_cards, cls._init_info_start_game(ID, own_cards),
                   cls._init_public_info_start_game(),
                   cls._init_hs_info_start_game(ID, own_cards), name=name)

    @staticmethod
    def _init_info_start_game(ID, own_cards):
        """
        Returns the info dictionary assuming its the start of a new game
        Given your own cards and ID
        """
        info = {}
        for player_id in range(6):
            if player_id == ID:
                player_cards = {card: NO for card in card_utils.gen_all_cards()}
                for card in own_cards:
                    player_cards[card] = YES
            else:
                player_cards = {card: UNSURE for card in card_utils.gen_all_cards()}
            info[player_id] = player_cards.copy()
        return info

    @staticmethod
    def _init_public_info_start_game():
        """
        Returns an "empty" public info dictionary
        :return: a dictionary that represents the public information at the start of the game
        """
        public_info_dict = {}
        for ID in range(6):
            player_info = {}
            for card in card_utils.gen_all_cards():
                player_info[card] = UNSURE
            public_info_dict[ID] = player_info
        return public_info_dict

    @staticmethod
    def _init_hs_info_start_game(ID, own_cards):
        """
        Returns the half suit info dictionary assuming its the start of a new game
        Uses data from the already intialized info dictionary
        """
        blank_hs = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        hs_info = {player_id: blank_hs.copy() for player_id in range(6)}
        for card in own_cards:
            hs_info[ID][card_utils.find_half_suit(card)] += 1
        return hs_info

    def _update_info(self):
        """
        Updates the info dictionary based on information already in the info dictionary
        For example, if a player has a certain card, you can be sure that no one else has that card
        Also, if 5 people are guarenteed not to have a card, the sixth person must have that card

        If a person is guarenteed to have a card in a half suit (based on what they ask for), and there is 
        only one card in that half suit left that isn't ruled out, then they have to have that card

        This method will also throw an exception if there is contradictory information, 
        such as 2 players both having the same card
        """
        # First update Yes -> No for other players
        # And 5 Nos -> Yes for 1 player
        for card in card_utils.gen_all_cards():
            id_exists = -1
            id_unsures = list(range(6))
            for ID in range(6):
                if self.info[ID][card] == YES:
                    id_exists = ID
                elif self.info[ID][card] == NO:
                    id_unsures.remove(ID)
            # Yes -> Nos for everyone else scenario
            if id_exists != -1:
                for ID in range(6):
                    if ID != id_exists:
                        if self.info[ID][card] == YES:
                            self.print_info()
                            raise InfoDictException("Two or more players have the card " + card)
                        self.info[ID][card] = NO
            # 5 Nos -> Yes scenario
            elif len(id_unsures) == 1:
                self.info[id_unsures[0]][card] = YES

        # Now check for when a player has a known half suit but not all known cards in that hs
        for hs in card_utils.gen_all_halfsuits():
            for ID in range(6):
                cards = card_utils.find_cards(hs)
                no_count = 0
                for c in cards:
                    if self.info[ID][c] == NO:
                        no_count += 1
                if no_count == 6 - self.hs_info[ID][hs]:
                    for c in cards:
                        if self.info[ID][c] != NO:
                            self.info[ID][c] = YES
                if no_count > 6 - self.hs_info[ID][hs]:
                    self.print_info()
                    raise InfoDictException("Player {} should have at least {} cards in the half suit {}, but doesn't"
                                    .format(ID, self.hs_info[ID][hs], hs))

        # Next check if unsures = num cards left
        for ID in range(6):
            unsures = []
            for c in card_utils.gen_all_cards():
                if self.info[ID][c] == UNSURE:
                    unsures.append(c)
            if self.num_cards[ID] == len(unsures):
                for c in unsures:
                    self.info[ID][c] = YES

    def _update_public_info(self):
        """
        Updates the public info dictionary, using the same logic as
        in the _update_info method
        Note that we don't need to update based on half suit information
        because half suit information is determined by public info
        """
        for card in card_utils.gen_all_cards():
            id_exists = -1
            for ID in range(6):
                if self.public_info[ID][card] == YES:
                    id_exists = ID
            if id_exists != -1:
                for ID in range(6):
                    if ID != id_exists:
                        if self.public_info[ID][card] == YES:
                            raise Exception("Two or more players have the card " + card)
                        self.public_info[ID][card] = NO

    def update_transaction(self, ID_ask, ID_target, card, success):
        """
        Given a transaction, updates the player's info, public info, and half suit info

        :param ID_ask: ID of player asking for the card
        :param ID_target: player being asked
        :param card: card being asked
        :param success: true if card was taken from ID_target
        """
        if success:
            self.num_cards[ID_ask] += 1
            self.num_cards[ID_target] -= 1
            self.info[ID_ask][card] = YES
            self.info[ID_target][card] = NO
            self.public_info[ID_ask][card] = YES
            self.public_info[ID_target][card] = NO
            if self.hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
            self.hs_info[ID_ask][card_utils.find_half_suit(card)] += 1
            if self.hs_info[ID_target][card_utils.find_half_suit(card)] > 0:
                self.hs_info[ID_target][card_utils.find_half_suit(card)] -= 1
        else:
            self.info[ID_ask][card] = NO
            self.info[ID_target][card] = NO
            self.public_info[ID_ask][card] = NO
            self.public_info[ID_target][card] = NO
            if self.hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
        self._update_info()
        self._update_public_info()

    def update_call(self, hs, card_count_hs):
        """
        Given a half suit being called, update the player's info and half suit info
        This essentially sets the info on all players to knowing that they don't have cards in that half suit

        hs: the half suit being called
        card_count_hs: the number of cards that each player had in the half suit
        This is a dictionary of {Player ID: num_cards}

        Note that there's no difference whether the call succeeds or fails!
        """
        for ID in range(6):
            for card in card_utils.find_cards(hs):
                self.info[ID][card] = NO
                self.public_info[ID][card] = NO
            self.hs_info[ID][hs] = 0
            self.num_cards[ID] -= card_count_hs[ID]
        self._update_info()
        self._update_public_info()

    def own_cards(self):
        """
        Returns a list of the cards the player currently has
        """
        cards = []
        for c in self.info[self.ID]:
            if self.info[self.ID][c] == YES:
                cards.append(c)
        return cards

    def _check_legal_ask(self, ID_target, card):
        """
        Given a target player and a card to ask, check if the ask is legal
        Conditions for legality:
        1. You must have a card in the same half suit
        2. You must not have that card
        3. The person you ask must be on the opposite team

        ID_target: The ID of the person the self wants to ask
        card: the card that we are checking the legality of
        """
        if ID_target % 2 != self.ID % 2:
            if self.info[self.ID][card] == NO:
                for c in card_utils.find_cards(card_utils.find_half_suit(card)):
                    if self.info[self.ID][c] == YES:
                        return True
        return False

    def make_optimal_ask(self):
        """
        Returns the optimal person and card to ask
        Format: (target_player_id, card)
        """
        ask_guarenteed = self._check_card_guarenteed()
        if ask_guarenteed:
            return ask_guarenteed
        # For now, just ask randomly if no obvious card
        target = self._get_opponents()[random.randint(0, 2)]
        valid = []
        for c in card_utils.gen_all_cards():
            if self._check_legal_ask(target, c):
                valid.append(c)
        return target, valid[random.randint(0, len(valid) - 1)]
        # return self._list_best_options()[0]

    def _check_card_guarenteed(self):
        """
        Checks if an opponent player has a card that you know you are guarenteed to guess correctly
        If so, return a tuple (player_id, card)
        If not, return False
        """
        for hs in card_utils.gen_all_halfsuits():
            if self.hs_info[self.ID][hs] > 0:
                for card in card_utils.find_cards(hs):
                    for ID in self._get_opponents():
                        if self.info[ID][card] == YES:
                            return ID, card
        return False

    def _list_best_options(self):
        """
        Returns a list of the highest probability asks you can make, according to self.info
        Ties are broken in this method by the following criteria:
        1. Number of guarenteed cards in half suit
        If player A is guarenteed to have more cards in the half suit than player B, ask them

        This method does not account for the "danger" of asking certain players yet
        """
        best_asks = []
        highest_prob = 0
        most_hs_cards = 0
        for card in card_utils.gen_all_cards():
            for ID in self._get_opponents():
                if self._check_legal_ask(ID, card):
                    if self.info[ID][card] != NO:
                        best_asks = [(ID, card)]
                        highest_prob = self.info[ID][card]
                        most_hs_cards = self.hs_info[ID][card_utils.find_half_suit(card)]
                    elif self.info[ID][card] == highest_prob:
                        if self.hs_info[ID][card_utils.find_half_suit(card)] > most_hs_cards:
                            best_asks = [(ID, card)]
                            most_hs_cards = self.hs_info[ID][card_utils.find_half_suit(card)]
                        elif self.hs_info[ID][card_utils.find_half_suit(card)] == most_hs_cards:
                            best_asks.append((ID, card))
        return best_asks

    def check_call(self):
        """
        Check if you can call a half suit
        Returns a list of tuples like this:
        [(player, card), (player, card) ...]
        If no call can be made, return False
        """
        for hs in card_utils.gen_all_halfsuits():
            call = []
            for card in card_utils.find_cards(hs):
                for ID in self._get_teammates():
                    if self.info[ID][card] == YES:
                        call.append((ID, card))
            if len(call) == 6:
                return call
        return False

    def _get_opponents(self):
        """
        returns the IDs of the opponents
        """
        if self.ID % 2 == 0:
            return 1, 3, 5
        return 0, 2, 4

    def _get_teammates(self):
        """
        returns the ID of your teammates
        """
        if self.ID % 2 == 0:
            return 0, 2, 4
        return 1, 3, 5

    def print_info(self):
        for ID in range(6):
            if self.ID == ID:
                print("Player {} (You)".format(ID))
            else:
                print("Player {}".format(ID))
            known_yes = []
            known_no = []
            for card in card_utils.gen_all_cards():
                if self.info[ID][card] == YES:
                    known_yes.append(card)
                elif self.info[ID][card] == NO:
                    known_no.append(card)
            print("Guarenteed to have: ")
            print(" ".join(known_yes))
            print("Guarenteed to not have: ")
            print(" ".join(known_no))
            print()
