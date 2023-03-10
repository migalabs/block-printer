#!/usr/bin/env python3

import json
import os
import time
import logging
from flask import Flask, request, jsonify
from guessRequester import getSlotGuess
import blockprint.knn_classifier as knn

import argparse

app = Flask(__name__)

node_url = 'http://localhost:5052'
model_folder = 'model/'
add_to_model = None
classifier = None


@app.route('/', methods=['GET'])
def notFound():
    return jsonify({"status": 404})


@app.route('/getClientGuess', methods=['GET'])
def getClientGuess():
    args = (request.args).to_dict()

    slot = args.get('slot')

    if slot is None:
        return jsonify({'error': 'Invalid request, please provide slot'}), 500

    try:
        slot = int(slot)
    except ValueError:
        return jsonify({'error': 'Invalid request, slot must be an integer'}), 500

    res = getSlotGuess(slot, classifier, model_folder,
                       node_url, add_to_model=add_to_model)
    if res is None:
        return jsonify({'error': 'Model folder doesn\'t exists or Slot is empty or could not be downloaded'}), 500

    # print the guess probabilities with json format
    json_str = json.dumps(res, indent=4, sort_keys=True)
    logging.info(f"Model guess:\n{json_str}")
    return jsonify(res), 200


def parse_args():
    parser = argparse.ArgumentParser(
        description='Request a guess for a given slot')
    parser.add_argument('model_folder', default=model_folder,
                        type=str, help='Path to the folder with model files')
    parser.add_argument('--add-to-model', default=add_to_model, action='store_true',
                        help='Add the block to the model if client could be identified with graffiti')
    parser.add_argument('--node-url', default=node_url, type=str,
                        help='URL of the beacon node to download blocks from (default: http://localhost:5052)')
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s - %(message)s')
    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)s - %(message)s')

    args = parse_args()
    model_folder = args.model_folder
    add_to_model = args.add_to_model is not None
    node_url = args.node_url

    if (not os.path.exists(model_folder)):
        logging.error(f"Model folder {model_folder} does not exist")
        exit(1)

    # Load the model
    logging.info(f"Loading model from {model_folder}...")
    start = time.time()
    classifier = knn.Classifier(model_folder)
    end = time.time()
    logging.info(f"Classifier loaded, took {end - start} seconds")

    logging.info("Starting server")
    app.run()
