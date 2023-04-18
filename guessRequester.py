#!/usr/bin/env python3

import argparse
import logging
import os
import time
import blockprint.knn_classifier as knn
import blockprint.load_blocks as lb
import blockprint.prepare_training_data as pt
import requests
DEFAULT_MODEL_FOLDER = 'blockprint/model/'
DEFAULT_NODE_URL = 'http://localhost:5052'
MAX_SLOTS = 10000


def parse_args():
    parser = argparse.ArgumentParser(
        description='Request a guess for a given slot')
    parser.add_argument('model_folder', default=DEFAULT_MODEL_FOLDER,
                        type=str, help='Path to the folder with model files')
    parser.add_argument('start_slot', type=int,
                        help='Start Slot to request a guess for')
    parser.add_argument(
        'end_slot', type=int, nargs='?', help='End Slot to request a guess for. If not provided, only the start slot will be requested')
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


def getSlotGuesses(start_slot, end_slot, classifier, model_folder=DEFAULT_MODEL_FOLDER, node_url=DEFAULT_NODE_URL, add_to_model=False):
    if end_slot - start_slot > MAX_SLOTS:
        end_slot = start_slot + MAX_SLOTS
    guesses = []
    # Load the blocks
    logging.info(f"Downloading blocks {start_slot} to {end_slot}...")
    start_time = time.time()
    try:
        block_rewards = lb.download_block_rewards(
            start_slot, end_slot, node_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            message = e.response.json()['message']
            logging.error(
                f"Error downloading blocks: {e}: {message}")
            return None
        else:
            raise e  # Re-raise the exception for other status codes
    except Exception as e:
        logging.error(f"Error downloading blocks: {e}")
        return None
    end_time = time.time()
    logging.info(
        f"Downloaded {len(block_rewards)} blocks in {end_time - start_time} seconds")
    block_rewards_index = 0
    for i in range(end_slot-start_slot+1):
        best_guess_multi = ""
        best_guess_single = ""
        probability_map = {}
        proposer_index = None
        slot_num = start_slot + i
        if len(block_rewards) > 0:
            slot = block_rewards[block_rewards_index]
            if i == int(slot["meta"]["slot"]) - start_slot:
                block_rewards_index += 1
                if add_to_model:
                    logging.info(f"Adding block {slot_num} to model...")
                    add_to_model_if_possible(model_folder, slot_num)
                guess = classifier.classify(slot)
                if guess is None:
                    guesses = None
                    return
                best_guess_single, best_guess_multi, probability_map, _ = guess
                proposer_index = slot["meta"]["proposer_index"]

        guesses.append({"slot": slot_num, "best_guess_single": best_guess_single, "best_guess_multi": best_guess_multi,
                        "probability_map": probability_map, "proposer_index": proposer_index})
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
    start_slot = args.start_slot
    end_slot = args.end_slot or args.start_slot

    if end_slot < start_slot:
        logging.error("End slot must be greater than start slot")
        return None
    model_folder = args.model_folder or DEFAULT_MODEL_FOLDER
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

    # Make guesses for all slots
    guesses = getSlotGuesses(start_slot, end_slot, classifier, model_folder,
                             node_url, add_to_model=add_to_model)

    if guesses is None:
        logging.error("Error making guesses")
        return None

    # Print the guesses
    for guess in guesses:
        if guess is None:
            continue
        slot = guess["slot"]
        best_guess_single = guess["best_guess_single"]
        best_guess_multi = guess["best_guess_multi"]
        probability_map = guess["probability_map"]
        proposer_index = guess["proposer_index"]
        logging.info(f"Slot {slot}:")
        logging.info(f"Best guess (single): {best_guess_single}")
        logging.info(f"Best guess (multi): {best_guess_multi}")
        logging.info(f"Probability map: {probability_map}")
        logging.info(f"Proposer index: {proposer_index}")
    return guesses


if __name__ == "__main__":
    main()
