from common.log_util import log
from common.postgres_util import PostgresDataManager
from common.config import dbHost, dbName, dbUser, dbPassword


def execute_create_table():
    try:
        dbCon = PostgresDataManager.get_conn(dbHost, dbUser, dbPassword, dbName)
        script = open('output/create_table.sql', "r").read()
        log.debug(f'Transformation Script: {script}')
        log.info('Start creating table.')
        PostgresDataManager.execute_update(dbCon, script)
        log.info('Finish creating table.')
    except Exception as e:
        log.error('Error in creating table. {0}'.format(e))
