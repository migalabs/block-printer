#!/usr/bin/env python3

import argparse
from blockprint.build_db import build_block_db
from blockprint.knn_classifier import Classifier

from blockprint.multi_classifier import MultiClassifier

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", required=True, help="path to sqlite database file")
    parser.add_argument(
        "--data-dir", required=True, help="training data for classifier(s)"
    )
    parser.add_argument("--classify-dir", required=True, help="data to classify")
    parser.add_argument(
        "--multi-classifier",
        default=False,
        action="store_true",
        help="build MultiClassifier from datadir",
    )
    parser.add_argument(
        "--force-rebuild", action="store_true", help="delete any existing database"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    db_path = args.db_path
    data_dir = args.data_dir
    data_to_classify = args.classify_dir

    if args.multi_classifier:
        classifier = MultiClassifier(data_dir)
    else:
        print("loading single KNN classifier")
        classifier = Classifier(data_dir)
        print("loaded")

    conn = build_block_db(
        db_path, classifier, data_to_classify, force_rebuild=args.force_rebuild
    )
    conn.close()

if __name__ == "__main__":
    main()
