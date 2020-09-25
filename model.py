import tensorflow
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import card_utils
import constants


class FishDecisionMaker(keras.Sequential):
    """
    A decision maker for the player class for Fish.
    This class is a neural network that takes in the game state and
    predicts which player to ask and which card to ask for
    This class is a shared model between all 6 bots in the virtual fish game
    They all use the same logic and train together (not sure if that's a good idea)

    Also note that this model only predicts what cards to ask,
    not when to call.
    When to call is hardcoded (It is when the players know excactly a half suit)

    This model trains on data collected from virtual games
    """

    def __init__(self, *layers, **compile_options):
        """
        Creates the neural network with an architecture given by layers
        :param *layers: A sequential list of Layer Objects defined in keras (ex. InputLayer)
        :param **options: A list of compile options used to compile the network
        """
        super().__init__()
        for l in layers:
            self.add(l)
        self.compile(**compile_options)
        self.action_history = []
        self.state_history = []
        self.rewards_history = []
        self.done_history = []

    def update_data(self, info, hs_info, num_cards, public_info, public_hs_info,
                    ID_ask, ID_target, card, success):
        """
        Updates the history lists of the model, given a transaction and state
        :param info: defined in Player class
        :param hs_info: defined in Player class
        :param num_cards: defined in Player class
        :param public_info: defined in Player class
        :param ID_ask: ID of asker
        :param ID_target: ID of target
        :param card: Card being asked for
        :param success: Was the ask successful
        :param done: has the game finished?
        """
        self.state_history.append(self.generate_state_vector(info, hs_info, num_cards, public_info,
                                                             public_hs_info, ID_ask))
        self.action_history.append(self.generate_action_number(ID_ask, ID_target, card))
        self.rewards_history.append(self.generate_reward_ask(success))
        self.done_history.append(False)

    @staticmethod
    def generate_state_vector(info, hs_info, num_cards, public_info, public_hs_info, ID_player):
        """
        Generates a state vector from the player's information

        The structure of the state vector is as follows:
        Length: 762 (SIZE_STATES)
        The order of players in each section starts with the ID of the player
        and counts up mod 6 (example: 3, 4, 5, 0, 1, 2)
        The order of cards is defined in card_utils.gen_all_cards
        The first 54 * 6 = 324 entries are for the info dict, with the values
        being the same as in the info dict
        The next 54 * 6 = 324 entries are for the public_info dict, with the values
        being the same as in the public_info dict
        The next 9 * 6 = 54 entries are for the hs_info, with the values
        being the same as in the hs_info dict
        The last 6 entries are the number of cards each player has

        :param info: defined in Player class
        :param hs_info: defined in Player class
        :param num_cards: defined in Player class
        :param public_info: defined in Player class
        :param ID_player: ID of the player
        :return: a state vector
        """
        player_order = list(range(6))[ID_player:] + list(range(6))[:ID_player]
        state = []
        # Info dict
        for ID in player_order:
            for card in card_utils.gen_all_cards():
                state.append(info[ID][card])
        # Public Info dict
        for ID in player_order:
            for card in card_utils.gen_all_cards():
                state.append(public_info[ID][card])
        # Half suit info dict
        for ID in player_order:
            for hs in card_utils.gen_all_halfsuits():
                state.append(hs_info[ID][hs])
        # Public half suit info dict
        for ID in player_order:
            for hs in card_utils.gen_all_halfsuits():
                state.append(public_hs_info[ID][hs])
        # Num cards
        for ID in player_order:
            state.append(num_cards[ID])
        return state

    @staticmethod
    def generate_action_number(ID_ask, ID_target, card):
        """
        Generates an action vector from the player's action
        This vector is universal to all players, meaning it is independent of player ID
        For example, player 0 asking player 3 for a Jc will return the ]
        same vector as player 1 asking player 4 for a Jc
        This is to ensure that the model can be used universally among all players
        :param ID_ask: ID of player asking
        :param ID_target: ID of target
        :param card: Card being asked
        :return: Action number (0-161)
        """
        player_num = (((ID_target - ID_ask) % 6) - 1) // 2
        card_num = list(card_utils.gen_all_cards()).index(card)
        return player_num * constants.DECK_SIZE + card_num

    @staticmethod
    def generate_reward_ask(success):
        """
        Generates a reward based on whether the ask was a success
        :param success:
        :return: reward
        """
        if success:
            return constants.REWARD_SUCCESSFUL_ASK
        return constants.REWARD_UNSUCCESSFUL_ASK

    def update_game_done(self, win):
        """
        Changes the rewards in the final state (right before the game ends) to win or lose

        Also creates a new game done state
        :param win: did the player win
        """
        self.done_history[-1] = True
        if win:
            self.rewards_history[-1] = constants.REWARD_WIN
        else:
            self.rewards_history[-1] = constants.REWARD_LOSE

    def fit(self, history_length,
            batch_size=None,
            epochs=1,
            verbose=1,
            callbacks=None,
            validation_split=0.,
            validation_data=None,
            shuffle=True,
            class_weight=None,
            sample_weight=None,
            initial_epoch=0,
            steps_per_epoch=None,
            validation_steps=None,
            validation_batch_size=None,
            validation_freq=1,
            max_queue_size=10,
            workers=1,
            use_multiprocessing=False):
        """
        Fits the model with q learning y values and states for x values
        :param history_length: maximum number of games to fit history on
        Other parameters are inherited from superclass
        """
        i = len(self.done_history) - 1
        count = 0
        while i > 0 and count < history_length + 1:
            if self.done_history[i]:
                count += 1
            i -= 1
        i += 1
        x = np.array(self.state_history[i:])
        actions = np.array(self.action_history[i:])
        target = self.rewards_history[i:] + constants.GAMMA * np.max()
        self.fit(x, y, batch_size, epochs, verbose, callbacks, validation_split,
                  validation_data, shuffle, class_weight, sample_weight, initial_epoch,
                  steps_per_epoch, validation_steps, validation_batch_size, validation_freq,
                  max_queue_size, workers, use_multiprocessing)