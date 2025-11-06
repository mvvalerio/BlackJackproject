from cartas import Hand

class Player:
    def __init__(self):
        self.hands = [Hand()]  # suporte para split, lista de mãos
        self.current_hand = 0

    def reset(self):
        self.hands = [Hand()]
        self.current_hand = 0

    def add_card(self, card):
        self.hands[self.current_hand].add(card)

    def _rank_key(self, card):
        """
        Return a normalized rank key for comparison:
         - Aces => 'A'
         - Face cards (J, Q, K, 'jack', 'queen', 'king') => '10'
         - Numeric ranks => their string numeric value '2'..'10'
         - If rank is stored as int, convert to str
        """
        r = getattr(card, 'rank', None)
        if r is None:
            return None
        # ints -> string
        if isinstance(r, int):
            return str(r)
        rs = str(r).lower()
        if rs in ('a', 'ace'):
            return 'A'
        if rs in ('j', 'q', 'k', 'jack', 'queen', 'king'):
            return '10'
        # Accept 't' or '10'
        if rs in ('t', '10', 'ten'):
            return '10'
        # fallback: return raw lower string
        return rs

    def can_split(self):
        # Only allow split if exactly one hand and that hand has 2 cards
        if len(self.hands) != 1:
            return False

        hand = self.hands[0]

        if len(hand.cards) != 2:
            return False

        c1, c2 = hand.cards[0], hand.cards[1]

        # STRICT: ranks must be EXACTLY equal ("10" == "10", "Q" != "10")
        return c1.rank == c2.rank

    def split(self):
        hand = self.hands[0]
        if self.can_split():
            c1 = hand.cards[0]
            c2 = hand.cards[1]
            self.hands = [Hand(), Hand()]
            self.hands[0].add(c1)
            self.hands[1].add(c2)
            self.current_hand = 0
            return True
        return False

class Dealer(Player):
    def __init__(self):
        super().__init__()

    def should_hit(self):
        best = self.hands[0].best_value()
        return best < 17
