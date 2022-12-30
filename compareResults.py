#!/usr/bin/env python3

import os
from sys import argv as av
import pandas as pd
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


def parseClients(fileName):
    '''
    Parse the clients from the rocket-pool-proposals.csv data
    return: a dataframe with the slot and the client that are not Unknown
    '''

    # read the csv file and parse the clients thanks to the graffiti
    df = pd.read_csv(fileName)[['f_slot', 'f_graffiti']]
    df['f_client'] = df.apply(
        lambda row: parseGraffiti(row.f_graffiti), axis=1)
    df = df.sort_values(by=['f_slot'])

    # remove the Unknown clients and reset the index in order to have a continuous index
    knownDF = df[df['f_client'] != "Unknown"]
    knownDF = knownDF[['f_slot', 'f_client']]
    knownDF = knownDF.reset_index(drop=True)

    # uncomment the line below to save the parsed clients to a csv file
    # knownDF.to_csv("parsedClients.csv")
    return knownDF


def get_validator_proposed_blocks(init_block, end_block):
    '''
    Get the best guesses by calling the Blockprint API for the blocks between init_block and end_block
    return: the response from the API
    '''

    url = f"{API_URL}/{init_block}/{end_block}"
    response = json.loads(requests.get(url).text)
    return response


def getBlockprintGuesses(init_block, end_block):
    '''
    Get the best guesses from the Blockprint API
    return: a dictionary with the block slot as key and the best guess as value
    '''

    bestGuesses = {}
    # call to the API to get the guesses
    block_guesses = get_validator_proposed_blocks(init_block, end_block)

    # get the best guess for each block and add it to the dictionary with the slot as key
    for block in block_guesses:
        bestGuesses[block['slot']] = block['best_guess_single']
    return bestGuesses


def compareGuesses(rocketDF, bestGuesses):
    '''
    Compare the guesses from the Blockprint API to the parsed clients from the rocket-pool-proposals data
    return: a list of booleans, True if the guess is matching, False otherwise
    '''

    # initialize the list of booleans to gain time
    matches = [True] * len(rocketDF)

    # compare the guesses for the blocks we have known clients for
    # and add the result to the list in order to add it to the dataframe
    for i in range(len(rocketDF)):
        matches[i] = rocketDF['f_client'].iloc[i] == bestGuesses[rocketDF['f_slot'].iloc[i]]
    return matches


def compareResults(fileName):
    '''
    Parse the used clients from the rocket-pool-proposals data and compare them to the
    guesses from the Blockprint API for the same blocks in order to get the accuracy of the Blockprint API
    '''

    # start timer
    start = time.time()

    # get the parsed clients dataframe from the csv file
    # add '.head(x)' to the end of the line below to test with a smaller dataset
    # x being the number of rows
    rocketDF = parseClients(fileName)

    # get the first and last block of the dataset and  get the best guesses from the API
    init_block = rocketDF['f_slot'].iloc[0]
    end_block = rocketDF['f_slot'].iloc[-1]
    bestGuesses = getBlockprintGuesses(init_block, end_block + 1)

    # compare the guesses and add the result to the dataframe
    rocketDF['match'] = compareGuesses(rocketDF, bestGuesses)

    # uncomment the line below to save the results to a csv file
    # rocketDF.to_csv('result.csv')

    # get the matching percentage and print it
    matchingPercentage = rocketDF.match.value_counts()[True] / len(rocketDF) * 100
    print('We have a matching percentage of {:.2f}%'.format(
        matchingPercentage))

    # end timer and print the time it took to compare the results
    end = time.time()
    print('It took {:.2f} seconds to compare the results'.format(end - start))


def main():
    fileName = 'rocket-pool-proposals.csv' if len(av) < 2 else av[1]
    compareResults(fileName)


if __name__ == "__main__":
    main()
