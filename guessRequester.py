#!/usr/bin/env python3

import argparse
import blockprint.knn_classifier as knn
import blockprint.load_blocks as lb

def parse_args():
    parser = argparse.ArgumentParser(description='Request a guess for a given slot')
    parser.add_argument('model_folder', type=str, help='Folder with model files')
    parser.add_argument('slot', type=int, help='Slot to request a guess for')
    return parser.parse_args()

def getSlotGuess(model_folder, slot):
    # Load the model
    classifier = knn.Classifier(model_folder)

    # Load the block
    block_reward = lb.download_block_rewards(slot, slot+1)
    if len(block_reward) == 0:
        print(f"Slot {slot} is empty")
        return None

    # Return the guess
    return classifier.classify(block_reward[0])

def main():
    args = parse_args()
    model_folder = args.model_folder
    slot = args.slot

    # Make a guess
    label, multilabel, prob_by_client, graffiti_guess = getSlotGuess(model_folder, slot)

    # Print the guess
    print(f"Slot {slot} was mined by {label} with probability {prob_by_client[label]}")
    return label

if __name__ == "__main__":
    main()
