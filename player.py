import card_utils
import random
from constants import YES, NO, UNSURE
from exceptions import InfoDictException
import copy
import model


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

    The player also stores a model for decision making and whether to train or not
    in the parameters
    model and train

    Important methods:
    Take in a Transaction object and update the info data structure with the information
    Determine the "optimal" play that it can make
    Determine whether to call, and which half suit
    """

    def __init__(self, ID, num_cards, info, public_info, hs_info, public_hs_info, remaining_hs,
                 model=model.FishDecisionMaker(), train=True, name=None):
        """
        Initializes the player with the information:
        :param ID: a number in the range 0-5 that denotes the team of the player.
        IDs are universally agreed on by all players
        ID numbers 1, 3, and 5 are on 1 team
        :param Num_cards:
        A dictionary that stores the id of the player and how many cards each player has
        :param info: Info dictionary defined above
        :param public_info: A dictionary that stores the public information available
        to all players as defined above
        :param hs_info: Defined above
        :param public_hs_info: public info dictionary for half suit information
        :param remaining_hs: A list of all the called half suits
        :param model: A keras model for decision making for asking
        :param train: Is the player training
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
        self.public_hs_info = public_hs_info
        self.remaining_hs = remaining_hs
        self.model = model
        self.train = train
        self._update_info()
        self._update_public_info()

    @classmethod
    def player_start_of_game(cls, ID, own_cards, model=model.FishDecisionMaker(), train = True, name=None):
        """
        This initialization corresponds to the initialization at the start of a fish game
        Assumes that everyone has 9 cards
        """
        num_cards = {x: 9 for x in range(6)}
        return cls(ID, num_cards, cls._init_info_start_game(ID, own_cards),
                   cls._init_public_info_start_game(),
                   cls._init_hs_info_start_game(ID, own_cards),
                   cls._init_public_hs_info_start_game(),
                   list(card_utils.gen_all_halfsuits()),
                   model, train, name)

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

    @staticmethod
    def _init_public_hs_info_start_game():
        """
        Returns the public half suit info at the start of a game
        (This is just an empty dictionary)
        """
        public_hs_info = {}
        for ID in range(6):
            d = {}
            for hs in card_utils.gen_all_halfsuits():
                d[hs] = 0
            public_hs_info[ID] = d
        return public_hs_info

    def _update_info(self, check_cards=tuple(card_utils.gen_all_cards())):
        self.info = self._update_recurse(copy.deepcopy(self.info), self.remaining_hs,
                                         self.hs_info, self.num_cards, check_cards=check_cards)

    def _update_public_info(self, check_cards=tuple(card_utils.gen_all_cards())):
        self.public_info = self._update_recurse(copy.deepcopy(self.public_info), self.remaining_hs,
                                                self.public_hs_info, self.num_cards, check_cards=check_cards)

    @staticmethod
    def _update_recurse(info_dict, remaining_hs, hs_info, num_cards, check_cards):
        """
        Recursively updates entries in an info dictionary to YES or NO
        This method works by assuming either YES or NO for all unsure cards
        then checking for contradictions
        If there is a contradiction, the other option must be correct
        If there is no contradiction for either YES or NO, then leave as UNSURE

        This function is expensive!
        :param info_dict: either a public info dict or player info dict
        :param remaining_hs: remaining half suits
        :param hs_info: half suit info
        :param num_cards: each players number of cards
        :param check_cards: list of cards to check for updates to info
        :return: an updated info dictionary
        """
        changed = True
        while changed:
            changed = False
            for ID in range(6):
                for c in check_cards:
                    if info_dict[ID][c] == UNSURE:
                        res = UNSURE
                        info_dict[ID][c] = YES
                        if not Player._is_consistent(info_dict, remaining_hs, hs_info, num_cards, check_cards):
                            res = NO
                            changed = True
                        info_dict[ID][c] = NO
                        if not Player._is_consistent(info_dict, remaining_hs, hs_info, num_cards, check_cards):
                            res = YES
                            changed = True
                        info_dict[ID][c] = res
        return info_dict

    @staticmethod
    def _is_consistent(info_dict, remaining_hs, hs_info, num_cards, check_cards=tuple(card_utils.gen_all_cards())):
        """
        Checks if an info dictionary is consistent. If the info dictionary
        has a contradiction, returns false. Otherwise returns true.

        Info dictionaries must follow these rules:
        1. No two players can have YES for the same card
        2. If the half suit has not been called yet, at least 1 player
        must have at least the possibility of having any card
        in that half suit
        3. If a player has at least X cards in a half suit, they cannot have
        more than 6-X cards being NO in that half suit
        4. If a player has X cards in their hand, they cannot have more than
        54-X cards being NO
        :param info_dict: either a public info dict or player info dict
        :param remaining_hs: the remaining half suits in the game
        :param hs_info: the half suit info
        :param num_cards: number of each players cards
        :param check_cards: cards to check for consistency
        :return: True if consistent, false otherwise
        """
        # Calculate check_hs based on check_cards
        check_hs = set([])
        for c in check_cards:
            hs = card_utils.find_half_suit(c)
            if hs not in check_hs and hs in remaining_hs:
                check_hs.add(hs)
        # Rule 1
        for card in check_cards:
            players_yes = 0
            for ID in range(6):
                if info_dict[ID][card] == YES:
                    players_yes += 1
            if players_yes > 1:
                return False
        # Rule 2
        for hs in check_hs:
            for card in card_utils.find_cards(hs):
                players_no = 0
                for ID in range(6):
                    if info_dict[ID][card] == NO:
                        players_no += 1
                if players_no == 6:
                    return False
        # Rule 3
        for hs in check_hs:
            for ID in range(6):
                hs_no_count = 0
                for card in card_utils.find_cards(hs):
                    if info_dict[ID][card] == NO:
                        hs_no_count += 1
                if hs_info[ID][hs] + hs_no_count > 6:
                    return False
        # Rule 4
        for ID in range(6):
            no_count = 0
            for card in card_utils.gen_all_cards():
                if info_dict[ID][card] == NO:
                    no_count += 1
            if num_cards[ID] + no_count > 54:
                return False
        return True

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
            if self.public_hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.public_hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
            self.public_hs_info[ID_ask][card_utils.find_half_suit(card)] += 1
            if self.hs_info[ID_target][card_utils.find_half_suit(card)] > 0:
                self.hs_info[ID_target][card_utils.find_half_suit(card)] -= 1
            if self.public_hs_info[ID_target][card_utils.find_half_suit(card)] > 0:
                self.public_hs_info[ID_target][card_utils.find_half_suit(card)] -= 1
        else:
            self.info[ID_ask][card] = NO
            self.info[ID_target][card] = NO
            self.public_info[ID_ask][card] = NO
            self.public_info[ID_target][card] = NO
            if self.hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
            if self.public_hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.public_hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
        self._update_info(card_utils.find_cards(card_utils.find_half_suit(card)))
        self._update_public_info(card_utils.find_cards(card_utils.find_half_suit(card)))
        self._update_model(ID_ask, ID_target, card, success)

    def update_call(self, hs, card_count_hs):
        """
        Given a half suit being called, update the player's info and half suit info
        This essentially sets the info on all players to knowing that they don't have cards in that half suit

        hs: the half suit being called
        card_count_hs: the number of cards that each player had in the half suit
        This is a dictionary of {Player ID: num_cards}

        Note that there's no difference whether the call succeeds or fails!
        """
        self.remaining_hs.remove(hs)
        for ID in range(6):
            for card in card_utils.find_cards(hs):
                self.info[ID][card] = NO
                self.public_info[ID][card] = NO
            self.hs_info[ID][hs] = 0
            self.public_hs_info[ID][hs] = 0
            self.num_cards[ID] -= card_count_hs[ID]
        self._update_info()
        self._update_public_info()

    def update_gameover(self, win):
        """
        Updates the latest reward of the model
        :param win: did the player win
        """
        self.model.update_gameover(win)

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

    def force_call(self, hs):
        """
        Forces the player to call the half suit hs.
        Typically this happens at the end of the game
        :param hs: half suit that is being forced
        :return: A "call" list of tuples
        [(player, card), (player, card) ...]
        """
        call = []
        teammates = self._get_teammates()
        for card in card_utils.find_cards(hs):
            found = False
            for ID in range(6):
                if self.info[ID][card] == YES and ID in teammates:
                    call.append((ID, teammates))
                    found = True
            if not found:
                call.append(teammates[random.randint(0, 2)], call)
        return call

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

    def _update_model(self, ID_ask, ID_target, card, success):
        """
        Updates the model of the player based on transaction
        This only updates the information in the model, not the actual model
        The actual model is updated in model
        :param ID_ask: ID of asker
        :param ID_target: ID of target
        :param card: card being asked
        :param success: is the action successful
        """
        self.model.update_data(self.info, self.hs_info, self.num_cards, self.public_info, self.public_hs_info,
                               ID_ask, ID_target, card, success)
