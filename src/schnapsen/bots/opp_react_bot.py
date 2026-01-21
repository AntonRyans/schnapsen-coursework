from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer
from schnapsen.deck import Rank, Suit, Card

class OppReactBot(Bot):
    """
    Smarter opponent-reactive bot for Schnapsen with late-game card counting.
    Fully compatible with tournament code.
    """

    def __init__(self, name: Optional[str] = "OppReactBot") -> None:
        super().__init__(name)
        self.name = name if name is not None else "OppReactBot"
        self.played_cards: set[Card] = set()  # track all seen cards

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves: list[Move] = perspective.valid_moves()
        scorer = SchnapsenTrickScorer()
        trump = perspective.get_trump_suit()

        # Get the bot's current hand safely
        hand_cards = list(getattr(perspective, "hand", []))
        hand_size = len(hand_cards)

        # -------------------------------
        # Update seen cards
        # -------------------------------
        opponent_cards = list(getattr(perspective, "opponent_played_cards", []))
        for card in hand_cards + opponent_cards:
            self.played_cards.add(card)

        # -------------------------------
        # Estimate remaining cards safely
        # -------------------------------
        remaining_cards = [c for c in hand_cards + opponent_cards if c not in self.played_cards]

        remaining_trumps = [c for c in remaining_cards if c.suit == trump]
        remaining_aces_tens = [c for c in remaining_cards if c.rank in [Rank.ACE, Rank.TEN]]

        # -------------------------------
        # Scoring function for moves
        # -------------------------------
        def move_score(move: Move) -> int:
            card = move.cards[0]
            score = scorer.rank_to_points(card.rank)

            # Marriages and trumps are stronger
            if move.is_marriage():
                score += 5
            if card.suit == trump:
                score += 3

            # Save high-value cards early if many remain
            if card.rank in [Rank.ACE, Rank.TEN] and len(remaining_aces_tens) > 2:
                score -= 2

            # Use trumps strategically if many are left
            if card.suit == trump and len(remaining_trumps) > 2:
                score -= 1

            # Late-game: prioritize winning tricks with high cards or trumps
            if hand_size <= 3:
                if card.rank in [Rank.ACE, Rank.TEN] or card.suit == trump:
                    score += 3

            return score

        # -------------------------------
        # Opponent behavior detection
        # -------------------------------
        opponent_aggressive = False
        opponent_safe = False
        if leader_move is not None:
            card = leader_move.cards[0]
            points = scorer.rank_to_points(card.rank)
            if leader_move.is_marriage() or card.suit == trump or points >= 10:
                opponent_aggressive = True
            elif points <= 4:
                opponent_safe = True

        # -------------------------------
        # Defensive play if opponent aggressive
        # -------------------------------
        if opponent_aggressive and leader_move is not None:
            leader_card = leader_move.cards[0]
            winning_moves = []
            for move in moves:
                my_card = move.cards[0]
                if my_card.suit == leader_card.suit and scorer.rank_to_points(my_card.rank) > scorer.rank_to_points(leader_card.rank):
                    winning_moves.append(move)
                elif my_card.suit == trump and leader_card.suit != trump:
                    winning_moves.append(move)
            if winning_moves:
                return min(winning_moves, key=move_score)
            return min(moves, key=move_score)

        # -------------------------------
        # Offensive / neutral play
        # -------------------------------
        if opponent_safe or leader_move is None:
            # Play marriages first if available
            marriage_moves = [m for m in moves if m.is_marriage()]
            if marriage_moves:
                return max(marriage_moves, key=move_score)
            # Otherwise play highest-score move
            return max(moves, key=move_score)

        # -------------------------------
        # Fallback
        # -------------------------------
        return min(moves, key=move_score)
