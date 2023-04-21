import os
import boto3

from common.ssm_util import get_ssm_parameter

if os.environ['ENV'] == 'local':
    session = boto3.Session(profile_name=os.environ['AWS_PROFILE'])
    s3_client = session.client('s3')
    dynamodb_client = session.client('dynamodb')
    ssm_client = session.client('ssm')
    s3_resource = session.resource('s3')
else:
    s3_client = boto3.client('s3')
    ssm_client = boto3.client('ssm')
    s3_resource = boto3.resource('s3')

dbHost = get_ssm_parameter(ssm_client, '/postgres-table-schema-generator/postgres.dbHost', False)
dbUser = get_ssm_parameter(ssm_client, '/postgres-table-schema-generator/postgres.dbUser', False)
dbPassword = get_ssm_parameter(ssm_client, '/postgres-table-schema-generator/postgres.dbPassword', True)
dbName = get_ssm_parameter(ssm_client, '/postgres-table-schema-generator/postgres.dbName', False)

s3InputBucket = get_ssm_parameter(ssm_client, '/postgres-table-schema-generator/input.bucket.name', False)