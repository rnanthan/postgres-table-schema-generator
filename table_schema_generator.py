import io
import argparse
import pandas as pd

from common.config import s3InputBucket, s3_client
from common.constant import EMPTY
from common.s3_util import get_object
from create_table import execute_create_table


def change_case(str):
    str = str.replace(' ', '_')
    str = str.replace('-', '_')
    str = str.replace('.', '_')
    res = [str[0].lower()]
    previous = res
    for c in str[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            if previous != '_':
                res.append('_')
            res.append(c.lower())
        else:
            previous = c
            res.append(c)
    return ''.join(res)


def get_primary_key(df):
    column_list = df.columns.tolist()
    i = 0
    for data in df:
        if '_value' in str(column_list[i]):
            deDuped = df.drop_duplicates(data)
            if len(deDuped.index) == len(df.index):
                return change_case(data)
        i += 1
    return EMPTY


def create_postgres_table_stmt(df, table, schema='public'):
    sort_key = EMPTY
    d_types = df.convert_dtypes()
    output = io.StringIO()
    output.write(f"CREATE TABLE IF NOT EXISTS {schema}.{table} (")
    for d in d_types:
        if d_types[d].dtype == 'string':
            if '_display' in d:
                if int(df[d].str.len().max()) < 255:
                    output.write(f'{change_case(d)}  VARCHAR({int(df[d].str.len().max())}), ')
                else:
                    output.write(f'{change_case(d)}  TEXT, ')
            else:
                try:
                    pd.to_datetime(df[d], dayfirst=True)
                    output.write(f'{change_case(d)} TIMESTAMP, ')
                except Exception as e:
                    try:
                        pd.to_timedelta(df[d])
                        output.write(f'{change_case(d)} TIMESTAMP, ')
                        if sort_key == EMPTY:
                            sort_key = change_case(d)
                    except Exception as e:
                        if int(df[d].str.len().max()) < 255:
                            output.write(f'{change_case(d)}  VARCHAR({int(df[d].str.len().max())}), ')
                        else:
                            output.write(f'{change_case(d)}  TEXT, ')
        elif d_types[d].dtype == 'Int64':
            if '_display' in d:
                output.write(f'{change_case(d)}  VARCHAR(100), ')
            elif df[d].isin([0, 1]).all():
                output.write(f'{change_case(d)} BOOLEAN, ')
            else:
                output.write(f'{change_case(d)} FLOAT, ')
        elif d_types[d].dtype == 'Float64':
            if '_display' in d:
                output.write(f'{change_case(d)}  VARCHAR(100), ')
            else:
                output.write(f'{change_case(d)} FLOAT, ')
        elif d_types[d].dtype == 'boolean':
            if '_display' in d:
                output.write(f'{change_case(d)}  VARCHAR(10), ')
            else:
                output.write(f'{change_case(d)} BOOLEAN, ')

    sql = output.getvalue()

    primary_key = get_primary_key(df)
    if len(primary_key) > 0:
        sql += f' PRIMARY KEY ({df.columns.tolist()[0]}, {primary_key})'
    else:
        sql = sql[:-2]
    sql = sql + ')'
    sql += ';'
    return sql


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("s3_object_name", help="CSV filename uploaded to S3 bucket.")
    parser.add_argument("table_name", help="Preferred table name.")
    parser.add_argument("--create_table", "-c", default='no', help="If true, table will created in the database.")
    parser.add_argument("--schema_name", "-s", default="public",
                        help="Schema name in which you want to create a table.")

    args = vars(parser.parse_args())
    object_key = args['s3_object_name']
    table_name = args['table_name']
    schema_name = args['schema_name']
    create_table = args['create_table']
    obj = get_object(s3_client, s3InputBucket, object_key)
    df = pd.read_csv(obj, low_memory=False)
    sql = create_postgres_table_stmt(df, table_name, schema_name)
    with open('output/create_table.sql', 'w') as f:
        f.write(sql)
    print('################## CREATE TABLE DDL ##################')
    print(sql)
    print('######################################################')
    if create_table == 'yes':
        execute_create_table()
