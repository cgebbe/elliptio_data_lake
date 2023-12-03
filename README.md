- [About](#about)
- [Problems and solution approach](#problems-and-solution-approach)
- [Functional specification / User stories](#functional-specification--user-stories)
  - [Save files](#save-files)
  - [Searching files by metadata](#searching-files-by-metadata)
  - [Using files](#using-files)
  - [Searching files by lineage](#searching-files-by-lineage)
- [Technical specification](#technical-specification)
  - [High level design](#high-level-design)
  - [Alternatives](#alternatives)
- [Further considerations](#further-considerations)
  - [Licensing](#licensing)
  - [Cost](#cost)

# About

ElliptIO is an opinionated application (idea) on how to store and access files in data lakes.

It is named after the Elliptio mussel genus which lives in freshwater lakes.

# Problems and solution approach

Particular in data science you often find data lakes where...

| problem                        | solution approach                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| data cannot be reproduced      | [Automatically log](https://docs.wandb.ai/guides/track/log#automatically-logged-data) required information.                     |
| data lineage is unknown        | [Automatically track](https://docs.wandb.ai/guides/artifacts/explore-and-traverse-an-artifact-graph) lineage between artifacts. |
| data is accidentally modified  | Lock files using S3 lock.                                                                                                       |
| data has no metadata           | Users can specify custom metadata as dict when saving files.                                                                    |
| directory structure is chaotic | Simply save files by date and user. A good metadata search makes structure much less important.                                 |
| data is duplicated             | Automatically replace duplicated files with references (not yet implemented)                                                    |

# Functional specification / User stories

## Save files

Andy is an ambitious data scientist who analyzes data and trains models. He just prepared a new `train.txt` and `test.txt` with a special stratification method. He saves them with the following API call:

```python
import elliptio as eio
artifact = eio.save(
  ["train.txt", "test.txt"],
  info={
    "type": "dataset_list",
    "stratification": "new-cool-method",
  },
)
```

Note that he doesn't need to specify the destination. The destination path is generated automatically and the S3 bucket is defined as an environment variable.

## Searching files by metadata

Brenda wants to use the files from Andy. However, Andy just started his Antartica-crossing last week and hasn't told anybody where he stored his work. So Brenda uses the internal data catalogue webpage to search for artifacts which were...

- generated by Andy
- generated within the last 10 days
- contain `*.txt` files
- are tagged with `*dataset*`

Based on the displayed results and the `stratification: new-cool-method` label, Brenda is pretty sure she found the correct file. She copies the artifact ID from the GUI.

## Using files

To use the file, Brenda uses the unique artifact ID and runs:

```python
artifact = eio.load("id_123456789")
pprint(artifact.metadata)
df = pd.read_csv(artifact.files["train.txt"].s3_url)
```

Unfortunately she gets an error upon opening the file. Could it be that Andy used another pandas version?

```python
artifact.logs.pip_freeze.download()
```

Yes, Andy used `2.0.1` whereas Brenda is using `1.4.0`. To be on the safe side, she quickly matches all her python libraries to the ones that Andy used by running `pip install -r pip_freeze.txt`. Afterwards, she trains a models and saves it via

```python
elliptio.create_artifact().save_files(["model.pth"], type="model")
```

## Searching files by lineage

Once Andy comes back from his antarctica-crossing, he wants to know whether anybody actually used the newly stratified dataset he created. He goes to the internal catalogue webpage and...

- quickly finds the artifact ID he created (`id123456789`)
- searches for artifacts which are _based on_ `id123456789`
- finds the model artifact from Brenda with `id777777777`
- searches for artifacts which are _based on_ `id777777777`
- finds an evaluation report artifact from Charlie with a corresponding S3 URL

He opens the corresponding folder (mounted via `s3fs`) and happily sees that the evaluation metrics improved compared to the previous stratification method.

Note that the lineage between `train.txt` and `model.pth` in Brendas run was tracked automatically: For any created artifact, all previously used artifacts are added as `based_on` unless explicitly stated otherwise.

# Technical specification

## High level design

The high level design consists of...

- a python lib which...
  - saves user files to a certain directory in S3 (e.g. `/year/month/day/user/artifact_id`)
  - saves log files from e.g. `pip-freeze` or `git diff`
  - creates a `metadata.yaml` file
- an AWS Lambda function
  - which inserts the contents of `metadata.yaml` to a database
- a database such as MongoDB Atlas
- the same python lib which...
  - efficiently queries the database for artifacts inlcuding their S3 URLs
  - accesses the stored files in S3
- a web GUI to connect and search the database. Options:
  - Metabase, see https://www.metabase.com/learn/questions/searching-tables
  - MongoDB Compass (local app), see https://www.mongodb.com/docs/compass/current/query/filter/
  - (?) MongoDB Atlas Search or MongoDB Atlas Data Explorer, see e.g. https://www.mongodb.com/docs/cloud-manager/data-explorer/documents/

<img src=README.assets/2023-10-15-19-55-53.png height=150>

## Alternatives

Object stores such as S3 or Ceph already provide the option to store metadata. However, this does not cover all required data for reproducibility. Also, querying metadata is not as efficient as querying a database.

Weights and Biases is an amazing python library, from which a lot of inspiration is drawn. It also offers the option to search and filter run- and artifact- tables. However, it can be rather expensive and focuses on a lot more things than just data storage.

# Further considerations

## Licensing

MongoDB is licenced under the "Server Side Public License". This prohibits "selling" MongoDB as a service, but you can use it as database, see https://www.mongodb.com/licensing/server-side-public-license/faq

> What are the implications of this new license on applications built using MongoDB and made available as a service (SaaS)? The copyleft condition of Section 13 of the SSPL applies only when you are offering the functionality of MongoDB, or modified versions of MongoDB, to third parties as a service. _There is no copyleft condition for other SaaS applications that use MongoDB as a database._

Metabase, without the enterprise features, is APGL licensed. You have to be careful when modifying the code or incorporating it into your application, but running the app without modifications internally in "vanilla mode" seems to be fine [according to them](https://discourse.metabase.com/t/licensing-and-agpl-implicaitons-in-different-usage-scenarios/3115/5):

> Our posture is a little different if you’re trying to embed our entire interface in your application, modify the actual program itself, etc. The situations you describe are standard vanilla modes of operation that we definitely don’t want to encumber in any way.

## Cost

- MongoDB Atlas has a free option for databases up to 512 MB
- Metabase itself is free if self-hosted (and used for internal purposes according to its license)
