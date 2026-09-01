"""weduofficial"""
"""Coi Flip: the only tool that i personally used for sake of deciding if i should kiss my homie or not... jk"""

import argparse
import random


def flip_coin() -> str:
    return random.choice(["Heads", "Tails"])


def main():
    parser = argparse.ArgumentParser(description="Flip a coin.")
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Number of times to flip (default: 1)",
    )
    args = parser.parse_args()

    if args.count <= 0:
        parser.error("Number of flips must be positive.")

    results = [flip_coin() for _ in range(args.count)]

    if args.count == 1:
        print(f"🪙 {results[0]}")
    else:
        for i, result in enumerate(results, 1):
            print(f"{i:>3}: 🪙 {result}")

        heads = results.count("Heads")
        tails = results.count("Tails")

        print()
        print(f"Heads: {heads}")
        print(f"Tails: {tails}")


if __name__ == "__main__":
    main()
  
