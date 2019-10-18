import psycopg2
from sqlalchemy import create_engine
from . import CREDENTIALS, logger


def db_uri(credentials):
    """Construct and return db URI string (RFC-1738) from credentials.
    """
    return 'postgresql+psycopg2://' +\
        CREDENTIALS['user']+':' +\
        CREDENTIALS['password'] + '@localhost:' +\
        CREDENTIALS['port'] + '/' +\
        CREDENTIALS['database']


def save_to_db_table_from_df(df, credentials, table_name, if_exists='append'):
    """Instantiate sqlalchemy engine with credentials to connect to db,
    then write `DataFrame` to table.
    """
    try:
        # Instantiate db engine
        db_uri_string = db_uri(credentials)
        engine = create_engine(db_uri_string)
        # Write df to table
        df.to_sql(table_name, engine, if_exists=if_exists)
        logger.info('Successful write to table: {}'.format(table_name))

    except (Exception, psycopg2.Error) as e:
        logger.info('Error writing to PostgreSQL database.', e)
