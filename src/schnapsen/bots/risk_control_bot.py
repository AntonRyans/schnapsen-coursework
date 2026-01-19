from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer, Score
from schnapsen.deck import Suit, Card, Rank


class riskControlBot(Bot):

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves = perspective.valid_moves()
        scorer = SchnapsenTrickScorer()
        trump = perspective.get_trump_suit()

        # -------------------------------
        # SCORE DIFFERENCE (RISK CONTROL)
        # -------------------------------
        my_score: Score = perspective.get_my_score()
        opp_score: Score = perspective.get_opponent_score()

        my_total = my_score.direct_points + my_score.pending_points
        opp_total = opp_score.direct_points + opp_score.pending_points

        losing = my_total < opp_total
        winning = my_total > opp_total

        # -------------------------------
        # MOVE CLASSIFICATION
        # -------------------------------
        def is_uncertain(move: Move) -> bool:
            if move.is_marriage():
                return True

            card = move.cards[0]
            points = scorer.rank_to_points(card.rank)

            # High value card
            if points >= 10:
                return True

            # Trump usage when not forced
            if leader_move is not None:
                leader_card = leader_move.cards[0]
                if card.suit == trump and leader_card.suit != trump:
                    return True

            return False

        def reward_value(move: Move) -> int:
            if move.is_marriage():
                return 40
            return scorer.rank_to_points(move.cards[0].rank)

        # -------------------------------
        # WHEN WINNING → AVOID UNCERTAINTY
        # -------------------------------
        if winning:
            safe_moves = [m for m in moves if not is_uncertain(m)]

            if safe_moves:
                return min(
                    safe_moves,
                    key=lambda m: scorer.rank_to_points(m.cards[0].rank)
                )

            # If forced, take lowest-risk uncertain move
            return min(
                moves,
                key=lambda m: reward_value(m)
            )

        # -------------------------------
        # WHEN LOSING → ALLOW RISK
        # -------------------------------
        if losing:
            return max(
                moves,
                key=lambda m: reward_value(m)
            )

        # -------------------------------
        # NEUTRAL STATE
        # -------------------------------
        return moves[0]
