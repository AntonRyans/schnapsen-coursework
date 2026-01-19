from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer, Score
from schnapsen.deck import Suit, Card, Rank


class OppReactBot(Bot):

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves: list[Move] = perspective.valid_moves()
        scorer = SchnapsenTrickScorer()
        trump = perspective.get_trump_suit()

        # -------------------------------
        # OPPONENT BEHAVIOUR DETECTION
        # -------------------------------
        opponent_aggressive = False
        opponent_safe = False

        if leader_move is not None:
            card = leader_move.cards[0]
            points = scorer.rank_to_points(card.rank)

            # Aggressive signals
            if leader_move.is_marriage():
                opponent_aggressive = True
            elif card.suit == trump:
                opponent_aggressive = True
            elif points >= 10:  # Ace or Ten
                opponent_aggressive = True

            # Safe signals
            elif points <= 4:
                opponent_safe = True

        # -------------------------------
        # DEFENSIVE STRATEGY
        # -------------------------------
        if opponent_aggressive:
            # Try to beat trick or minimize loss
            winning_moves = []

            if leader_move is not None:
                leader_card = leader_move.cards[0]
                for move in moves:
                    my_card = move.cards[0]

                    # Same suit and higher rank
                    if my_card.suit == leader_card.suit and \
                       scorer.rank_to_points(my_card.rank) > scorer.rank_to_points(leader_card.rank):
                        winning_moves.append(move)

                    # Trump beats non-trump
                    elif my_card.suit == trump and leader_card.suit != trump:
                        winning_moves.append(move)

            if winning_moves:
                return min(
                    winning_moves,
                    key=lambda m: scorer.rank_to_points(m.cards[0].rank)
                )

            # Otherwise dump lowest-value card
            return min(
                moves,
                key=lambda m: scorer.rank_to_points(m.cards[0].rank)
            )

        # -------------------------------
        # ATTACKING STRATEGY
        # -------------------------------
        if opponent_safe:
            # Prefer marriages
            for move in moves:
                if move.is_marriage():
                    return move

            # Play highest-point card
            return max(
                moves,
                key=lambda m: scorer.rank_to_points(m.cards[0].rank)
            )

        # -------------------------------
        # NEUTRAL FALLBACK
        # -------------------------------
        return moves[0]
