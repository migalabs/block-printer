#!/usr/bin/env python3

import pandas as pd
import numpy as np
from time import sleep
import requests
import json

consensus = {
    "N": "Nimbus",
    "P": "Prysm",
    "L": "Lighthouse",
    "T": "Teku"
}


def parseGraffiti(f_graffiti):
    if type(f_graffiti) != str or len(f_graffiti) < 4:
        return ("Unknown")
    for client in consensus.values():
        if client.lower() in f_graffiti.lower():
            return client
    if f_graffiti[4] not in consensus:
        return ("Unknown")
    return consensus[f_graffiti[4]]


def parseClients():
    df = pd.read_csv("rocket-pool-proposals.csv")[['f_slot', 'f_graffiti']]
    df['f_client'] = df.apply(
        lambda row: parseGraffiti(row.f_graffiti), axis=1)
    df = df.sort_values(by=['f_slot'])

    knownDF = df[df['f_client'] != "Unknown"]
    knownDF = knownDF[['f_slot', 'f_client']]
    knownDF = knownDF.reset_index(drop=True)

    knownDF.to_csv("parsedClients.csv")
    return knownDF


def get_validator_proposed_blocks(init_block, end_block):
    url = f"https://alrevuelta:dqZ6W2WOxhNX6EjUXYovRu9HvcSceRps@api.blockprint.sigp.io/blocks/{init_block}/{end_block}"
    response = json.loads(requests.get(url).text)
    return response


def getGuessesBlockprint(rocketDF):
    bestGuesses = []

    for i in rocketDF.index:
        block = rocketDF['f_slot'][i]
        guesses = get_validator_proposed_blocks(block, block + 1)
        bestGuesses.append(guesses[0]['best_guess_single'])
    return bestGuesses


def main():
    # add '.head(x)' to the end of the line below to test with a smaller dataset, x being the number of rows
    rocketDF = parseClients()
    bestGuesses = getGuessesBlockprint(rocketDF)
    rocketDF['f_guess'] = bestGuesses
    rocketDF['match'] = np.where(
        rocketDF['f_client'] == rocketDF['f_guess'], True, False)
    rocketDF.to_csv('result.csv')

    matchingPercertage = rocketDF.match.value_counts()[True] / len(rocketDF)

    print('We have a matching percentage of {:.2f}%'.format(
        matchingPercertage * 100))


if __name__ == "__main__":
    main()
