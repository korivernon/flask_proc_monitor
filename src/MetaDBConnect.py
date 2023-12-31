import traceback

import psycopg2
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
import pandas as pd

from datetime import datetime

USE_PG_HOST = {"host": ''}


def today():
    date = datetime.now()
    if date < datetime(date.year, date.month, date.day, 9, 30):
        date = date - timedelta(days=1)
    return date.strftime("%Y-%m-%d")


from datetime import timedelta
import config


class MetadataDBConnect:
    def __init(self, host=config.POSTGRES_HOST):
        self.host = host

    def run_sql(self, sql, return_result=False, verbose=False):
        try:
            if verbose: print(f"run_sql:\n\t{sql}")
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if return_result:
                if verbose: print("Returning Result")
                cols = [s.name for s in cursor.description]
                try:
                    df = pd.DataFrame(cursor.fetchall(), columns=cols)
                    # Close the cursor and connection
                    cursor.close()
                    return df
                except:
                    return pd.DataFrame()
        except errors.lookup(UNIQUE_VIOLATION):
            print("Duplicate Entry")
            return False
        except:
            print(f"Hit Error!\n{traceback.format_exc()}")
            return False
        return True

    def run_sql_err(self, sql, return_result=False, verbose=False):
        try:
            if verbose: print(f"run_sql_err\n\t{sql}")
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if return_result:
                if verbose: print("Returning Result")
                cols = [s.name for s in cursor.description]
                try:
                    df = pd.DataFrame(cursor.fetchall(), columns=cols)
                    # Close the cursor and connection
                    cursor.close()
                    return df
                except:
                    raise Exception("Error fetching result")
        except errors.lookup(UNIQUE_VIOLATION):
            print("Duplicate Entry")
            raise Exception("Duplicate Entry")
        except:
            print(f"Hit Error!\n{traceback.format_exc()}")
            raise Exception("Error in execution")
        return True

    def __enter__(self):
        # Establishing the connection
        for location, host in config.POSTGRES_HOSTS.items():
            try:
                self.conn = psycopg2.connect(
                    database=config.POSTGRES_DB, user=config.POSTGRES_USER,
                    password=config.POSTGRES_PASS, host=host, port=config.POSTGRES_PORT
                )
                # Setting auto commit false
                self.conn.autocommit = True
            except:
                print(f"Unable to connect to postgres in location: {location} IP {host} .")
                print(traceback.format_exc())
                continue
            else:
                print("successfully connected")
                return True
        print(f"Unable to any hosts.")
        exit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.conn.close()
        except:
            print("Unable to close postgres cursor.")

    def insert_process(self, process_name, script_path, command_line, plist, run_at_load, active, project_name):
        sql = f'''
        INSERT INTO scheduler_info (process_name, script_path, command_line, plist, run_at_load, active, project_name)
        VALUES ('{process_name}','{script_path}','{command_line}','{plist}','{run_at_load}', '{active}','{project_name}');
            '''
        try:
            print(sql)
            self.run_sql_err(sql)
        except:
            print(traceback.format_exc())
            return False
        return True

def get_procs(process_name):
    sql = f'''select * from scheduler_info where process_name='{process_name}' '''
    conn = MetadataDBConnect()
    with conn:
        df = conn.run_sql(sql, return_result=True)
    return df

def get_procs_by_project(project_name):
    sql = f'''select * from scheduler_info where project_name='{project_name}' '''
    conn = MetadataDBConnect()
    with conn:
        df = conn.run_sql(sql, return_result=True)
    return df

def get_all_procs():
    sql = f'''select * from scheduler_info'''
    conn = MetadataDBConnect()
    with conn:
        df = conn.run_sql(sql, return_result=True)
    return df

def get_all_projects():
    sql = f'''select distinct(project_name) as project_name from scheduler_info'''
    conn = MetadataDBConnect()
    with conn:
        df = conn.run_sql(sql, return_result=True)
    return list(df['project_name'].values)

def fetch_command_line_from_name(name):
    sql = f'''select * from scheduler_info where process_name = '{name}' '''
    conn = MetadataDBConnect()
    with conn:
        df = conn.run_sql(sql, return_result=True)
    cli = df.iloc[0]['command_line']
    return cli

def segregate_procs( all_procs = get_all_procs()):
    project_names = get_all_projects()
    matrix = {project_name:all_procs[all_procs['project_name'] == project_name] for project_name in project_names}
    return matrix

def main():
    print(segregate_procs())


if __name__ == '__main__':
    main()
