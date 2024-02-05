# About

![](README.assets/2024-01-29-23-44-57.png)

ElliptIO is a small python library for storing and accessing files in data lakes in a data science context. It stores files including automatically generated metadata on any file system and inserts metada into a database. A lot of inspiration is drawn from [Weights & Biases](https://github.com/wandb/wandb).

It is named after the Elliptio mussel genus which lives in freshwater lakes.

# Problems and solution approach

Particular in data science you often find data lakes where...

| Problem                        | Solution approach                                                                                                           |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| data cannot be reproduced      | [Automatically log](https://docs.wandb.ai/guides/track/log#automatically-logged-data) required information.                 |
| data lineage is unknown        | [Automatically track](https://docs.wandb.ai/guides/artifacts/explore-and-traverse-an-artifact-graph) lineage between files. |
| data is accidentally modified  | Lock files using S3 lock.                                                                                                   |
| data has no metadata           | Users can specify custom metadata when saving files.                                                                        |
| directory structure is chaotic | Simply save files by date and user. A good metadata search makes structure much less important.                             |
| data is duplicated             | Automatically replace duplicated files with references (not yet implemented)                                                |

## Existing solutions

I find Weights and Biases a great app, from which a lot of inspiration is drawn. However, it can be rather expensive and focuses on a lot more things than just data storage, so can easily be an overkill.

Object stores such as S3 or Ceph already provide the option to store metadata. However, this does not cover all required data for reproducibility. Also, querying metadata is not as efficient as querying a database.

# How to use

```python
import json
import pandas as pd
from elliptio import get_default_handler, ManualMetadata

# setup manual metadata (optional) and handler
metadata = ManualMetadata(
    ticket="abc-123",
    project="my_project",
    config=json.dumps({"example": "value"}),
    description="lorem ipsum",
)
h = get_handler(dirpath="/tmp/my_data_lake", manual_metadata=metadata)

# save file directly to remote
df = pd.DataFrame({"a": [1], "b": [2]})
with h.create("train.txt") as f:
    df.to_csv(f.remote_url)

# load file. Its file_id will be added to every new file in this session.
train_file = h.load(f.file_id)

# upload an existing new file
# model.train(train_file)
with h.create("model.pickle") as model:
    model.upload("/tmp/my_data_lake/best_model.pickle")
assert model.based_on == [train_file.file_id]

# querying the database
df = h.query({"ticket": "abc-123"})
```

# How to install

Simply run `pip install elliptio`.

# Tips

- You can easily pass custom filesystem, database, tracker and id_creator classes to `get_handler`
- The current filesystem class is based on fsspec and thus should support [all their filesystem implementations (S3, Azure Blob service, Google Cloud Storage, etc.)](https://filesystem-spec.readthedocs.io/en/latest/api.html#other-known-implementations). See example below.
- To create a nice GUI for your database, I can recommend [Metabase](https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker). Metabase, without the enterprise features, is APGL licensed. You have to be careful when modifying the code or incorporating it into your application, but running the app without modifications internally in "vanilla mode" seems to be fine [according to them](https://discourse.metabase.com/t/licensing-and-agpl-implicaitons-in-different-usage-scenarios/3115/5).
- The [terraform/](terraform/) directory contains example Terraform code to setup S3 and a free MongoDB on AWS. However, there's currently no MongoDB implementation for the DatabaseInterface.

```python
# Example for passing custom FileSystemInterfaces like S3
from elliptio.adapters import db, fs
from elliptio import get_default_handler

h = get_default_handler(
    fs=fs.FsspecFilesystem(prefix="some/prefix/", protocol="s3", storage_options={}),
    db=db.SqlDatabase("db.sqlite"),
)
```

# TODOs

- compare with other data versioning tools from https://github.com/EthicalML/awesome-production-machine-learning/ (and other reproducibility tools)
- automatic metadata
  - automatically log git-hash and `git diff` (also from new untracked files)
  - does `argv` work with Jupyter notebooks?!
