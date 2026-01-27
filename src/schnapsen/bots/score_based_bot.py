from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer, Score
from schnapsen.deck import Suit, Card, Rank


class ScoreBasedBot(Bot):

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves: list[Move] = perspective.valid_moves()
        scorer = SchnapsenTrickScorer()

        # SCORE DIFFERENCE 
        my_score: Score = perspective.get_my_score()
        opp_score: Score = perspective.get_opponent_score()

        my_total = my_score.direct_points + my_score.pending_points
        opp_total = opp_score.direct_points + opp_score.pending_points

        score_diff = my_total - opp_total

        # GAME STATE 
        losing = score_diff < 0
        winning = score_diff > 0

        # RISKY STRATEGY (WHEN LOSING)
        if losing:
            # 1. Prefer marriages (high reward)
            for move in moves:
                if move.is_marriage():
                    return move

            # 2. Play highest-point card (aggressive)
            best_move = max(
                moves,
                key=lambda m: scorer.rank_to_points(m.cards[0].rank)
            )
            return best_move

        # SAFE STRATEGY (WHEN WINNING)
        if winning:
            trump = perspective.get_trump_suit()

            # 1. Prefer low-point non-trump cards
            safe_moves = [
                m for m in moves
                if not m.is_marriage()
                and m.cards[0].suit != trump
            ]

            if safe_moves:
                return min(
                    safe_moves,
                    key=lambda m: scorer.rank_to_points(m.cards[0].rank)
                )

            # 2. Fallback: lowest-point move overall
            return min(
                moves,
                key=lambda m: scorer.rank_to_points(m.cards[0].rank)
            )

        # NEUTRAL (TIED SCORE) 
        # Play middle-ground strategy
        return moves[0]
