import argparse
import logging
import os
import time
import blockprint.knn_classifier as knn
from guessRequester import getSlotGuesses, EndSlotUnkown
from Postgres import Postgres, parse_db_endpoint_string

DEFAULT_MODEL_FOLDER = "model"
DEFAULT_NODE_URL = "http://localhost:5052"
DEFAULT_BACKFILLING_BATCH_SIZE = 10000
MAX_RETRIES = 5


def parse_args():
    parser = argparse.ArgumentParser(description="Request a guess for a given slot")
    parser.add_argument(
        "--model-folder",
        default=DEFAULT_MODEL_FOLDER,
        type=str,
        help="Path to the folder with model files. Default: model",
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
        end = time.time()
        logging.info("Inserted {} rows in {} seconds".format(len(guesses), end - start))


def backfillSlots(
    last_slot_saved, classifier, model_folder, node_url, add_to_model, db
):
    done = False
    batch_size = DEFAULT_BACKFILLING_BATCH_SIZE
    retries = 0
    while not done:
        try:
            loadSlotGuessesDatabase(
                last_slot_saved + 1,
                last_slot_saved + batch_size,
                classifier,
                model_folder,
                node_url,
                add_to_model,
                db,
            )
        except EndSlotUnkown:
            if batch_size == 1:
                done = True
            else:
                batch_size = int(batch_size / 2)
                logging.info(
                    "End slot unknown, reducing batch size to {}".format(batch_size)
                )
                continue
        except Exception as e:
            logging.error("Error while backfilling: {}".format(e))
            if retries >= MAX_RETRIES:
                logging.error("Max retries reached, aborting")
                raise e
            else:
                retries += 1
                logging.info("Retrying...")
                time.sleep(5)
                continue
        retries = 0
        last_slot_saved += DEFAULT_BACKFILLING_BATCH_SIZE


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s - %(message)s")

    args = parse_args()
    model_folder = args.model_folder or DEFAULT_MODEL_FOLDER
    add_to_model = args.add_to_model
    node_url = args.node_url or DEFAULT_NODE_URL
    reindex = args.reindex or False
    print("Reindex: {}".format(reindex))
    if not os.path.exists(model_folder):
        logging.error(f"Model folder {model_folder} does not exist")
        exit(1)

    # Load the model
    logging.info(f"Loading model from {model_folder}...")
    start = time.time()
    classifier = knn.Classifier(model_folder)
    end = time.time()
    logging.info(f"Classifier loaded, took {end - start} seconds")

    logging.info("Connecting to database...")
    db = Postgres(url=args.postgres_endpoint)
    logging.info("Connected to database")
    db.create_table(
        "t_slot_client_guesses",
        "f_slot integer, f_best_guess_single text, f_best_guess_multi text, f_probability_map text[], f_proposer_index integer",
        "f_slot",
        replace=reindex,
    )
    last_slot_saved = db.dict_query("SELECT MAX(f_slot) FROM t_slot_client_guesses")[0][
        "max"
    ]
    if last_slot_saved is None:
        last_slot_saved = 0
    logging.info(f"Last slot saved: {last_slot_saved}")

    logging.info("Backfilling slots...")
    backfillSlots(last_slot_saved, classifier, model_folder, node_url, add_to_model, db)

    last_slot_saved = db.dict_query("SELECT MAX(f_slot) FROM t_slot_client_guesses")[0][
        "max"
    ]

    while True:
        try:
            loadSlotGuessesDatabase(
                last_slot_saved + 1,
                last_slot_saved + 1,
                classifier,
                model_folder,
                node_url,
                add_to_model,
                db,
            )
        except EndSlotUnkown:
            logging.info("End slot unknown, waiting for next slot")
            time.sleep(1)
            continue
        last_slot_saved += 1
        time.sleep(12)


if __name__ == "__main__":
    main()
