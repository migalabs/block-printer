import argparse
import logging
import os
import time
import blockprint.knn_classifier as knn
from guessRequester import getSlotGuesses
from Postgres import Postgres, parse_db_endpoint_string

DEFAULT_MODEL_FOLDER = "model"
DEFAULT_NODE_URL = "http://localhost:5052"


def parse_args():
    parser = argparse.ArgumentParser(description="Request a guess for a given slot")
    parser.add_argument(
        "--model-folder",
        default=DEFAULT_MODEL_FOLDER,
        type=str,
        help="Path to the folder with model files. Default: model",
    )
    parser.add_argument(
        "--start-slot", type=int, default=0, help="Start Slot to request a guess for"
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
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s - %(message)s")

    args = parse_args()
    model_folder = args.model_folder or DEFAULT_MODEL_FOLDER
    add_to_model = args.add_to_model
    node_url = args.node_url or DEFAULT_NODE_URL
    if not os.path.exists(model_folder):
        logging.error(f"Model folder {model_folder} does not exist")
        exit(1)

    # Load the model
    logging.info(f"Loading model from {model_folder}...")
    start = time.time()
    classifier = knn.Classifier(model_folder)
    end = time.time()
    logging.info(f"Classifier loaded, took {end - start} seconds")

    try:
        port, database, user, password, host = parse_db_endpoint_string(
            args.postgres_endpoint
        )
    except Exception as e:
        logging.error("Error parsing postgres endpoint string: {}".format(e))
        return
    logging.info("Connecting to database...")
    db = Postgres(port=port, host=host, user=user, password=password, database=database)
    logging.info("Connected to database")
    db.create_table(
        "t_slot_client_guesses",
        "f_slot integer, f_best_guess_single text, f_best_guess_multi text, f_probability_map text[], f_proposer_index integer",
        "f_slot",
        replace=True,
    )
    guesses = getSlotGuesses(
        1, 2, classifier, model_folder, node_url, add_to_model, db_format=True
    )
    if guesses is None:
        logging.error("Error getting guesses")
        exit(1)
    print(guesses)
    print((guesses[0][3]))
    db.insert_rows(
        "t_slot_client_guesses",
        (
            "f_slot",
            "f_best_guess_single",
            "f_best_guess_multi",
            "f_probability_map",
            "f_proposer_index",
        ),
        guesses,
    )


if __name__ == "__main__":
    main()
