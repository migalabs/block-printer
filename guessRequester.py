#!/usr/bin/env python3

import argparse
import os
import blockprint.knn_classifier as knn
import blockprint.load_blocks as lb
import blockprint.prepare_training_data as pt

DEFAULT_MODEL_FOLDER = 'blockprint/model/'
DEFAULT_NODE_URL = 'http://localhost:5052'

def parse_args():
    parser = argparse.ArgumentParser(description='Request a guess for a given slot')
    parser.add_argument('model_folder', default=DEFAULT_MODEL_FOLDER, type=str, help='Path to the folder with model files')
    parser.add_argument('slot', type=int, help='Slot to request a guess for')
    parser.add_argument('--add-to-model', default=False, action='store_true',help='Add the block to the model if client could be identified with graffiti')
    parser.add_argument('--node-url', default=DEFAULT_NODE_URL, type=str, help='URL of the beacon node to download blocks from (default: http://localhost:5052)')
    return parser.parse_args()

def add_to_model_if_possible(model_folder, block_reward):
    client = pt.classify_reward_by_graffiti(block_reward[0])
    if client is not None:
        lb.store_block_rewards(block_reward[0], client, model_folder)

def getSlotGuess(slot, model_folder=DEFAULT_MODEL_FOLDER, node_url=DEFAULT_NODE_URL, add_to_model=False):
    model_folder = model_folder or DEFAULT_MODEL_FOLDER
    node_url = node_url or DEFAULT_NODE_URL

    if (not os.path.exists(model_folder)):
        print(f"Model folder {model_folder} does not exist")
        return None

    # Load the model
    classifier = knn.Classifier(model_folder)

    # Load the block
    try:
        block_reward = lb.download_block_rewards(slot, slot+1, node_url)
    except Exception as e:
        print(f'Error downloading block {slot}: {e}')
        return None

    if len(block_reward) == 0:
        print(f"Slot {slot} is empty")
        return None

    # Add the block to the model if it has a graffiti and add_to_model arg is set
    if add_to_model:
        add_to_model_if_possible(model_folder, block_reward)

    # Return the guess
    return classifier.classify(block_reward[0])

def main():
    args = parse_args()
    model_folder = args.model_folder
    slot = args.slot
    add_to_model = args.add_to_model
    node_url = args.node_url

    # Make a guess
    res = getSlotGuess(slot, model_folder, node_url, add_to_model=add_to_model)
    if res is None:
        print(f"Slot {slot} is empty or could not be downloaded")
        return None

    label, multilabel, prob_by_client, graffiti_guess = res

    # Print the guess
    print(f"Slot {slot} was mined by {label} with probability {prob_by_client[label]}")
    return label

if __name__ == "__main__":
    main()
