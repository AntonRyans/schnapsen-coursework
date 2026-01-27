import sys
from pathlib import Path
import time
import random
from schnapsen.game import SchnapsenGamePlayEngine, SchnapsenDeckGenerator
from schnapsen.bots.score_based_bot import ScoreBasedBot
from schnapsen.bots.ml_bot import MLPlayingBot

# Fix imports when running directly
SRC_PATH = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC_PATH))

# Tournament function
def run_tournament(
    n_games: int = 100000,
    bot1_class=None,
    bot2_class=None,
    bot1_name: str = "Bot1",
    bot2_name: str = "Bot2",
    ml_model_path: Path | None = None
):
    engine = SchnapsenGamePlayEngine()
    rng = random.Random(42)

    """
    Run a tournament between two Schnapsen bots.
    """

    engine = SchnapsenGamePlayEngine()
    deck_generator = SchnapsenDeckGenerator()

    # Instantiate bots
    bot1 = bot1_class(name=bot1_name)

    if ml_model_path is not None and issubclass(bot2_class, MLPlayingBot):
        bot2 = bot2_class(
            model_location=ml_model_path,
            name=bot2_name
        )
    else:
        bot2 = bot2_class(name=bot2_name)

    wins = {
        bot1.name: 0,
        bot2.name: 0
    }

    start_time = time.time()

    for i in range(n_games):
        if i % 2 == 0:
            p1, p2 = bot1, bot2
        else:
            p1, p2 = bot2, bot1

        # Pass the rng as a positional argument 
        winner, _, _ = engine.play_game(
            p1, 
            p2, 
            rng
        )

        wins[winner.name] += 1

        # Progress update every 10%
        if (i + 1) % max(1, n_games // 10) == 0:
            print(f"Completed {i + 1}/{n_games} games")

    # Results
    print("\n==============================")
    print("        TOURNAMENT RESULTS    ")
    print("==============================")

    for bot_name, count in wins.items():
        print(f"{bot_name}: {count} wins ({count / n_games:.2%})")

    print(f"\nTotal runtime: {(time.time() - start_time) / 60:.2f} minutes")

# Main
if __name__ == "__main__":
    # This finds the root "schnapsen-coursework" directory
    root_path = Path(__file__).resolve().parents[4] 
    
    # This points to where the training script saves the model
    model_path = root_path / "ML_models" / "ml_vs_bully_model.joblib"

    # DEBUG: Run this once to see exactly where the script is looking
    print(f"Looking for model at: {model_path}")

    assert model_path.exists(), f"Model not found! Please ensure you ran the training script first and that the file exists at: {model_path}"

    run_tournament(
        n_games=100000,
        bot1_class=ScoreBasedBot,
        bot2_class=MLPlayingBot,
        bot1_name="ScoreBasedBot",
        bot2_name="MLBot",
        ml_model_path=model_path
    )