#!/usr/bin/env python3

import time
from getGuesses import getBlockprintGuesses
from dataClasses import ProbabilityMapArray
from Plot import Plot
from Parser import Parser

clients = [
    "Lighthouse",
    "Lodestar",
    "Nimbus",
    "Prysm",
    "Teku"
]


class Comparer:
    def __init__(self, parser: Parser):
        self._parser = parser

    def analyzeResults(self, rocketDF, doPlot: bool):

        def plotResults():
            plot = Plot(rocketDF, unmatchedDF)
            plot.plot()

        # get the unmatched blocks and get the distribution of the clients
        unmatchedDF = rocketDF[rocketDF['match'] == False]

        if doPlot:
            plotResults()

        # get the matching percentage and print it
        matchingPercentage = rocketDF.match.value_counts()[
            True] / len(rocketDF) * 100
        print('\nWe have a matching percentage of {:.2f}%\n'.format(
            matchingPercentage))

    def compareGuesses(self, rocketDF, bestGuesses):
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

    def compareResults(self, arguments):
        '''
        Parse the used clients from the rocket-pool-proposals data and compare them to the
        guesses from the Blockprint API for the same blocks in order to get the accuracy of the Blockprint API
        '''

        # get the parsed clients dataframe from the csv file
        # add '.head(x)' to the end of the line below to test with a smaller dataset
        # x being the number of rows
        rocketDF = self._parser.parseClients(arguments) # .head(x)

        # get the first and last block of the dataset and  get the best guesses from the API
        init_block, end_block = rocketDF['f_slot'].iloc[0], rocketDF['f_slot'].iloc[-1]
        bestGuesses = getBlockprintGuesses(init_block, end_block + 1, arguments.api_url)

        # compare the guesses and add the result to the dataframe
        matching, wrongGuesses, probaMap = self.compareGuesses(
            rocketDF, bestGuesses)
        rocketDF['match'] = matching
        rocketDF['model_guess'] = wrongGuesses

        allProbabilities = probaMap.getLists()
        for i, client in enumerate(clients):
            rocketDF[f'proba_{client}'] = allProbabilities[i]

        if arguments.save:
            rocketDF.to_csv('result.csv')
        
        return rocketDF
