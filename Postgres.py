import psycopg2
import binascii
from psycopg2.extras import DictCursor


# function to convert bytea data to string
def data_to_str(s):
    if s is None:
        return None
    if isinstance(s, bytes):
        return binascii.hexlify(s).decode("utf-8")
    return str(s)


def parse_db_endpoint_string(s):
    port = s.split(":")[3].split("/")[0]
    database = s.split(":")[3].split("/")[1]
    user = s.split(":")[1].split("@")[0].split("//")[1]
    password = s.split(":")[2].split("@")[0]
    host = s.split(":")[2].split("@")[1]
    return port, database, user, password, host


class Postgres:
    def __init__(
        self,
        port=None,
        user=None,
        password=None,
        database=None,
        host="localhost",
        url=None,
    ):
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        if url is not None:
            self.conn = psycopg2.connect(url)
        else:
            self.conn = psycopg2.connect(
                port=port, database=database, user=user, password=password, host=host
            )

    def dict_query(self, sql):
        data = None
        try:
            # create a cursor with DictCursor and custom functions
            cursor = self.conn.cursor(cursor_factory=DictCursor)
            psycopg2.extensions.register_adapter(bytes, data_to_str)

            # execute the SELECT statement
            cursor.execute(sql)
            data = [dict(row) for row in cursor.fetchall()]
            # close the cursor and connection
            cursor.close()

            # return all the data from the table as dictionaries
        except psycopg2.errors.UndefinedTable as error:
            print(error)
        return data

    def close(self):
        self.conn.close()

    def create_table(self, table_name, columns, primary_key, replace=False):
        cursor = self.conn.cursor()
        if replace:
            cursor.execute(f"DROP TABLE IF EXISTS public.{table_name};")
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS public.{table_name}({columns}, CONSTRAINT {table_name}_pkey PRIMARY KEY ({primary_key})) TABLESPACE pg_default;"
        )
        self.conn.commit()
        cursor.close()

    def insert_row(self, table_name, columns, values):
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            raise
        cursor.close()

    def insert_rows(
        self,
        table_name: str,
        columns: tuple,
        values: list[tuple],
        ignore_duplicates: bool = False,
    ):
        """
        Inserts multiple rows of data into a specified table in a SQL database.

        Args:
            table_name (str): The name of the table to insert rows into.
            columns (tuple): A list of column names in the order they appear in each tuple in `values`.
            values (List[Tuple]): A list of tuples, where each tuple represents a single row of data to be inserted into the table.
            ignore_duplicates (bool, optional): If True, any rows that would result in a duplicate primary key (or unique constraint) will be ignored and not inserted into the table. Defaults to False.

        Raises:
            Any error that occurs during the execution of the query.

        Returns:
            None
        """
        cursor = self.conn.cursor()
        try:
            subtitute_list = ",".join(["%s"] * len(values[0]))
            query = (
                f"INSERT INTO {table_name} ({subtitute_list})" % (columns)
                + f" VALUES ({subtitute_list})"
            )

            if ignore_duplicates:
                query += " ON CONFLICT DO NOTHING"
            cursor.executemany(query, values)
            self.conn.commit()
        except:
            self.conn.rollback()
            cursor.close()
            raise
        cursor.close()

    def get_last_entry(self, table_name, column):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT {column} FROM {table_name} ORDER BY {column} DESC LIMIT 1"
        )
        self.conn.commit()
        data = cursor.fetchone()
        cursor.close()
        return data[0] if data else 0
