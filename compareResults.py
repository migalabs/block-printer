#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

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
    url = f"{API_URL}/{init_block}/{end_block}"
    response = json.loads(requests.get(url).text)
    return response


def getGuessesBlockprint(init_block, end_block):
    bestGuesses = {}
    block_guesses = get_validator_proposed_blocks(init_block, end_block)

    for block in block_guesses:
        bestGuesses[block['slot']] = block['best_guess_single']

    return bestGuesses


def compareGuesses(rocketDF, bestGuesses):
    matches = [True]*len(rocketDF)

    for i in range(len(rocketDF)):
        matches[i] = rocketDF['f_client'].iloc[i] == bestGuesses[rocketDF['f_slot'].iloc[i]]
    return matches


def main():
    start = time.time()
    # add '.head(x)' to the end of the line below to test with a smaller dataset, x being the number of rows
    rocketDF = parseClients()

    init_block = rocketDF['f_slot'].iloc[0]
    end_block = rocketDF['f_slot'].iloc[-1]

    bestGuesses = getGuessesBlockprint(init_block, end_block + 1)

    rocketDF['match'] = compareGuesses(rocketDF, bestGuesses)
    rocketDF.to_csv('result.csv')

    matchingPercertage = rocketDF.match.value_counts()[True] / len(rocketDF)
    end = time.time()
    print('It took {:.2f} seconds to compare the results'.format(end - start))
    print('We have a matching percentage of {:.2f}%'.format(
        matchingPercertage * 100))


if __name__ == "__main__":
    main()
