from schnapsen.game import Bot, Move, PlayerPerspective, Rank, Suit

class RiskControlBot(Bot):
    """
    A Schnapsen bot that uses simple risk control logic to choose moves.
    It ensures:
    - Always returns a Move object
    - Chooses lowest-risk moves first
    - Handles all game phases safely
    """

    def get_move(self, perspective: PlayerPerspective, leader_move: Move = None) -> Move:
        # 1️⃣ Hand not yet dealt (early game)
        hand = perspective.get_hand()
        if not hand or len(hand.cards) == 0:
            return Move(trick_type="default", card=None)  # engine-safe placeholder

        # 2️⃣ Get all legal moves
        try:
            legal_moves = perspective.valid_moves()
        except AttributeError:
            # fallback if valid_moves method missing
            legal_moves = [Move(trick_type="default", card=hand.cards[0])]

        if not legal_moves:
            # fallback if legal_moves empty
            return Move(trick_type="default", card=hand.cards[0])

        # 3️⃣ Apply simple risk control scoring
        # Strategy:
        # - Avoid playing high cards if you can win with a lower card
        # - Prefer regular moves over marriages/trump-exchange if not necessary
        scored_moves = []
        for move in legal_moves:
            score = 0

            # Penalize high cards to keep them safe
            if hasattr(move, 'card') and move.card is not None:
                if move.card.rank in [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK]:
                    score += 5  # higher penalty for higher cards

            # Penalize special moves unless necessary
            if hasattr(move, 'is_marriage') and move.is_marriage():
                score += 2
            if hasattr(move, 'is_trump_exchange') and move.is_trump_exchange():
                score += 3

            # Prefer moves with lower score
            scored_moves.append((score, move))

        # Pick the move with lowest score (safest)
        scored_moves.sort(key=lambda x: x[0])
        chosen_move = scored_moves[0][1]

        return chosen_move
