import argparse
import logging
import os
import pickle
import time
import blockprint.knn_classifier as knn
import requests
from guess_requester import getSlotGuesses, EndSlotUnkown
from postgres import Postgres, parse_db_endpoint_string

DEFAULT_MODEL_FOLDER = "model"
DEFAULT_NODE_URL = "http://localhost:5052"
DEFAULT_BACKFILLING_BATCH_SIZE = 10000

def parse_args():
    parser = argparse.ArgumentParser(description="Request a guess for a given slot")
    parser.add_argument(
        "--model-folder",
        default=DEFAULT_MODEL_FOLDER,
        type=str,
        help="Path to the folder with model files. It will be used to train the classifier if there isn't one persisted already. Default: model",
    )
    parser.add_argument(
        "--persist-classifier",
        type=str,
        help=f"Persist the classifier to disk after training. It will be stored in the persisted_classifier folder with the name given as parameter. This name will also be used to load the classifier if it exists. The name should end with .pkl. Example: --persist-classifier my_classifier.pkl",
    )
    parser.add_argument(
        "postgres_endpoint",
        type=str,
        help="Postgres endpoint. Example: postgresql://user:password@host:port/dbname",
    )
    parser.add_argument(
        "--add-to-model",
        default=False,
        action="store_true",
        help="Add the block to the model if client could be identified with graffiti",
    )
    parser.add_argument(
        "--node-url",
        default=DEFAULT_NODE_URL,
        type=str,
        help="URL of the beacon node to download blocks from (default: http://localhost:5052)",
    )

    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Reindex the database. WARNING: This will delete all data in the database and reindex all slots from the beacon node. Useful if the model was updated",
    )

    return parser.parse_args()


def get_node_head_slot(node_url):
    response = requests.get(node_url + "/eth/v2/beacon/blocks/head")
    head_slot_json = response.json()
    return int(head_slot_json["data"]["message"]["slot"])


def loadSlotGuessesDatabase(
    start_slot, end_slot, classifier, model_folder, node_url, add_to_model, db
):
    guesses = getSlotGuesses(
        start_slot,
        end_slot,
        classifier,
        model_folder,
        node_url,
        add_to_model,
        db_format=True,
    )

    if guesses is not None:
        start = time.time()
        db.insert_rows(
            TABLE_NAME,
            (
                "f_slot",
                "f_best_guess_single",
                "f_best_guess_multi",
                "f_probability_map",
                "f_proposer_index",
            ),
            guesses,
        )
        end = time.time()
        logging.info("Inserted {} rows in {} seconds".format(len(guesses), end - start))


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s - %(message)s")

    args = parse_args()
    model_folder = args.model_folder or DEFAULT_MODEL_FOLDER
    add_to_model = args.add_to_model
    node_url = args.node_url or DEFAULT_NODE_URL
    reindex = args.reindex or False
    persisted_classifier_path = None
    if args.persist_classifier:
        if not args.persist_classifier.endswith(".pkl"):
            logging.error(
                f"Persisted classifier name should end with .pkl, got {args.persist_classifier}"
            )
            exit(1)
        persisted_classifier_path = f"persisted_classifier/{args.persist_classifier}"
        if not os.path.exists("persisted_classifier"):
            os.makedirs("persisted_classifier")

    print("Reindex: {}".format(reindex))

    # Load the model
    start = time.time()
    if args.persist_classifier and os.path.exists(persisted_classifier_path):
        logging.info(
            f"Loading persisted classifier from {persisted_classifier_path}..."
        )
        classifier = pickle.load(open(persisted_classifier_path, "rb"))
    else:
        if not os.path.exists(model_folder):
            logging.error(
                f"Model folder {model_folder} does not exist. Read the README.md for instructions on how to train the model"
            )
            exit(1)
        logging.info(f"Loading model from {model_folder}...")
        classifier = knn.Classifier(model_folder)

    if persisted_classifier_path:
        knn.persist_classifier(
            classifier,
            persisted_classifier_path.split(".pkl")[0],
        )
        logging.info(f"Persisting classifier to {persisted_classifier_path}...")

    end = time.time()
    logging.info(f"Classifier loaded, took {end - start} seconds")

    logging.info("Connecting to database...")
    db = Postgres(url=args.postgres_endpoint)
    logging.info("Connected to database")
    db.create_table(
        TABLE_NAME,
        "f_slot integer, f_best_guess_single text, f_best_guess_multi text, f_probability_map text[], f_proposer_index integer",
        "f_slot",
        replace=reindex,
    )
    last_slot_saved = db.dict_query(f"SELECT MAX(f_slot) FROM {TABLE_NAME}")[0]["max"]
    if last_slot_saved is None:
        last_slot_saved = 0
    logging.info(f"Last slot saved: {last_slot_saved}")

    while True:
        start = time.time()
        try:
            head_slot = get_node_head_slot(node_url)
        except Exception as e:
            logging.error(f"Error getting head slot: {e}. Retrying...")
            time.sleep(5)
            continue
        logging.info(f"Head slot: {head_slot}")
        targetSlot = min(
            last_slot_saved + DEFAULT_BACKFILLING_BATCH_SIZE,
            head_slot,
        )
        if targetSlot > last_slot_saved:
            try:
                loadSlotGuessesDatabase(
                    last_slot_saved + 1,
                    targetSlot,
                    classifier,
                    model_folder,
                    node_url,
                    add_to_model,
                    db,
                )
            except EndSlotUnkown:
                logging.info("End slot unknown, waiting for next slot")
                time.sleep(0.5)
                continue
            last_slot_saved += targetSlot - last_slot_saved
            end = time.time()
            time.sleep(max(0, 12 - (end - start)))
        else:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
