#!/usr/bin/env python3

import argparse
import blockprint.knn_classifier as knn
import blockprint.load_blocks as lb
import blockprint.prepare_training_data as pt

def parse_args():
    parser = argparse.ArgumentParser(description='Request a guess for a given slot')
    parser.add_argument('model_folder', type=str, help='Folder with model files')
    parser.add_argument('slot', type=int, help='Slot to request a guess for')
    parser.add_argument('--add-to-model', default=False, action='store_true', help='Add the block to the model if client could be identified with graffiti')
    return parser.parse_args()

def add_to_model_if_possible(model_folder, block_reward):
    client = pt.classify_reward_by_graffiti(block_reward[0])
    if client is not None:
        lb.store_block_rewards(block_reward[0], client, model_folder)

def getSlotGuess(model_folder, slot, add_to_model=False):
    # Load the model
    classifier = knn.Classifier(model_folder)

    # Load the block
    try:
        block_reward = lb.download_block_rewards(slot, slot+1)
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

    # Make a guess
    res = getSlotGuess(model_folder, slot, add_to_model=add_to_model)
    if res is None:
        print(f"Slot {slot} is empty or could not be downloaded")
        return

    label, multilabel, prob_by_client, graffiti_guess = res

    # Print the guess
    print(f"Slot {slot} was mined by {label} with probability {prob_by_client[label]}")
    return label

if __name__ == "__main__":
    main()
