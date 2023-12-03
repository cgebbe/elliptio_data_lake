# TODO

- instructions on how to use (jupyter notebook as user story)
- instructions on required env vars
  - MongoDB
    - specify mongo_full_URI, db_name and collection_name
  - File-local
    - ELLIPTIO_LOCAL_ROOT
  - File-AWS
    - AWS_ACCESS_KEY, ... , ELLIPTIO_S3_BUCKET_NAME
- instructions on how to setup
  - locally
    - mongoDB and
  - AWS
    - mongoDB Atlas
- move terraform directory into aws
- separate required envs for terraform and for code

MAYBE

- git-hash
- find() shall report number of items (not just the displayed ones)
- sent_bytes(byte_stream, remote_url)
- fetch_bytes(remote_url)
- test for all storage types

# Talk

Title

Storing files with metadata, reproducibility and data lineage

Abstract

Have you ever come across files (unstructured data) which you cannot reproduce? For example, the evaluation metrics from your coworker which were likely generated with some local unpushed modifications? Are you looking for that one preprocessed dataset that your now ex-coworker stored _somewhere_? Have you only realized now that the golden annotation table stored on the network share seems to have been modified about a month ago, thereby invalidating all your recent results?

In this talk I'd like to present some real-life problems when storing data and propose solution approaches. As inspiration, I'd like to present the small `elliptio` python library. It's an opinionated prototype for storing data with metadata, reproducibility and data lineage in mind. It also stores metadata in a Mongo database, thereby allowing fast queries.

Description

Preliminary slide structure

- Problems
  - reproducibility
  - no lineage
  - no metadata
  - accidental modification
  - chaotic directory structures
  - duplicated data
- Overview of existing applications (e.g. wandb, ceph, ...)
- Presentation of elliptio library
  - function specification: user story
  - technical specificiation

See https://github.com/cgebbe/elliptio_data_lake (WIP)
