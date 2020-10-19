import unittest
from player import Player
import card_utils
from game import FishGame
from model import FishDecisionMaker
import constants
import copy


class TestPlayer(unittest.TestCase):

    def test_init_info_start_game(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res = p1._init_info_start_game(0, own_hand)
        expected = {}
        own_info = {card: constants.NO for card in card_utils.gen_all_cards()}
        for c in own_hand:
            own_info[c] = constants.YES
        expected[0] = own_info.copy()
        opp_info = {card: constants.UNSURE for card in card_utils.gen_all_cards()}
        for i in range(1, constants.NUM_PLAYERS):
            expected[i] = opp_info.copy()
        self.assertEqual(res, expected, "Failed in init_info_start_game")

    def test_init_hs_info_start_game(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res = p1._init_hs_info_start_game(0, own_hand)
        expected = {}
        opp_hs_info = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        for i in range(1, constants.NUM_PLAYERS):
            expected[i] = opp_hs_info.copy()
        own_hs_info = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        own_hs_info["Lh"] = 6
        own_hs_info["8J"] = 1
        own_hs_info["Hh"] = 2
        expected[0] = own_hs_info.copy()
        self.assertEqual(res, expected, "Failed in init_hs_info_start_game")

    def test_init_public_info_start_game(self):
        p1 = Player.player_start_of_game(0, [])
        res = p1._init_public_info_start_game()
        expected = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(6)}
        self.assertEqual(res, expected, "Failed in init_public_info_start_game")

    def test_init_public_hs_info_start_game(self):
        p1 = Player.player_start_of_game(0, [])
        res = p1._init_public_hs_info_start_game()
        expected = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        self.assertEqual(res, expected, "Failed in init_public_hs_info_start_game")

    def test_update_info(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res = p1.info
        expected = {}
        own_info = {card: constants.NO for card in card_utils.gen_all_cards()}
        for c in own_hand:
            own_info[c] = constants.YES
        expected[0] = own_info.copy()
        opp_info = {card: constants.UNSURE for card in card_utils.gen_all_cards()}
        for c in own_hand:
            opp_info[c] = constants.NO
        for i in range(1, constants.NUM_PLAYERS):
            expected[i] = opp_info.copy()
        self.assertEqual(res, expected, "Failed in test_update_info")

    def test_update_info_5_nos(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        for i in range(1, 5):
            p1.info[i]["Jh"] = constants.NO
        p1._update_info()
        self.assertEqual(p1.info[5]["Jh"], constants.YES, "Did not update correctly")

    def test_update_info_endgame(self):
        own_hand = ["2h", "3h"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.num_cards = {0: 2, 1: 0, 2: 2, 3: 0, 4: 2, 5: 0}
        for c in card_utils.gen_all_cards():
            for ID in range(constants.NUM_PLAYERS):
                if c not in card_utils.find_cards("Lh") or ID in p1._get_opponents():
                    p1.info[ID][c] = constants.NO
        p1.info[2]["4h"] = constants.NO
        p1.info[2]["5h"] = constants.NO
        p1._update_info()
        self.assertEqual(p1.info[4]["4h"], constants.YES, "Did not conclude player 4 had 4h")
        self.assertEqual(p1.info[2]["6h"], constants.YES, "Did not conclude player 2 had 2h")

    @unittest.skip
    def test_printing(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_transaction(1, 2, "BJ", True)
        p1.update_transaction(4, 5, "Jc", True)
        p1.update_transaction(3, 4, "3d", False)
        p1.print_info()

    def test_is_consistent_duplicate_cards(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 1 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        info[0]["2h"] = constants.YES
        info[1]["2h"] = constants.YES
        self.assertFalse(
            Player._is_consistent(info, list(card_utils.gen_all_halfsuits()), hs_info, {ID: 9 for ID in range(constants.NUM_PLAYERS)}),
            "Failed to catch duplicate cards in _is_consistent")

    def test_is_consistent_all_nos(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        for ID in range(constants.NUM_PLAYERS):
            info[ID]["2h"] = constants.NO
        self.assertFalse(Player._is_consistent(info, ["Lh"], hs_info, {ID: 1 for ID in range(constants.NUM_PLAYERS)}),
                         "Failed to catch duplicate cards in _is_consistent")

    def test_is_consistent_all_nos_2(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        for ID in range(5):
            info[ID]["2h"] = constants.NO
        self.assertTrue(Player._is_consistent(info, ["Lh"], hs_info, {ID: 1 for ID in range(constants.NUM_PLAYERS)}),
                        "Incorrectly claimed inconsistency")

    def test_is_consistent_all_nos_3(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        for ID in range(constants.NUM_PLAYERS):
            info[ID]["2h"] = constants.NO
        self.assertTrue(Player._is_consistent(info, ["8J"], hs_info, {ID: 1 for ID in range(constants.NUM_PLAYERS)}),
                        "Incorrectly claimed inconsistency")

    def test_is_consistent_hs(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        hs_info[1]["Hc"] = 4
        info[1]["9c"] = constants.NO
        info[1]["Tc"] = constants.NO
        self.assertTrue(Player._is_consistent(info, list(card_utils.gen_all_halfsuits()), hs_info, {ID: 9 for ID in range(constants.NUM_PLAYERS)}),
                        "Incorrectly claimed inconsistency")

    def test_is_consistent_hs_2(self):
        info = {ID: {card: constants.UNSURE for card in card_utils.gen_all_cards()} for ID in range(constants.NUM_PLAYERS)}
        hs_info = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(constants.NUM_PLAYERS)}
        hs_info[1]["Hc"] = 4
        info[1]["9c"] = constants.NO
        info[1]["Tc"] = constants.NO
        info[1]["Jc"] = constants.NO
        self.assertFalse(Player._is_consistent(info, list(card_utils.gen_all_halfsuits()), hs_info, {ID: 9 for ID in range(constants.NUM_PLAYERS)}),
                        "Did not claim inconsistency")

    def test_update_successful_transaction(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(1, own_hand)
        p1.update_transaction(2, 1, "Th", True)
        self.assertEqual(p1.num_cards[1], 8, "Number of own cards is incorrect")
        self.assertEqual(p1.num_cards[2], 10, "Number of other's cards is incorrect")
        self.assertEqual(p1.info[1]["Th"], constants.NO, "Own info not updated correctly")
        self.assertEqual(p1.info[2]["Th"], constants.YES, "Other player's info not updated correctly")
        self.assertEqual(p1.hs_info[1]["Hh"], 1, "Own half suit info not updated correctly")
        self.assertEqual(p1.hs_info[2]["Hh"], 2, "Other player's half suit info not updated correctly")
        self.assertEqual(p1.public_info[1]["Th"], constants.NO, "Public info for asker not correct")
        self.assertEqual(p1.public_info[2]["Th"], constants.YES, "Public info for target not correct")

    def test_update_failed_transaction(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(1, own_hand)
        p1.update_transaction(2, 1, "Jh", False)
        self.assertEqual(p1.num_cards[1], 9, "Number of own cards is incorrect")
        self.assertEqual(p1.num_cards[2], 9, "Number of other's cards is incorrect")
        self.assertEqual(p1.info[1]["Jh"], constants.NO, "Own info not updated correctly")
        self.assertEqual(p1.info[2]["Jh"], constants.NO, "Other player's info not updated correctly")
        self.assertEqual(p1.hs_info[1]["Hh"], 2, "Own half suit info not updated correctly")
        self.assertEqual(p1.hs_info[2]["Hh"], 1, "Other player's half suit info not updated correctly")
        self.assertEqual(p1.public_info[1]["Jh"], constants.NO, "Own info not updated correctly")
        self.assertEqual(p1.public_info[2]["Jh"], constants.NO, "Other player's info not updated correctly")

    def test_update_multiple_transaction(self):
        own_hand = ["5h", "7h", "Jh", "2d", "Ad", "8c", "SJ", "6s", "6c"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_transaction(3, 4, "9c", False)
        p1.update_transaction(4, 3, "Tc", False)
        p1.update_transaction(3, 4, "Jc", False)
        p1.update_transaction(4, 3, "Qc", False)
        for ID in [3, 4]:
            for card in ["Kc", "Ac"]:
                self.assertEqual(p1.info[ID][card], constants.UNSURE, "Not enough info to know about p{}'s status of {}".format(ID, card))
            self.assertEqual(p1.hs_info[ID]["Hc"], 1, "player {} has incorrect half suit info".format(ID))
            for card in ["9c", "Tc", "Jc", "Qc"]:
                self.assertEqual(p1.info[ID][card], constants.NO, "Did not update p{}'s {}".format(ID, card))

    def test_update_multiple_transaction_2(self):
        own_hand = ["5h", "7h", "Jh", "2d", "Ad", "8c", "SJ", "6s", "6c"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_transaction(3, 4, "9c", True)
        p1.update_transaction(4, 3, "9c", True)
        for ID in [3, 4]:
            for card in ["Tc", "Jc", "Qc", "Kc", "Ac"]:
                self.assertEqual(p1.info[ID][card], constants.UNSURE, "Not enough info to know about p{}'s status of {}".format(ID, card))
        self.assertEqual(p1.hs_info[3]["Hc"], 1, "player 3 has incorrect half suit info")
        self.assertEqual(p1.hs_info[4]["Hc"], 2, "player 4 has incorrect half suit info")
        self.assertEqual(p1.info[3]["9c"], constants.NO, "4 did not take back 3's 9c")
        self.assertEqual(p1.info[4]["9c"], constants.YES, "4 did not take back 3's 9c")

    @unittest.skipIf(constants.NUM_PLAYERS != 6, "only works for 6 players")
    def test_update_call(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_call("8J", {0: 1, 1: 0, 2: 2, 3: 0, 4: 3, 5: 0})
        self.assertEqual(p1.num_cards, {0: 8, 1: 9, 2: 7, 3: 9, 4: 6, 5: 9}, "Number of cards is incorrect")
        for ID in range(constants.NUM_PLAYERS):
            for card in card_utils.find_cards("8J"):
                self.assertEqual(p1.info[ID][card], constants.NO, "A player still has a card in the called half suit")
            self.assertEqual(p1.hs_info[ID]["8J"], 0,
                             "A player is still marked as having at least 1 card in the half suit")

    def test_make_optimal_ask_guarenteed(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_transaction(1, 0, "9h", True)
        res_ID, res_card = p1.make_optimal_ask()
        expected_ID, expected_card = (1, "9h")
        self.assertEqual(res_ID, expected_ID, "Did not ask the correct player")
        self.assertEqual(res_card, expected_card, "Did not ask the correct card")

    def test_make_optimal_ask_unsure(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res_ID, res_card = p1.make_optimal_ask()
        self.assertEqual(p1.info[res_ID][res_card], constants.UNSURE, "Did not ask for a card that was unsure")
        self.assertEqual(res_ID % 2, 1, "Did not ask an opponent")

    def test_check_call(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res = p1.check_call()
        expected = [(0, x) for x in card_utils.find_cards("Lh")]
        self.assertTrue(res, "Did not call")
        self.assertEqual(res, expected, "Did not attribute the cards with the correct player")

    def test_check_call_other_players(self):
        own_hand = ["2h", "9h", "2d", "9d", "2c", "9c", "2s", "9s", "8c"]
        p1 = Player.player_start_of_game(0, own_hand)
        for card in ["3h", "4h", "5h", "6h"]:
            p1.update_transaction(2, 1, card, True)
        res = p1.check_call()
        expected = [(0, "2h")] + [(2, x) for x in ["3h", "4h", "5h", "6h", "7h"]]
        self.assertTrue(res, "Did not call")
        self.assertEqual(res, expected, "Did not call correctly")

    def test_check_call_222_dist(self):
        own_hand = ["2h", "3h", "9h", "Th", "Jh", "8h", "8c", "8d", "BJ"]
        p1 = Player.player_start_of_game(0, own_hand)
        for opp in p1._get_opponents():
            p1.update_transaction(2, opp, "6h", False)
            p1.update_transaction(2, opp, "7h", False)
            p1.update_transaction(4, opp, "4h", False)
            p1.update_transaction(4, opp, "5h", False)
        res = p1.check_call()
        expected = [(0, "2h"), (0, "3h"), (2, "4h"), (2, "5h"), (4, "6h"), (4, "7h")]
        self.assertTrue(res, "Did not call")
        self.assertEqual(res, expected, "Call was incorrect")


class TestGame(unittest.TestCase):

    def test_init_random_game(self):
        random_game = FishGame.start_random_game([FishDecisionMaker() for i in range(constants.NUM_PLAYERS)])
        self.assertEqual(len(random_game.players), constants.NUM_PLAYERS, "Number of players is not " + str(constants.NUM_PLAYERS))
        all_cards_dict = {c: 0 for c in card_utils.gen_all_cards()}
        for i in range(constants.NUM_PLAYERS):
            self.assertEqual(len(random_game.players[i].own_cards()), 9, "Player {} does not have 9 cards".format(i))
            for c in random_game.players[i].own_cards():
                all_cards_dict[c] += 1
        for card, count in all_cards_dict.items():
            self.assertEqual(count, 1, "{} shows up {} times instead of once".format(card, count))

    @unittest.skipIf(constants.NUM_PLAYERS != 6, "only works for 6 players")
    def test_init_specific_game(self):
        models = [FishDecisionMaker() for i in range(constants.NUM_PLAYERS)]
        specific_game = FishGame([["2h"], ["3h"], ["4h"], ["5h"], ["6h"], ["7h"]], models, 0, 0, 0)
        self.assertEqual(specific_game.players[0].own_cards(), ["2h"], "Player ID 0 has the wrong cards")
        self.assertEqual(specific_game.players[1].own_cards(), ["3h"], "Player ID 1 has the wrong cards")
        self.assertEqual(specific_game.players[2].own_cards(), ["4h"], "Player ID 2 has the wrong cards")
        self.assertEqual(specific_game.players[3].own_cards(), ["5h"], "Player ID 3 has the wrong cards")
        self.assertEqual(specific_game.players[4].own_cards(), ["6h"], "Player ID 4 has the wrong cards")
        self.assertEqual(specific_game.players[5].own_cards(), ["7h"], "Player ID 5 has the wrong cards")

    @unittest.skipIf(constants.NUM_PLAYERS != 6, "only works if 6 players")
    def test_update_call(self):
        models = [FishDecisionMaker() for i in range(constants.NUM_PLAYERS)]
        specific_game = FishGame([["2h", "9h"], ["3h", "Th"], ["4h", "Jh"], ["5h", "Qh"], ["6h", "Kh"], ["7h", "Ah"]],
                                 models, 0, 4, 3)
        specific_game.report_call("Lh")
        cards_remaining = [["9h"], ["Th"], ["Jh"], ["Qh"], ["Kh"], ["Ah"]]
        for i in range(6):
            self.assertEqual(specific_game.players[i].own_cards(), cards_remaining[i],
                             "Player {} has the wrong cards".format(i))

    @unittest.skipIf(constants.NUM_PLAYERS != 6, "only works if 6 players")
    def test_update_ask_successful(self):
        models = [FishDecisionMaker(applicable_players=(0,)) for i in range(constants.NUM_PLAYERS)]
        specific_game = FishGame([["2h", "9h"], ["3h", "Th"], ["4h", "Jh"], ["5h", "Qh"], ["6h", "Kh"], ["7h", "Ah"]],
                                 models, 0, 0, 0, train=False)
        specific_game.report_ask(0, 1, "3h", True)
        self.assertIn("3h", specific_game.players[0].own_cards(), "3h was not successfully received")
        self.assertIn("3h", specific_game.player_cards[0], "3h was not successfully added to player 0 cards")
        self.assertNotIn("3h", specific_game.players[1].own_cards(), "3h was not successfully taken")
        self.assertNotIn("3h", specific_game.player_cards[1], "3h was not removed from player 1 cards")
        for i in range(2, 6):
            self.assertEqual(specific_game.players[i].info[0]["3h"], constants.YES,
                             "Player {} doesn't know about the transaction".format(i))
            self.assertEqual(specific_game.players[i].info[1]["3h"], constants.NO,
                             "Player {} doesn't know about the transaction".format(i))

    @unittest.skipIf(constants.NUM_PLAYERS != 6, "only works if 6 players")
    def test_update_ask_unsuccessful(self):
        models = [FishDecisionMaker(applicable_players=(0,)) for i in range(constants.NUM_PLAYERS)]
        specific_game = FishGame([["2h", "9h"], ["3h", "Th"], ["4h", "Jh"], ["5h", "Qh"], ["6h", "Kh"], ["7h", "Ah"]],
                                 models, 0, 0, 0, train=False)
        specific_game.report_ask(0, 1, "Jh", False)
        self.assertNotIn("Jh", specific_game.players[0].own_cards(), "Jh was incorrectly received")
        self.assertNotIn("Jh", specific_game.player_cards[0], "Jh was incorrectly added to player 0's cards")
        self.assertNotIn("Jh", specific_game.players[1].own_cards(), "Jh was added to player 1 even though they didn't have the card")
        self.assertNotIn("Jh", specific_game.player_cards[1], "Jh was added to player 1 even though they didn't have the card")
        for i in range(2, 6):
            self.assertEqual(specific_game.players[i].info[0]["Jh"], constants.NO,
                             "Player {} doesn't know about the transaction".format(i))
            self.assertEqual(specific_game.players[i].info[1]["Jh"], constants.NO,
                             "Player {} doesn't know about the transaction".format(i))

    def test_play_random_fish_game(self):
        models = [FishDecisionMaker(applicable_players=tuple(range(constants.NUM_PLAYERS))) for i in range(constants.NUM_PLAYERS)]
        game = FishGame.start_random_game(models, train=False)
        max_turns = 500
        result = game.run_whole_game(verbose=2, max_turns=max_turns)
        if result:
            print("Game went on >{} turns".format(max_turns))


class TestModel(unittest.TestCase):

    def test_generate_state_vector(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        player = Player.player_start_of_game(0, own_hand)
        state_vector_res = FishDecisionMaker.generate_state_vector(player.info, player.hs_info, player.num_cards,
                                                                   player.public_info, player.public_hs_info, 0, 0)
        state_vector_expected = []
        for i in range(constants.NUM_PLAYERS):
            for c in card_utils.gen_all_cards():
                if i == 0 and c in own_hand:
                    state_vector_expected.append(constants.YES)
                elif i == 0:
                    state_vector_expected.append(constants.NO)
                elif c in own_hand:
                    state_vector_expected.append(constants.NO)
                else:
                    state_vector_expected.append(constants.UNSURE)
        state_vector_expected += [constants.UNSURE for i in range(324)] # public info
        state_vector_expected += [0, 0, 0, 0, 6, 2, 0, 0, 1] # your hs info
        state_vector_expected += [0 for i in range(45)] # Rest of hs info
        state_vector_expected += [0 for i in range(54)] # Public hs info
        state_vector_expected += [9 for i in range(6)] # num cards
        state_vector_expected += [0]
        self.assertEqual(len(state_vector_res), len(state_vector_expected), "Length of state vector not correct")
        self.assertEqual(state_vector_res, state_vector_expected, "State vector not correct")

    def test_generate_action_number(self):
        action_res = FishDecisionMaker.generate_action_number(2, 5, "BJ")
        self.assertEqual(action_res, 107)

    def test_create_new_histories(self):
        model = FishDecisionMaker(applicable_players=(0,))
        model.create_new_histories(1)
        self.assertEqual(model.state_history, {0: [[]]}, "state history not created correctly")
        self.assertEqual(model.action_history, {0: [[]]}, "action history not created correctly")
        self.assertEqual(model.rewards_history, {0: [[]]}, "rewards history not created correctly")

    def test_multiple_players(self):
        model = FishDecisionMaker(applicable_players=(0,1))
        model.create_new_histories(1)
        self.assertEqual(model.state_history, {0: [[]], 1: [[]]}, "state history not created correctly")
        self.assertEqual(model.action_history, {0: [[]], 1: [[]]}, "action history not created correctly")
        self.assertEqual(model.rewards_history, {0: [[]], 1: [[]]}, "rewards history not created correctly")

    def test_update_data(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        model = FishDecisionMaker(applicable_players=(0,))
        model.create_new_histories(1)
        player = Player.player_start_of_game(0, own_hand, train=False)
        info_i = copy.deepcopy(player.info)
        hs_info_i = copy.deepcopy(player.hs_info)
        num_cards_i = copy.deepcopy(player.num_cards)
        public_info_i = copy.deepcopy(player.public_info)
        public_hs_info_i = copy.deepcopy(player.public_hs_info)
        player.update_transaction(0, 1, "Jh", True)
        info_f = player.info
        hs_info_f = player.hs_info
        num_cards_f = player.num_cards
        public_info_f = player.public_info
        public_hs_info_f = player.public_hs_info
        model.update_data(0, info_i, hs_info_i, num_cards_i, public_info_i, public_hs_info_i,
                          info_f, hs_info_f, num_cards_f, public_info_f, public_hs_info_f,
                          0, 1, "Jh", True, 0)
        state_i = model.generate_state_vector(info_i, hs_info_i, num_cards_i, public_info_i, public_hs_info_i, 0, 0)
        state_f = model.generate_state_vector(info_f, hs_info_f, num_cards_f, public_info_f, public_hs_info_f, 0, 0)
        state_expected = {0: [[(state_i, state_f)]]}
        action_expected = {0: [[model.generate_action_number(0, 1, "Jh")]]}
        reward_expected = {0: [[1]]}
        self.assertEqual(model.state_history, state_expected, "state history not correct")
        self.assertEqual(model.action_history, action_expected, "action history not correct")
        self.assertEqual(model.rewards_history, reward_expected, "reward history not correct")


if __name__ == "__main__":
    unittest.main(verbosity=2)