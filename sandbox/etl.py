# %% Goal: load metadata.yaml and insert into mongoDB

import os
from pathlib import Path

import dotenv
from pymongo.mongo_client import MongoClient

dotenv.load_dotenv()

repo_dirpath = Path(__file__).parents[1]
terraform_output = dotenv.dotenv_values(
    dotenv_path=repo_dirpath / "terraform/output.env",
)

uri_with_options = terraform_output["mongodb_uri_with_options"]
uri = f"mongodb://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@{uri_with_options.removeprefix('mongodb://')}"
print(uri)
client = MongoClient(uri)

# Send a ping to confirm a successful connection
client.admin.command("ping")
print("Pinged your deployment. You successfully connected to MongoDB!")


print("listing db")
for dbname in client.list_database_names():
    for collection in client[dbname].list_collection_names():
        print(f"{dbname=}, {collection=}")

# %%cluster

# Select the database and collection
collection = client["sample_airbnb"]["listingsAndReviews"]

# Query and list the first 10 documents (rows) from the collection
cursor = collection.find().limit(1)
for document in cursor:
    print(document)

print("Finished")

# %% create database and collection

# database and collection is created automatically, see
# https://stackoverflow.com/a/8566951/2135504
dct = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "age": 32,
    "dct": {"1": 2, "a": "b"},
    "lst": [1, 2, 3, "foo"],
}

collection = client["main"]["main"]
collection.insert_one(dct)
