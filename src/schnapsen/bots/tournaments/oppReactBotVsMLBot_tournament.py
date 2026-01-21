import sys
from pathlib import Path
import time

# -------------------------------------------------
# Fix imports when running directly
# Adds `src/` to PYTHONPATH
# -------------------------------------------------
SRC_PATH = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC_PATH))

# -------------------------------------------------
# Imports
# -------------------------------------------------
from schnapsen.game import SchnapsenGamePlayEngine, SchnapsenDeckGenerator
from schnapsen.bots.opp_react_bot import OppReactBot
from schnapsen.bots.ml_bot import MLPlayingBot

# -------------------------------------------------
# Tournament function
# -------------------------------------------------
def run_tournament(
    n_games: int = 100,
    bot1_class=None,
    bot2_class=None,
    bot1_name: str = "Bot1",
    bot2_name: str = "Bot2",
    ml_model_path: Path | None = None
):
    """
    Run a tournament between two Schnapsen bots.
    """

    # Correct engine for schnapsen 0.0.5
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
        # Alternate starting player
        if i % 2 == 0:
            p1, p2 = bot1, bot2
        else:
            p1, p2 = bot2, bot1

        winner, _ = engine.play_game(
            bot1=p1,
            bot2=p2,
            deck_generator=deck_generator
        )

        wins[winner.name] += 1

        # Progress update every 10%
        if (i + 1) % max(1, n_games // 10) == 0:
            print(f"Completed {i + 1}/{n_games} games")

    # -------------------------------------------------
    # Results
    # -------------------------------------------------
    print("\n==============================")
    print("        TOURNAMENT RESULTS    ")
    print("==============================")

    for bot_name, count in wins.items():
        print(f"{bot_name}: {count} wins ({count / n_games:.2%})")

    print(f"\nTotal runtime: {(time.time() - start_time) / 60:.2f} minutes")


# -------------------------------------------------
# Main
# -------------------------------------------------
if __name__ == "__main__":

    # ML model is located in: schnapsen/bots/ML_models/test_model
    model_path = (
        Path(__file__).resolve().parents[1]
        / "ML_models"
        / "test_model"
    )

    # Optional sanity check (you can remove later)
    assert model_path.exists(), f"Model not found at: {model_path}"

    run_tournament(
        n_games=10,
        bot1_class=OppReactBot,
        bot2_class=MLPlayingBot,
        bot1_name="OppReactBot",
        bot2_name="MLBot",
        ml_model_path=model_path
    )
