import random
from pathlib import Path
from schnapsen.game import SchnapsenGamePlayEngine

from schnapsen.bots.risk_control_bot import RiskControlBot
from schnapsen.bots.ml_bot import MLPlayingBot

SEED = 42
NUM_GAMES = 10000
MODEL_PATH = Path(r"C:\Users\anton\Documents\GitHub\schnapsen-coursework\ML_models\ml_vs_bully_model.joblib")

def run_tournament(n_games: int = NUM_GAMES) -> None:
    # Ensure ML model exists
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found at {MODEL_PATH}. Please train your MLPlayingBot model first."
        )

    rng = random.Random(SEED)
    engine = SchnapsenGamePlayEngine()

    # Initialize bots
    rc_bot = RiskControlBot()
    ml_bot = MLPlayingBot(model_location=MODEL_PATH)

    # Ensure get_name exists for both bots
    for bot in [rc_bot, ml_bot]:
        if not hasattr(bot, "get_name"):
            bot.get_name = lambda b=bot: getattr(b, "_name", b.__class__.__name__)

    # Track wins
    wins = {rc_bot.get_name(): 0, ml_bot.get_name(): 0}

    # Play games
    for i in range(n_games):
        # Only reset bots that actually have a reset method
        for bot in [rc_bot, ml_bot]:
            if hasattr(bot, "reset"):
                bot.reset()

        winner, *_ = engine.play_game(rc_bot, ml_bot, rng)
        wins[winner.get_name()] += 1
        print(f"Game {i+1}/{n_games} winner: {winner.get_name()}")

    # Print final results
    print("\n=== Tournament Results ===")
    for bot_name, win_count in wins.items():
        print(f"{bot_name}: {win_count}/{n_games} wins ({win_count/n_games:.2%})")

if __name__ == "__main__":
    run_tournament(NUM_GAMES)
