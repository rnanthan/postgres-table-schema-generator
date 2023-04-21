**Amazon RDS for PostgreSQL - Table Schema Generator**

PostgreSQL is one of the most powerful open-source relational databases and is widely used on the market. Amazon RDS enables PostgreSQL deployments on the AWS cloud and simplifies setup, operation, and scaling.

Amazon RDS for PostgreSQL is used as a centralised repository for the business intelligence system that stores data from different sources in a unified schema and structure to create a single source of truth. We often get CSV extracts from third-party systems and stored them in the S3 data lake and then copied to PostgreSQL Database using COPY command. Before copying, we must create tables in PostgreSQL database to load CSV data. This utility, Postgres Table Schema Generator, allows you to generate the table schema. You can automate the table creation in PostgreSQL using this tool.

![](/Users/nanthan/Downloads/Untitled-Page-10.jpg)

**1. Upload CSVs**

You can upload CSV files into the S3 data lake using AWS console or AWS CLI or via scripts.

**2. Run Table Schema Generator script**

Prerequisites

_Use the CloudFormation template to create SSM parameters, S3, and IAM roles. You need to provide PostgreSQL connection parameters and S3 bucket name as CloudFormation parameters. Provisioning Amazon RDS for PostgreSQL Database is out of scope, and you have to make sure it is already created._

Set the following environment variable.

export AWS_PROFILE=<AWS Profile> ## Make sure to create an AWS profile with the right aws_access_key_id and aws_secret_access_key
export ENV=local ## set to local if you are running the script locally. 

Install Python libs

pip3 install -r requirements.txt

Run the schema generator script. You have to provide the CSV filename in the S3 bucket and the table name as an argument. The schema name is optional and if it is not provided, the table will be created under the default schema, public.

python3 table_schema_generator.py <CSV filename in S3> <table_name> -s <schema_name>

This script will generate SQL for creating a table. The script will find the best datatype, text length, and primary key based on the data.

The generated output will be stored ./output location and feel free to edit if you want to change anything.

Optionally, it enables you to create the table and requires argument --create_table yes or -c yes.

**3. Run Create Table Script**

Run the create table script as follows. It will create the table in PostgreSQL database.

python3 create_table.py 

**4. Copy the CSV data in S3 to the table created in PostgreSQL database.**

You can use the following command to copy the data. CloudFormation template creates IAM role and you can get the PostgresCopyRole ANR from CloudFormation stack output.

COPY <schema_name>.<table_name> from
's3://<s3 bucket name>/<object key>'
iam_role <PostgresCopyRole ARN>
IGNOREHEADER 1
CSV;

