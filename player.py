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
    half_suit_info: a dictionary that stores at least how many cards of each half suit each player has

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
    def __init__(ID, num_cards, info, half_suit_info, name = None):
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
        self.half_suit_info = half_suit_info

    def __init__(ID, own_cards, name = None):
        """
        This initialization corresponds to the initialization at the start of a fish game
        Assumes that everyone has 9 cards
        """
        self.ID = ID
        self.name = name
        num_cards = {x: 9 for x in range(1,7)}
        self.info = _init_info_start_game(ID, own_cards)
        self.half_suit_info = _init_hs_info_start_game()

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
        _update_info()
        return info

    def _init_hs_info_start_game():
        """
        Returns the half suit info dictionary assuming its the start of a new game
        Uses data from the already intialized info dictionary
        """
        blank_hs = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        hs_info = {ID: blank_hs.copy() for ID in range(1, 7)}
        for card in self.info[self.ID]:
            if self.info[self.ID][card] == "Y":
                hs_info[ID][card_utils.find_half_suit(card)] += 1
        return hs_info


    def _update_info():
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
            if not possible_list:
                raise Exception("All players don't have the card " + card)
            elif len(possible_list) == 1:
                self.info[possible_list[0]][card] == "Y"

        # Now check for when a player has a known half suit but not all known cards in that hs
        for hs in gen_all_halfsuits:
            for ID in range(1, 7):
                cards = card_utils.find_cards(hs)
                no_count = 0
                for c in cards:
                    if self.info[ID][c] == "N":
                        no_count += 1
                if no_count == 6 - self.half_suit_info[ID][hs]:
                    for c in cards:
                        if self.info[ID][c] == "?":
                            self.info[ID][c] = "Y"
                if no_count > 6 - self.half_suit_info[ID][hs]:
                    raise Exception("Player " + ID + " should have at least " + self.half_suit_info[ID][hs]
                                    + " cards in the half suit " + hs + ", but doesn't")
