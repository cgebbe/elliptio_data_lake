# %% Goal: load metadata.yaml and insert into mongoDB

import os

import dotenv
from pymongo.mongo_client import MongoClient

dotenv.load_dotenv()


user = "dbuser"
password = os.environ["MONGODB_PASSWORD"]
cluster = "main"
uri = f"mongodb+srv://{user}:{password}@{cluster}.nhmly7n.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
client.admin.command("ping")
print("Pinged your deployment. You successfully connected to MongoDB!")

# %%

for dbname in client.list_database_names():
    for collection in client[dbname].list_collection_names():
        print(f"{dbname=}, {collection=}")

# %%cluster

# Select the database and collection
collection = client["sample_airbnb"]["listingsAndReviews"]

# Query and list the first 10 documents (rows) from the collection
cursor = collection.find().limit(3)
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
