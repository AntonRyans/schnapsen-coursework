import sys
from pathlib import Path
import time
import random

# Fix imports when running directly
ROOT = Path(__file__).resolve().parents[4]  
sys.path.insert(0, str(ROOT / "src"))

# Imports
from schnapsen.game import SchnapsenGamePlayEngine
from schnapsen.bots.opp_react_bot import OppReactBot
from schnapsen.bots.ml_bot import MLPlayingBot

# Tournament function
def run_tournament(
    n_games: int,
    bot1_class,
    bot2_class,
    bot1_name: str,
    bot2_name: str,
    ml_model_path: Path
):
    engine = SchnapsenGamePlayEngine()
    rng = random.Random(42)

    bot1 = bot1_class(name=bot1_name)
    bot2 = bot2_class(
        model_location=ml_model_path,
        name=bot2_name
    )

    wins = {
        bot1_name: 0,
        bot2_name: 0
    }

    start_time = time.time()

    for i in range(n_games):
        # Alternate first player
        p1, p2 = (bot1, bot2) if i % 2 == 0 else (bot2, bot1)

        # Play the game; unpack winner tuple (winner, points, score)
        winner, *_ = engine.play_game(p1, p2, rng)

        # Map winner object to correct dictionary key
        if winner is bot1:
            wins[bot1_name] += 1
        else:
            wins[bot2_name] += 1

        if (i + 1) % max(1, n_games // 10) == 0:
            print(f"Completed {i + 1}/{n_games} games")

    # Results
    print("\n==============================")
    print("        TOURNAMENT RESULTS    ")
    print("==============================")

    for name, count in wins.items():
        print(f"{name}: {count} wins ({count / n_games:.2%})")

    print(f"\nTotal runtime: {(time.time() - start_time) / 60:.2f} minutes")

# Main
if __name__ == "__main__":

    model_path = ROOT / "ML_models" / "ml_vs_bully_model.joblib"

    print("Loading ML model from:")
    print(model_path)

    assert model_path.exists(), f"Model not found at: {model_path}"

    run_tournament(
        n_games=10000,
        bot1_class=OppReactBot,
        bot2_class=MLPlayingBot,
        bot1_name="OppReactBot",
        bot2_name="MLBot",
        ml_model_path=model_path
    )
