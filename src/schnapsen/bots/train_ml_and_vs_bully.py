"""
End-to-end script to:
1) Generate replay memory by letting an RdeepBot play games (recorded via MLDataBot)
2) Train an ML model from that replay memory
3) Play the trained MLPlayingBot against BullyBot

Assumptions:
- Your previously defined classes/functions are importable:
  MLDataBot, MLPlayingBot, train_ML_model
  RdeepBot, BullyBot
- schnapsen is installed and GamePlayEngine is available
"""

import random
import pathlib
from schnapsen.game import SchnapsenGamePlayEngine

# ---- IMPORT YOUR BOTS / FUNCTIONS ----
# Adjust these imports to match your project structure
from schnapsen.bots.rdeep import RdeepBot
from schnapsen.bots.bully_bot import BullyBot
from schnapsen.bots.ml_bot import MLDataBot, MLPlayingBot, train_ML_model



# ---------------- CONFIG ----------------
SEED = 42
NUM_TRAIN_GAMES = 5000        # increase (e.g. 5k–20k) for stronger ML bot
RDEEP_SAMPLES = 8            # rollouts per move
RDEEP_DEPTH = 8              # rollout depth
MODEL_CLASS = "LR"           # "LR" or "NN"

REPLAY_MEMORY_PATH = pathlib.Path("ML_replay_memories") / "rdeep_replay_memory.txt"
MODEL_PATH = pathlib.Path("ML_models") / "ml_vs_bully_model.joblib"

NUM_EVAL_GAMES = 5000
# --------------------------------------


def generate_replay_memory() -> None:
    print("=== Generating replay memory with RdeepBot ===")

    rng = random.Random(SEED)
    engine = SchnapsenGamePlayEngine()

    # Base bots
    rdeep = RdeepBot(num_samples=RDEEP_SAMPLES, depth=RDEEP_DEPTH, rand=rng, name="Rdeep")
    bully = BullyBot(rand=rng, name="Bully")

    # Wrap Rdeep with MLDataBot to record decisions
    data_bot = MLDataBot(bot=rdeep, replay_memory_location=REPLAY_MEMORY_PATH)

    # Ensure clean replay memory file
    REPLAY_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if REPLAY_MEMORY_PATH.exists():
        REPLAY_MEMORY_PATH.unlink()

    for i in range(NUM_TRAIN_GAMES):
        engine.play_game(data_bot, bully, rng)
        if (i + 1) % 50 == 0:
            print(f"  Played {i + 1}/{NUM_TRAIN_GAMES} games")

    print("Replay memory generation complete.\n")


def train_model() -> None:
    print("=== Training ML model ===")

    if MODEL_PATH.exists():
        MODEL_PATH.unlink()

    train_ML_model(
        replay_memory_location=REPLAY_MEMORY_PATH,
        model_location=MODEL_PATH,
        model_class=MODEL_CLASS
    )

    print("Model training complete.\n")


def evaluate_against_bully() -> None:
    print("=== Evaluating MLPlayingBot vs BullyBot ===")

    rng = random.Random(SEED + 1)
    engine = SchnapsenGamePlayEngine()

    ml_bot = MLPlayingBot(model_location=MODEL_PATH, name="MLBot")
    bully = BullyBot(rand=rng, name="Bully")

    ml_wins = 0

    for i in range(NUM_EVAL_GAMES):
        winner = engine.play_game(ml_bot, bully, rng)
        if winner is ml_bot:
            ml_wins += 1

    win_rate = ml_wins / NUM_EVAL_GAMES
    print(f"MLBot wins: {ml_wins}/{NUM_EVAL_GAMES}")
    print(f"Win rate: {win_rate:.2%}")


if __name__ == "__main__":
    generate_replay_memory()
    train_model()
    evaluate_against_bully()
