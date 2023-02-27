#!/usr/bin/env python3

import os
import time
import logging
from dotenv import load_dotenv

from Compare import Comparer
from Parser import Parser

load_dotenv()

API_URL = os.getenv("API_URL")


def main():
    '''
    Main function
    The csv file must contain at least the following columns:
    "f_slot","f_graffiti"
    '''

    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s - %(message)s')
    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)s - %(message)s')

    parser = Parser()
    arguments = parser.parse_args()
    arguments.api_url = API_URL

    if arguments.timer:
        # start timer
        start = time.time()

    comparer = Comparer(parser)
    finalDF = comparer.compareResults(arguments)

    if arguments.timer:
        # end timer
        end = time.time()
        logging.info("Comparing guesses took %.2f seconds" % (end - start))

    # analyze the results and plot them if needed
    comparer.analyzeResults(finalDF, arguments.plot)


if __name__ == "__main__":
    main()
