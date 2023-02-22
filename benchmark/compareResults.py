#!/usr/bin/env python3

import os
from sys import argv as av
from dataclasses import dataclass, field
import pandas as pd
import time
import requests
import json
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from Parser import Parser

load_dotenv()

API_URL = os.getenv("API_URL")

consensus = {
    "N": "Nimbus",
    "P": "Prysm",
    "L": "Lighthouse",
    "T": "Teku"
}

clients = [
    "Lighthouse",
    "Lodestar",
    "Nimbus",
    "Prysm",
    "Teku"
]


@dataclass
class BlockGuess:
    slot: int
    proposer_index: int
    best_guess_single: str
    best_guess_multi: str
    probability_map: dict

    @classmethod
    def from_json(cls, json):
        return cls(**json)

@dataclass
class ProbabilityMapArray:
    Lighthouse: list = field(default_factory=list)
    Lodestar: list = field(default_factory=list)
    Nimbus: list = field(default_factory=list)
    Prysm: list = field(default_factory=list)
    Teku: list = field(default_factory=list)

    def add_elem(self, Lighthouse, Lodestar, Nimbus, Prysm, Teku):
        self.Lighthouse.append(Lighthouse)
        self.Lodestar.append(Lodestar)
        self.Nimbus.append(Nimbus)
        self.Prysm.append(Prysm)
        self.Teku.append(Teku)
    
    def getLists(self):
        return [self.Lighthouse, self.Lodestar, self.Nimbus, self.Prysm, self.Teku]


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

    guesses = {}
    # call to the API to get the guesses
    block_guesses = get_validator_proposed_blocks(init_block, end_block)

    # get the guess for each block and add it to the dictionary with the slot as key
    for block in block_guesses:
        guesses[block['slot']] = BlockGuess.from_json(block)
    return guesses


def compareGuesses(rocketDF, bestGuesses):
    '''
    Compare the guesses from the Blockprint API to the parsed clients from the rocket-pool-proposals data
    return: a list of booleans, True if the guess is matching, False otherwise
    '''

    # initialize the lists to gain time
    matches = [True] * len(rocketDF)
    wrongGuesses = [None] * len(rocketDF)
    proba_map_array = ProbabilityMapArray()

    # compare the guesses for the blocks we have known clients for
    # and add the result to the list in order to add it to the dataframe
    for i in range(len(rocketDF)):
        block_guess = bestGuesses[rocketDF['f_slot'].iloc[i]]
        matches[i] = rocketDF['f_client'].iloc[i] in block_guess.best_guess_single

        proba_map = block_guess.probability_map
        proba_map_array.add_elem(*proba_map.values())

        if not matches[i]:
            wrongGuesses[i] = block_guess.best_guess_single

    return matches, wrongGuesses, proba_map_array


def analyzeResults(rocketDF):
    def drawValues():
        y_offset = -5
        for bar in plt.gca().patches:
            ax = plt.gca()
            if (bar.get_height() < 5):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + bar.get_y() + y_offset,
                '{:.2f}%'.format(bar.get_height()),
                ha='center',
                color='black',
                weight='bold',
                fontsize=8
            )
    
    def setTitleAndLabels(title, xlabel, ylabel):
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    
    def plotBarChart(df, title, xlabel, ylabel):
        columns = ['f_client', 'proba_Lighthouse', 'proba_Nimbus', 'proba_Prysm', 'proba_Teku']

        # get the distribution of the clients guesses thanks to the mean values
        distribution = df[columns].groupby('f_client').mean()
        
        # change from decimal to percentage
        percentDistribution = distribution.div(distribution.sum(axis=1), axis=0) * 100

        # plot the bar chart
        percentDistribution.plot(kind='bar', stacked=True, title=title)
        
        # change the titles and labels
        setTitleAndLabels(title, xlabel, ylabel)

        # draw the values on the bars
        drawValues()

    def getVisualRepresentation():
        # plot the distribution of the clients for all the blocks
        plotBarChart(rocketDF, 'Distribution of the clients guesses for all the blocks', 'Clients', 'Percentage (%)')
        
        # plot the distribution of the clients for the unmatched blocks
        plotBarChart(unmatchedDF, 'Distribution of the clients guesses for the unmatched blocks', 'Clients', 'Percentage (%)')
        plt.show()
    
    def getMatchingPercentageForEach():
        col = ['f_client','match']
        a = rocketDF[col]
        a = a.groupby('f_client').mean().round(4) * 100
        print(a)

    # get the unmatched blocks and get the distribution of the clients
    unmatchedDF = rocketDF[rocketDF['match'] == False]


    # uncomment the line below to display the guesses distribution charts
    # getVisualRepresentation()

    # uncomment the line below to display the matching percentage for each client
    # getMatchingPercentageForEach()

    # get the matching percentage and print it
    matchingPercentage = rocketDF.match.value_counts()[True] / len(rocketDF) * 100
    print('We have a matching percentage of {:.2f}%'.format(matchingPercentage))


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
    matching, wrongGuesses, probaMap = compareGuesses(rocketDF, bestGuesses)
    rocketDF['match'] = matching
    rocketDF['model_guess'] = wrongGuesses
    
    allProbabilities = probaMap.getLists()
    for i, client in enumerate(clients):
        rocketDF[f'proba_{client}'] = allProbabilities[i]

    # uncomment the line below to save the results to a csv file
    rocketDF.to_csv('result.csv')

    # analyze the results
    analyzeResults(rocketDF)

    # end timer and print the time it took to compare the results
    end = time.time()
    print('It took {:.2f} seconds to compare the results'.format(end - start))


def main():
    '''
    Main function
    The csv file must contain at least the following columns:
    "f_slot","f_graffiti"
    '''
    parser = Parser()
    arguments = parser.parse_args()
    print(arguments)
    exit()

    fileName = 'rocket-pool-proposals.csv' if len(av) < 2 else av[1]
    compareResults(fileName)
    # df = pd.read_csv('result.csv')
    # analyzeResults(df)


if __name__ == "__main__":
    main()
