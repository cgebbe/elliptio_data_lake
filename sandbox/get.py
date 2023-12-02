# ruff: noqa
# %%

import pandas as pd
import pymongo
from elliptio import Handler, LocalFile

eio = Handler(remote_file_cls=LocalFile)

# %%

artifact = eio.get(artifact_id="artifact_67cefe12-5f13-4d01-bfb8-f392b8589172")
# %%
artifact.files["a.txt"].download("/home/cgebbe/tmp/foo2.txt")

# %%

# sort_order = [("creation_time", pymongo.ASCENDING)]  # Replace with your field name
query = {}
exclude_columns = ("python_packages",)

cursor = (
    eio._collection.find(
        query,
        projection={c: 0 for c in exclude_columns},
    )
    .sort("creation_time", pymongo.DESCENDING)
    .limit(7)
)
dct_list = list(cursor)
print(dct_list)

table = pd.DataFrame(dct_list)

first_columns = [
    "artifact_id",
    "creation_time",
    "username",
    "files",
    "argv",
]
subsequent_columns = set(table.columns).difference(first_columns)
table = table[first_columns + sorted(subsequent_columns)]
