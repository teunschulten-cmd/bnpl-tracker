"""The command line that ties the modules together.

Owner: Máximo Beras-Goico.
"""

import argparse


def main() -> None:
    """Print help. Each module adds its own commands later."""
    parser = argparse.ArgumentParser(
        prog="bnpl",
        description="Track Buy Now, Pay Later purchases, instalments and debt.",
    )
    parser.parse_args()
    parser.print_help()
