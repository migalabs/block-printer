#!/usr/bin/env python3

import argparse
import os


class Parser:
    def __init__(self):
        self._parser = None
        self.init_parser()

    def init_parser(self):
        self._parser = argparse.ArgumentParser(
            description="Benchmark the block's client proposer guesser accuracy")
        self._parser.add_argument("dataset", default="rocket-pool-proposals.csv", type=str,
                                  help="Path to the dataset csv file, needs to contain at least \
                                    this two columns: 'f_slot','f_graffiti'")
        self._parser.add_argument("--timer", default=False, action="store_true",
                                  help="Print the time it took to run the script")
        self._parser.add_argument(
            "--plot", default=False, action="store_true", help="Plot the results")

    def parse_args(self):
        return self._parser.parse_args()
