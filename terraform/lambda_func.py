import json
from pprint import pprint
import boto3
import yaml
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection


def lambda_handler(event: dict, context: dict):
    pprint(event)
    del context

    # read metadata.yaml
    s3_client = boto3.client("s3")
    response = s3_client.get_object(
        Bucket=event["Records"][0]["s3"]["bucket"]["name"],
        Key=event["Records"][0]["s3"]["object"]["key"],
    )
    yaml_string = response["Body"].read().decode("utf-8")
    dct = yaml.safe_load(yaml_string)

    # save to mongodb
    collection = _get_mongo_client(
        database_name="main",
        collection_name="main",
    )
    collection.insert_one(dct)

    return {"statusCode": 200, "body": json.dumps(dct)}


class _SSM_Getter:
    def __init__(self) -> None:
        self.ssm = boto3.client("ssm")

    def get(self, name: str):
        response = self.ssm.get_parameter(Name=name)
        return response["Parameter"]["Value"]


def _get_mongo_client(database_name: str, collection_name: str) -> Collection:
    ssm = _SSM_Getter()
    uri_with_options = ssm.get("MONGODB_URI")
    username = ssm.get("MONGODB_USERNAME")
    password = ssm.get("MONGODB_PASSWORD")

    uri = (
        f"mongodb://{username}:{password}@{uri_with_options.removeprefix('mongodb://')}"
    )
    client = MongoClient(uri)
    client.admin.command("ping")

    return client[database_name][collection_name]
