import card_utils
import transaction

class Player:
    """
    The player class represents each of the players in a Fish game.
    It is responsible for storing the following information:

    id: the id of the Player (1-6)
    name: the name of the player (This is technically meaningless for the game state)
    num_cards: the number of cards that each of the 6 players have
    info: a dictionary that stores the "status" of the cards for each player
    hs_info: a dictionary that stores at least how many cards of each half suit each player has

    The structure of the info dictionary is like this:
    {
    player id: 
        {
        Card name: status
        }
    }
    Where status is one of:
    "Y": target player is guarenteed to have the card
    "N": target player is guarenteed to not have the card
    "?": no information about whether the target player has the card or not

    The structure of the half suit info dictionary is like this:
    {
    player id: 
        {
        Half suit name: status
        }
    }
    Where status is one of:
    "Y": target player is guarenteed to have the card
    "N": target player is guarenteed to not have the card
    "?": no information about whether the target player has the card or not

    Important methods:
    Take in a Transaction object and update the info data structure with the information
    Determine the "optimal" play that it can make
    Determine whether to call, and which half suit
    """
    def __init__(self, ID, num_cards, info, hs_info, name = None):
        """
        Initializes the player with the information:
        ID: a number in the range 1-6 that denotes the team of the player.
        IDs are universally agreed on by all players
        ID numbers 1, 3, and 5 are on 1 team

        Name: The name of the player. This field is not relevant to the logic in the game.

        Num_cards:
        A dictionary that stores the id of the player and how many cards each player has

        info: stores the information that the current player knows about each player.
        Structure:
        {
        player id: 
            {
            Card name: status
            }
        }
        Where status is one of:
        "Y": target player is guarenteed to have the card
        "N": target player is guarenteed to not have the card
        "?": no information about whether the target player has the card or not

        The structure of the half suit info dictionary is like this:
        {
        player id: 
            {
            Half suit name: status
            }
        }
        Where status is one of:
        "Y": target player is guarenteed to have the card
        "N": target player is guarenteed to not have the card
        "?": no information about whether the target player has the card or not

        Since each player knows their own cards, the section of the dictionary corresponding
        to their own id will be completely determined ("Y" or "N")
        """
        self.ID = ID
        self.name = name
        self.num_cards = num_cards
        self.info = info
        self.hs_info = hs_info
        self._update_info()

    @classmethod
    def player_start_of_game(cls, ID, own_cards, name = None):
        """
        This initialization corresponds to the initialization at the start of a fish game
        Assumes that everyone has 9 cards
        """
        num_cards = {x: 9 for x in range(1, 7)}
        return cls(ID, num_cards, cls._init_info_start_game(ID, own_cards), 
                   cls._init_hs_info_start_game(ID, own_cards), name = name)

    @staticmethod
    def _init_info_start_game(ID, own_cards):
        """
        Returns the info dictionary assuming its the start of a new game
        Given your own cards and ID
        """
        info = {}
        for player_id in range(1, 7):
            if player_id == ID:
                player_cards = {card: "N" for card in card_utils.gen_all_cards()}
                for card in own_cards:
                    player_cards[card] = "Y"
            else:
                player_cards = {card: "?" for card in card_utils.gen_all_cards()}
            info[player_id] = player_cards.copy()
        return info

    @staticmethod
    def _init_hs_info_start_game(ID, own_cards):
        """
        Returns the half suit info dictionary assuming its the start of a new game
        Uses data from the already intialized info dictionary
        """
        blank_hs = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        hs_info = {player_id: blank_hs.copy() for player_id in range(1, 7)}
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
        # First check for people with guarenteed cards
        for card in card_utils.gen_all_cards():
            id_exists = 0
            for ID in range(1, 7):
                if self.info[ID][card] == "Y":
                    id_exists = ID
            if id_exists != 0:
                for ID in range(1, 7):
                    if ID != id_exists:
                        if self.info[ID][card] == "Y":
                            raise Exception("Two or more players have the card " + card)
                        elif self.info[ID][card] == "?":
                            self.info[ID][card] = "N"

        # Next check for 5 people with "N"s for a particular card
        for card in card_utils.gen_all_cards():
            possible_list = list(range(1, 7))
            for ID in range(1, 7):
                if self.info[ID][card] == "N":
                    possible_list.remove(ID)
            if len(possible_list) == 1:
                self.info[possible_list[0]][card] == "Y"

        # Now check for when a player has a known half suit but not all known cards in that hs
        for hs in card_utils.gen_all_halfsuits():
            for ID in range(1, 7):
                cards = card_utils.find_cards(hs)
                no_count = 0
                for c in cards:
                    if self.info[ID][c] == "N":
                        no_count += 1
                if no_count == 6 - self.hs_info[ID][hs]:
                    for c in cards:
                        if self.info[ID][c] == "?":
                            self.info[ID][c] = "Y"
                if no_count > 6 - self.hs_info[ID][hs]:
                    raise Exception("Player " + ID + " should have at least " + self.hs_info[ID][hs]
                                    + " cards in the half suit " + hs + ", but doesn't")

    def update_transaction(self, ID_ask, ID_target, card, success):
        """
        Given a transaction, updates the player's info and half suit info

        ID_ask: ID of player asking for the card
        ID_target: player being asked
        card: card being asked
        success: true if card was taken from ID_target
        """
        if success:
            self.num_cards[ID_ask] += 1
            self.num_cards[ID_target] -= 1
            self.info[ID_ask][card] = "Y"
            self.info[ID_target][card] = "N"
            self.hs_info[ID_ask][card_utils.find_half_suit(card)] += 1
            if self.hs_info[ID_target][card_utils.find_half_suit(card)] > 0:
                self.hs_info[ID_target][card_utils.find_half_suit(card)] -= 1
        else:
            self.info[ID_ask][card] = "N"
            self.info[ID_target][card] = "N"
            if self.hs_info[ID_ask][card_utils.find_half_suit(card)] == 0:
                self.hs_info[ID_ask][card_utils.find_half_suit(card)] = 1
        self._update_info()

    def update_call(self, hs, card_count_hs):
        """
        Given a half suit being called, update the player's info and half suit info
        This essentially sets the info on all players to knowing that they don't have cards in that half suit

        hs: the half suit being called
        card_count_hs: the number of cards that each player had in the half suit
        This is a dictionary of {Player ID: num_cards}

        Note that there's no difference whether the call succeeds or fails!
        """
        for ID in range(1, 7):
            for card in card_utils.find_cards(hs):
                self.info[ID][card] = "N"
            self.hs_info[ID][hs] = 0
            self.num_cards[ID] -= card_count_hs[ID]
        self._update_info()

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
        if ID_target % 2 == self.ID % 2 and ID_target != self.ID:
            if self.info[self.ID][card] == "N":
                for c in card_utils.find_cards(find_half_suit(card)):
                    if self.info[self.ID][c] == "Y":
                        return True
        return False

    def make_optimal_play(self):
        """
        Returns the optimal person and card to ask, and whether to call or not
        Returns either 
        (call, (players, cards)) or
        (ask, target_player_id, card)
        """
        call = self._check_call()
        if call:
            return call
        ask_guarenteed = self._check_card_same_hs()
        if ask_guarenteed:
            return ask_guarenteed
        self.print_info()
        return None

    def _check_card_same_hs(self):
        """
        Checks if an opponent player has a card that you know you are guarenteed to guess correctly
        If so, return a tuple (player_id, card)
        If not, return False
        """
        for hs in card_utils.gen_all_halfsuits():
            if self.hs_info[hs] > 0:
                for card in card_utils.find_cards(hs):
                    for ID in self._get_opponents():
                        if self.info[ID][card] == "Y":
                            return (ID, card)
        return False

    def _calculate_danger(self):
        """
        Calculates the expected number of half suits that each opposing player can take
        """


    def _check_call(self):
        """
        Check if you can call a half suit
        Returns a list of tuples like this:
        [(player, card), (player, card) ...]
        If no call can be made, return False
        """
        for hs in card_utils.gen_all_halfsuits():
            call = []
            call_flag = True
            for card in card_utils.find_cards():
                for ID in self._get_teammates():
                    if self.info[ID][card] == "Y":
                        call.append((ID, card))
            if len(call) == 6:
                return call
        return False

    def _get_opponents(self):
        """
        returns the IDs of the opponents
        """
        if self.ID % 2 == 0:
            return (1, 3, 5)
        return (2, 4, 6)

    def _get_teammates(self):
        """
        returns the ID of your teammates
        """
        if self.ID % 2 == 0:
            return (2, 4, 6)
        return (1, 3, 5)

    def print_info(self):
        for ID in range(1, 7):
            if self.ID == ID:
                print ("Player {} (You)".format(ID))
            else:
                print ("Player {}".format(ID))
            known_yes = []
            known_no = []
            for card in card_utils.gen_all_cards():
                if self.info[ID][card] == "Y":
                    known_yes.append(card)
                elif self.info[ID][card] == "N":
                    known_no.append(card)
            print ("Guarenteed to have: ")
            print (" ".join(known_yes))
            print ("Guarenteed to not have: ")
            print (" ".join(known_no))
            print ("\n")