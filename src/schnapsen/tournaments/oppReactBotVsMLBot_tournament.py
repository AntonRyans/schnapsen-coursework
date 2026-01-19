from pathlib import Path

from schnapsen.game import GamePlayEngine, SchnapsenDeckGenerator
from schnapsen.bots.opp_react_bot import HeuristicBot
from schnapsen.bots.ml_bot import MLPlayingBot


def run_tournament(
    n_games: int = 100,
):
    engine = GamePlayEngine()
    deck_generator = SchnapsenDeckGenerator()

    # Instantiate bots
    heuristic_bot = HeuristicBot(name="HeuristicBot")

    model_path = Path("ML_models/test_model")  # adjust if needed
    ml_bot = MLPlayingBot(model_location=model_path, name="MLBot")

    wins = {
        heuristic_bot.name: 0,
        ml_bot.name: 0
    }

    for i in range(n_games):
        # Alternate leader
        if i % 2 == 0:
            bot1, bot2 = heuristic_bot, ml_bot
        else:
            bot1, bot2 = ml_bot, heuristic_bot

        winner, _ = engine.play_game(
            bot1=bot1,
            bot2=bot2,
            deck_generator=deck_generator
        )

        wins[winner.name] += 1
        print(f"Game {i + 1}/{n_games} → Winner: {winner.name}")

    # Final results
    print("\n==============================")
    print("        TOURNAMENT RESULTS    ")
    print("==============================")
    for bot_name, count in wins.items():
        print(f"{bot_name}: {count} wins ({count / n_games:.2%})")


if __name__ == "__main__":
    run_tournament(n_games=10000)
