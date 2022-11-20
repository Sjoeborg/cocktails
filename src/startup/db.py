import sqlite3
import pandas as pd
FILE_PATH = '../Downloads/test.parquet'#'./data_scripts/data/difford_1_5000_processed.parquet'


def create_connection() -> sqlite3.Connection:
    """ create a database connection to a database that resides
    in the memory
    """
    conn = sqlite3.connect(':memory:')
    return conn


def load_parquet(db_conn: sqlite3.Connection, file_path: str = FILE_PATH) -> sqlite3.Connection:
    df_parquet = pd.read_parquet(file_path)
    df_parquet.to_sql('difford', db_conn, index=False)

    return db_conn


def read_db(query: str, db_conn: sqlite3.Connection) -> list[str]:
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()

    return result


if __name__ == '__main__':
    conn = create_connection()

    conn = load_parquet(conn)

    result = read_db('select * from difford', conn)
    print(result)
