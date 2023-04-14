#!/usr/bin/env python3

import argparse
import logging
import os
import json
import time
import blockprint.knn_classifier as knn
import blockprint.load_blocks as lb
import blockprint.prepare_training_data as pt
import threading
import requests
DEFAULT_MODEL_FOLDER = 'blockprint/model/'
DEFAULT_NODE_URL = 'http://localhost:5052'


def parse_args():
    parser = argparse.ArgumentParser(
        description='Request a guess for a given slot')
    parser.add_argument('model_folder', default=DEFAULT_MODEL_FOLDER,
                        type=str, help='Path to the folder with model files')
    parser.add_argument('slot', type=int, help='Slot to request a guess for')
    parser.add_argument('--add-to-model', default=False, action='store_true',
                        help='Add the block to the model if client could be identified with graffiti')
    parser.add_argument('--node-url', default=DEFAULT_NODE_URL, type=str,
                        help='URL of the beacon node to download blocks from (default: http://localhost:5052)')
    return parser.parse_args()


def add_to_model_if_possible(model_folder, block_reward):
    client = pt.classify_reward_by_graffiti(block_reward[0])
    if client is None:
        logging.info(
            "Client couldn't be determined with graffity so can not be added to the model")
        return
    lb.store_block_rewards(block_reward[0], client, model_folder)
    logging.info(f"Added to model")


class ComputeGuessesThread(threading.Thread):
    def __init__(self, start_slot, end_slot, classifier, model_folder, node_url, add_to_model):
        super().__init__()
        self.start_slot = start_slot
        self.end_slot = end_slot
        self.classifier = classifier
        self.model_folder = model_folder
        self.node_url = node_url
        self.add_to_model = add_to_model
        self.guesses = None

    def run(self):
        self.guesses = []
        for slot in range(self.start_slot, self.end_slot + 1):
            guess = getSlotGuess(slot, self.classifier, self.model_folder,
                                 self.node_url, add_to_model=self.add_to_model)
            if guess is None:
                self.guesses = None
                return
            best_guess_single, best_guess_multi, probability_map, _ = guess
            json_str = json.dumps(guess, indent=4, sort_keys=True)
            # logging.info(f"Model guess:\n{json_str}")
            self.guesses.append({"slot": slot, "best_guess_single": best_guess_single, "best_guess_multi": best_guess_multi,
                                "probability_map": probability_map})

    def result(self):
        return self.guesses


def getSlotsGuesses(start_slot, end_slot, classifier, model_folder=DEFAULT_MODEL_FOLDER, node_url=DEFAULT_NODE_URL, add_to_model=False):
    # Define the number of threads to use
    num_threads = 16

    # Compute the number of slots per thread
    slots_per_thread = (end_slot - start_slot + 1) // num_threads

    # Create the threads and start them
    threads = []
    for i in range(num_threads):
        start = start_slot + i * slots_per_thread
        end = start + slots_per_thread - 1 if i < num_threads - 1 else end_slot
        t = ComputeGuessesThread(
            start, end, classifier, model_folder, node_url, add_to_model)
        threads.append(t)
        t.start()

    # Wait for all threads to finish and collect their results
    guesses = []
    for t in threads:
        t.join()
        result = t.result()
        if result is None:
            return None
        guesses.extend(result)

    return guesses


def getSlotGuess(slot, classifier, model_folder=DEFAULT_MODEL_FOLDER, node_url=DEFAULT_NODE_URL, add_to_model=False):

    # Load the block
    logging.info(f"Downloading block {slot}...")
    try:
        block_reward = lb.download_block_rewards(slot, slot+1, node_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            logging.error(f"Error downloading block {slot}: {e}")
            return (None, None, None, None)
        else:
            raise e  # Re-raise the exception for other status codes
    except Exception as e:
        logging.error(f"Error downloading block {slot}: {e}")
        return None
    if len(block_reward) == 0:
        logging.info(f"Slot {slot} is empty")
        return (None, None, None, None)

    # Add the block to the model if it has a graffiti and add_to_model arg is set
    if add_to_model:
        logging.info(f"Adding block {slot} to model...")
        add_to_model_if_possible(model_folder, block_reward)

    # Return the guess
    return classifier.classify(block_reward[0])


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s - %(message)s')
    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)s - %(message)s')

    args = parse_args()
    model_folder = args.model_folder or DEFAULT_MODEL_FOLDER
    slot = args.slot
    add_to_model = args.add_to_model
    node_url = args.node_url or DEFAULT_NODE_URL

    if (not os.path.exists(model_folder)):
        logging.error(f"Model folder {model_folder} does not exist")
        return None

    # Load the model
    logging.info("Loading Classifier...")
    start = time.time()
    classifier = knn.Classifier(model_folder)
    end = time.time()
    logging.info("Classifier loaded, took %.2f seconds" % (end - start))

    # Make a guess
    res = getSlotGuess(slot, classifier, model_folder,
                       node_url, add_to_model=add_to_model)
    if res is None:
        logging.error(f"Could not make a guess for slot {slot}")
        return

    label, multilabel, prob_by_client, graffiti_guess = res

    # Print the guess
    print(
        f"\nSlot {slot} was mined by {label} with probability {prob_by_client[label]}")
    return label


if __name__ == "__main__":
    main()
