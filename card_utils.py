def find_half_suit(card_name):
    """
    given a card name, find the half suit of the card
    Card names are in the following format:
    RankSuit
    ex) 2h, Ts, Qd
    Jokers are BJ and SJ

    Half suits are the following:
    (L/H) for low/high then suit letter
    8J for 8s and Jokers
    ex) Lh, Hh, Ls, 8J
    """
    if card_name in ["BJ", "SJ"] or card_name[0] == "8":
        return "8J"
    if card_name[0] in ["2", "3", "4", "5", "6", "7"]:
        low = "L"
    else:
        low = "H"
    return low + card_name[1]

def find_cards(hs_name):
    """
    Given a half suit name, returns a list of cards in that half suit
    """
    if hs_name == "8J":
        return ["8c", "8d", "8h", "8s", "SJ", "BJ"]
    elif hs_name[0] == "L":
        return [str(r) + hs_name[1] for r in range(2, 8)]
    else:
        return [r + hs_name[1] for r in ["9", "T", "J", "Q", "K", "A"]]

def gen_all_cards():
    """
    Generator that returns all cards
    Order: 2-A of clubs ... spades, then SJ, BJ
    """
    for s in gen_all_suits():
        for r in gen_all_ranks():
            yield r + s
    yield "SJ"
    yield "BJ"

def gen_all_ranks():
    """
    Generator that returns all ranks
    """
    for i in ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]:
        yield i

def gen_all_suits():
    for s in ["c", "h", "d", "s"]:
        yield s

def gen_all_halfsuits():
    for hs in ["Lc", "Hc", "Ld", "Hd", "Lh", "Hh", "Ls", "Hs", "8J"]:
        yield hs