# %%

import os
import re
from pathlib import Path

import boto3
import dotenv
import pymongo
from pymongo.mongo_client import MongoClient


class _SSMGetter:
    def __init__(self) -> None:
        self.ssm = boto3.client("ssm")

    def get(self, name: str):
        response = self.ssm.get_parameter(Name=name)
        return response["Parameter"]["Value"]


ssm = _SSMGetter()
uri_with_options = ssm.get("MONGODB_URI")
username = ssm.get("MONGODB_USERNAME")
password = ssm.get("MONGODB_PASSWORD")

# %% Goal: load metadata.yaml and insert into mongoDB


use_local = True
if use_local:
    dotenv.load_dotenv()
    repo_dirpath = Path(__file__).parents[1]
    terraform_output = dotenv.dotenv_values(
        dotenv_path=repo_dirpath / "terraform/output.env",
    )
    uri_with_options = terraform_output["mongodb_uri_with_options"]
    username = os.environ["MONGODB_USERNAME"]
    password = os.environ["MONGODB_PASSWORD"]


uri = f"mongodb://{username}:{password}@{uri_with_options.removeprefix('mongodb://')}"
uri = "mongodb://dbuser:ThisIsAnUnbreakablePassword123@ac-0bq9e4f-shard-00-00.nhmly7n.mongodb.net:27017,ac-0bq9e4f-shard-00-01.nhmly7n.mongodb.net:27017,ac-0bq9e4f-shard-00-02.nhmly7n.mongodb.net:27017/main?ssl=true&authSource=admin&replicaSet=atlas-h8aiy7-shard-0"
print(uri)
client = MongoClient(uri)
client.admin.command("ping")
# %%


collection = client["main"]["main"]
sort_order = [("timestamp_field", pymongo.DESCENDING)]  # Replace with your field name
query = {"user": "cgebbe"}
query = {"python_packages.assertpy": "1.1"}
query = {"python_packages.assertpy": {"$regex": re.compile("1.+")}}

cursor = collection.find(query).limit(6)
for document in cursor:
    print(document)

# %%
dct = {"foo": 2, "bar": 4}
print(dct)


# %%
dct["foo"]
