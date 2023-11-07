import json
import boto3
import yaml
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
import logging

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)  # Set the log level to INFO or your desired level


def lambda_handler(event: dict, context: dict):
    _LOGGER.info(event)
    del context

    # read metadata.yaml
    _LOGGER.info("loading from S3")
    s3_client = boto3.client("s3")
    response = s3_client.get_object(
        Bucket=event["Records"][0]["s3"]["bucket"]["name"],
        Key=event["Records"][0]["s3"]["object"]["key"],
    )
    yaml_string = response["Body"].read().decode("utf-8")
    dct = yaml.safe_load(yaml_string)

    # save to mongodb
    _LOGGER.info("saving to mongodb")
    collection = _get_mongo_client(
        database_name="main",
        collection_name="main",
    )
    collection.insert_one(dct)

    _LOGGER.info("returning")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Success!"}),
    }


class _SSM_Getter:
    def __init__(self) -> None:
        self.ssm = boto3.client("ssm")

    def get(self, name: str):
        response = self.ssm.get_parameter(Name=name)
        return response["Parameter"]["Value"]


def _get_mongo_client(database_name: str, collection_name: str) -> Collection:
    _LOGGER.info("Getting SSM Params")
    ssm = _SSM_Getter()
    uri_with_options = ssm.get("MONGODB_URI")
    username = ssm.get("MONGODB_USERNAME")
    password = ssm.get("MONGODB_PASSWORD")

    uri = (
        f"mongodb://{username}:{password}@{uri_with_options.removeprefix('mongodb://')}"
    )
    _LOGGER.info("Connecting to Mongo")
    client = MongoClient(uri)
    client.admin.command("ping")

    _LOGGER.info("Returning collection")
    return client[database_name][collection_name]
