import clickhouse_connect

TABLE_NAME = "t_slot_client_guesses"


class ClickHouseDB:
    def __init__(self, dsn):
        self.client = clickhouse_connect.get_client(dsn=dsn)

    def create_table(self):
        self.client.query(
            f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}
                (
                    f_slot UInt64,
                    f_best_guess_single String,
                    f_best_guess_multi String,
                    f_probability_map Array(String),
                    f_proposer_index UInt64
                )
                ENGINE = ReplacingMergeTree ORDER BY (f_slot)"""
        )

    def get_max_slot(self):
        query_res = self.client.query(f"SELECT MAX(f_slot) FROM {TABLE_NAME}")
        return query_res.first_row[0]

    def insert_client_guesses(self, guesses):
        # guesses = convert_to_clickhouse_format(guesses)
        self.client.insert(
            TABLE_NAME,
            guesses,
        )


def convert_to_clickhouse_format(guesses):
    return [
        (
            guess["slot"],
            guess["best_guess_single"],
            guess["best_guess_multi"],
            guess["probability_map"],
            guess["proposer_index"],
        )
        for guess in guesses
    ]
