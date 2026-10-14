import psycopg2
import os

from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self, db_env_variable : str):
        self.env_var = db_env_variable

    def convert_placeholders(self, query):
        return query.replace("?", "%s")
    
    def run(self, query, values=()):
        query = self.convert_placeholders(query)

        with psycopg2.connect(os.getenv(self.env_var)) as conn:
            with conn.cursor() as cur:

                cur.execute(query, values)
                result = cur.fetchall()

        return result

    def runs(self, *queries, values_list=None) -> int:
        if values_list is None:
            values_list = [() for _ in queries]
        row_count = 0

        with psycopg2.connect(os.getenv("DATABASE_URL")) as conn:
            cur = conn.cursor()
            for query, values in zip(queries, values_list):
                query = self.convert_placeholders(query)
                cur.execute(query, values)
                rows = cur.rowcount
                row_count += rows
        return row_count

    def colStr(self, cols_tuple, prefix = ""):
        if prefix:
            cols_tuple = [prefix + col for col in cols_tuple]
        return ", ".join(cols_tuple)

    def build_insert(self, table, insert_data, return_cols = None):
        columns = ", ".join(insert_data.keys())
        place_holders = ", ".join(['?' for _ in insert_data])
        if return_cols is None:
            returning = columns
        else:
            returning = ", ".join(return_cols)
        sql = f"INSERT INTO {table} ({columns}) VALUES ({place_holders}) RETURNING {returning};"
        return sql, tuple(insert_data.values())
    
    def build_select(self, table : str, cols : tuple, filter_data : dict = None, order_by: str = "", limit = None):
        if filter_data is None:
            filter_data = {}
        columns = ", ".join(cols)
        where = " AND ".join([f"{col} = ?" if filter_data[col] is not None else f"{col} IS ?" for col in filter_data.keys()]) if filter_data else "TRUE"
        order = f" ORDER BY {order_by}" if order_by else ""
        lim = f" LIMIT {str(limit)}" if limit is not None else ""
        sql = f"SELECT {columns} FROM {table} WHERE {where}{order}{lim};"
        return sql, tuple(filter_data.values())
    
    def build_update(self, table, insert_data, filter_data, return_cols = None):
        sets = ", ".join([f"{col} = ?" for col in insert_data.keys()])
        where = " AND ".join([f"{col} = ?" if filter_data[col] is not None else f"{col} IS ?" for col in filter_data.keys()]) if filter_data else "FALSE"
        vals = tuple(insert_data.values()) + tuple(filter_data.values())
        if return_cols is None:
            returning = ""
        else:
            returning = " RETURNING " + ", ".join(return_cols)
        sql = f"UPDATE {table} SET {sets} WHERE {where}{returning};"
        return sql, vals

    def parse_dict(self, tupl : tuple, *keys):
        if len(keys) != len(tupl):
            raise ValueError("Nr of tuple elements does not match nr of keys")
        return {key : val for key, val in zip(keys, tupl)}

    def parse_dicts(self, tupl_list : list[tuple], *keys):
        return [self.parse_dict(tupl, *keys) for tupl in tupl_list]
        