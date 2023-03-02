#!/usr/bin/env python3

import argparse
import pandas as pd

consensus = {
    "N": "Nimbus",
    "P": "Prysm",
    "L": "Lighthouse",
    "T": "Teku"
}


class Parser:
    def __init__(self):
        self._parser = None
        self.init_parser()

    def init_parser(self):
        self._parser = argparse.ArgumentParser(
            description="Benchmark the block's client proposer guesser accuracy")
        self._parser.add_argument("--dataset", default="rocket-pool-proposals.csv", type=str,
                                  help="Path to the dataset csv file, needs to contain at least \
                                    this two columns: 'f_slot','f_graffiti'")
        self._parser.add_argument("--timer", default=False, action="store_true",
                                  help="Print the time it took to run the script")
        self._parser.add_argument("--save", default=False, action="store_true",
                                  help="Save the parsed clients to a csv file")
        self._parser.add_argument(
            "--plot", default=False, action="store_true", help="Plot the results")

    def parse_args(self):
        return self._parser.parse_args()

    def parseGraffiti(self, f_graffiti):
        '''
        Parse the graffiti from the rocket-pool-proposals data
        return: the client name if it can be identify , Unknown otherwise
        '''

        # client can be identified either if the client name is in the graffiti or with the 4th character
        if type(f_graffiti) != str or len(f_graffiti) < 4:
            return ("Unknown")
        for client in consensus.values():
            if client.lower() in f_graffiti.lower():
                return client
        if f_graffiti[4] not in consensus:
            return ("Unknown")
        return consensus.get(f_graffiti[4])

    def parseClients(self, arguments):
        '''
        Parse the clients from the rocket-pool-proposals.csv data
        return: a dataframe with the slot and the client that are not Unknown
        '''

        # read the csv file and parse the clients thanks to the graffiti
        df = pd.read_csv(arguments.dataset)[['f_slot', 'f_graffiti']]
        df['f_client'] = df.apply(
            lambda row: self.parseGraffiti(row.f_graffiti), axis=1)
        df = df.sort_values(by=['f_slot'])

        # remove the Unknown clients and reset the index in order to have a continuous index
        knownDF = df[df['f_client'] != "Unknown"]
        knownDF = knownDF[['f_slot', 'f_client']]
        knownDF = knownDF.reset_index(drop=True)

        if (arguments.save):
            knownDF.to_csv("parsedClients.csv")
        return knownDF
