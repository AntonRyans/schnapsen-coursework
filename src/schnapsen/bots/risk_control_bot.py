from schnapsen.game import Bot, Move, PlayerPerspective, Rank, Suit

class RiskControlBot(Bot):

    def get_move(self, perspective: PlayerPerspective, leader_move: Move = None) -> Move:
        # Hand not yet dealt (early game)
        hand = perspective.get_hand()
        if not hand or len(hand.cards) == 0:
            return Move(trick_type="default", card=None) 

        # Get all legal moves
        try:
            legal_moves = perspective.valid_moves()
        except AttributeError:
            # fallback if valid_moves method missing
            legal_moves = [Move(trick_type="default", card=hand.cards[0])]

        if not legal_moves:
            # fallback if legal_moves empty
            return Move(trick_type="default", card=hand.cards[0])

        # Apply simple risk control scoring
        scored_moves = []
        for move in legal_moves:
            score = 0

            # Penalize high cards to keep them safe
            if hasattr(move, 'card') and move.card is not None:
                if move.card.rank in [Rank.ACE, Rank.KING, Rank.QUEEN, Rank.JACK]:
                    score += 5 

            # Penalize special moves unless necessary
            if hasattr(move, 'is_marriage') and move.is_marriage():
                score += 2
            if hasattr(move, 'is_trump_exchange') and move.is_trump_exchange():
                score += 3

            # Prefer moves with lower score
            scored_moves.append((score, move))

        # Pick the move with lowest score 
        scored_moves.sort(key=lambda x: x[0])
        chosen_move = scored_moves[0][1]

        return chosen_move
