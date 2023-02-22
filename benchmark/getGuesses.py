#!/usr/bin/env python3

import json
import sys
import time
import requests

from dataClasses import BlockGuess


def get_validator_proposed_blocks(init_block, end_block, api_url):
    '''
    Get the best guesses by calling the Blockprint API for the blocks between init_block and end_block
    return: the response from the API
    '''

    url = f"{api_url}/{init_block}/{end_block}"
    response = json.loads(requests.get(url).text)
    return response


def getBlockprintGuesses(init_block, end_block, api_url):
    '''
    Get the best guesses from the Blockprint API
    return: a dictionary with the block slot as key and the best guess as value
    '''

    guesses = {}
    # call to the API to get the guesses
    print(f"[INFO] Getting guesses from {init_block} to {end_block}...")
    start = time.time()
    block_guesses = get_validator_proposed_blocks(init_block, end_block, api_url)
    end = time.time()
    print("[INFO] Getting guesses took %.2f seconds" % (end - start))

    if type(block_guesses) == dict:
        print(f"[ERROR] requesting guesses from {init_block} to {end_block} failed")
        sys.exit(1)

    # get the guess for each block and add it to the dictionary with the slot as key
    for block in block_guesses:
        guesses[block['slot']] = BlockGuess.from_json(block)
    return guesses
