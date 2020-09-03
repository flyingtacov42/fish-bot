import unittest
from player import Player
import card_utils
from game import FishGame
from model import FishDecisionMaker
import constants


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
        for i in range(1, 6):
            expected[i] = opp_info.copy()
        self.assertEqual(res, expected, "Failed in init_info_start_game")

    def test_init_hs_info_start_game(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        res = p1._init_hs_info_start_game(0, own_hand)
        expected = {}
        opp_hs_info = {hs: 0 for hs in card_utils.gen_all_halfsuits()}
        for i in range(1, 6):
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
        expected = {ID: {hs: 0 for hs in card_utils.gen_all_halfsuits()} for ID in range(6)}
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
        for i in range(1, 6):
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
            for ID in range(6):
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

    def test_update_call(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        p1 = Player.player_start_of_game(0, own_hand)
        p1.update_call("8J", {0: 1, 1: 0, 2: 2, 3: 0, 4: 3, 5: 0})
        self.assertEqual(p1.num_cards, {0: 8, 1: 9, 2: 7, 3: 9, 4: 6, 5: 9}, "Number of cards is incorrect")
        for ID in range(6):
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
        random_game = FishGame.start_random_game()
        self.assertEqual(len(random_game.players), 6, "Number of players is not 6")
        all_cards_dict = {c: 0 for c in card_utils.gen_all_cards()}
        for i in range(6):
            self.assertEqual(len(random_game.players[i].own_cards()), 9, "Player {} does not have 9 cards".format(i))
            for c in random_game.players[i].own_cards():
                all_cards_dict[c] += 1
        for card, count in all_cards_dict.items():
            self.assertEqual(count, 1, "{} shows up {} times instead of once".format(card, count))

    def test_init_specific_game(self):
        specific_game = FishGame([["2h"], ["3h"], ["4h"], ["5h"], ["6h"], ["7h"]], 0, 0, 0)
        self.assertEqual(specific_game.players[0].own_cards(), ["2h"], "Player ID 0 has the wrong cards")
        self.assertEqual(specific_game.players[1].own_cards(), ["3h"], "Player ID 1 has the wrong cards")
        self.assertEqual(specific_game.players[2].own_cards(), ["4h"], "Player ID 2 has the wrong cards")
        self.assertEqual(specific_game.players[3].own_cards(), ["5h"], "Player ID 3 has the wrong cards")
        self.assertEqual(specific_game.players[4].own_cards(), ["6h"], "Player ID 4 has the wrong cards")
        self.assertEqual(specific_game.players[5].own_cards(), ["7h"], "Player ID 5 has the wrong cards")

    def test_update_call(self):
        specific_game = FishGame([["2h", "9h"], ["3h", "Th"], ["4h", "Jh"], ["5h", "Qh"], ["6h", "Kh"], ["7h", "Ah"]],
                                 0, 0, 0)
        specific_game.report_call("Lh")
        cards_remaining = [["9h"], ["Th"], ["Jh"], ["Qh"], ["Kh"], ["Ah"]]
        for i in range(6):
            self.assertEqual(specific_game.players[i].own_cards(), cards_remaining[i],
                             "Player {} has the wrong cards".format(i))

    def test_update_ask(self):
        specific_game = FishGame([["2h", "9h"], ["3h", "Th"], ["4h", "Jh"], ["5h", "Qh"], ["6h", "Kh"], ["7h", "Ah"]],
                                 0, 0, 0)
        specific_game.report_ask(0, 1, "3h", True)
        self.assertIn("3h", specific_game.players[0].own_cards(), "3h was not successfully received")
        self.assertNotIn("3h", specific_game.players[1].own_cards(), "3h was not successfully taken")
        for i in range(2, 6):
            self.assertEqual(specific_game.players[i].info[0]["3h"], constants.YES,
                             "Other players don't know about the transaction")
            self.assertEqual(specific_game.players[i].info[1]["3h"], constants.NO,
                             "Other players don't know about the transaction")

    def test_play_random_fish_game(self):
        game = FishGame.start_random_game()
        max_turns = 500
        result = game.run_whole_game(verbose=2, max_turns=max_turns)
        if result:
            print("Game went on >{} turns".format(max_turns))


class TestModel(unittest.TestCase):

    def test_generate_state_vector(self):
        own_hand = ["2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
        player = Player.player_start_of_game(0, own_hand)
        state_vector_res = FishDecisionMaker.generate_state_vector(player.info, player.hs_info, player.num_cards,
                                                                   player.public_info, 0)
        state_vector_expected = []
        for i in range(6):
            for c in card_utils.gen_all_cards():
                if i == 0 and c in own_hand:
                    state_vector_expected.append(constants.YES)
                elif i == 0:
                    state_vector_expected.append(constants.NO)
                elif c in own_hand:
                    state_vector_expected.append(constants.NO)
                else:
                    state_vector_expected.append(constants.UNSURE)
        state_vector_expected += [constants.UNSURE for i in range(324)]
        state_vector_expected += [0, 0, 0, 0, 6, 2, 0, 0, 1]
        state_vector_expected += [0 for i in range(45)]
        state_vector_expected += [9 for i in range(6)]
        self.assertEqual(len(state_vector_res), len(state_vector_expected), "Length of state vector not correct")
        self.assertEqual(state_vector_res, state_vector_expected, "State vector not correct")

    def test_generate_action_number(self):
        action_res = FishDecisionMaker.generate_action_number(3, 6, "BJ")
        self.assertEqual(action_res, 107)


if __name__ == "__main__":
    unittest.main(verbosity=2)