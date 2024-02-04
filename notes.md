# User story2

class FileInfo

- rel_path
- remote_url
- ~~artifact_id ?! (could be multiple! Don't do this...)~~
- hash
- MMD
- AMD
- deduplicated_by # always the newer stuff

class File(FileInfo)

- fs
- upload(local_path)
- download(local_path)
- write_text()
- read_text()
- get_hash_and_size()

# User story File

create file (rel_path, fs, db)

```python
with h.create_file(rel_path, amd=amd, mmd=mmd, fs=self.fs, db=self.db) as f:
  pd.save(f.remote_url)

# also possible:
h.upload(local_file, rel_path, mmd=mmd, amd=amd, fs=self.fs,db=self.db)
```

- AMD = tracker.get_amd()
- prefix = fs.define_prefix(amd)
- remote_url = fs.define_remote_url(prefix, rel_path)
- yield File(fs, remote_url, self.based_on)
- f.get_hash_and_size()
- db.insert(FileInfo)

get file (id, fs, db)

- FileInfo = db.load_file(file_id)
- while FileInfo.deduplicated_by is not None:
  - FileInfo = db.load_file(FileInfo.deduplicated_by)
- File = fs.load(FileInfo, fs)

deduplicate

- ids_per_hash = db.get_duplicate_files() -> dict[str,str]
-

# User story Artifact

class ArtifactInfo

- remote_url
- AMD
- MMD
- files: dict[str,id]

class Artifact(ArtifactInfo)

- files: defaultdict[str,File]

save artifact

```python
with h.create_artifact(fs=self.fs) as a:
  pd.save(a.file["foo.txt"].remote_url)
```

- AMD = tracker.get_amd()
- prefix = fs.define_prefix(amd)
- remote_url = fs.define_remote_url(prefix, "")
- yield Artifact(remote_url)
- via defaultdict
  - yield File(fs.define_remote_url(prefix,rel))
- f.get_hash_and_size()
- db.insert(FileInfo)
- db.insert(ArtifactInfo)

load artifact (id, fs, db)

- ArtifactInfo = db.load_artifact(id)
- Artifact(ArtifactInfo, )
- for k, file_id in ArtifactInfo.files.items():
  - File = get_file(file_id, fs)
  - Artifact.files[k] = File
- return Artifact

# Old

class (New)Artifact

- files: CustomDefaultDict[str, File] or dict[str, File]
- metadata

create new artifacts

- with h.create() as artifact -> NewArtifact
  - a.new_file(...)
  - artifact.file["train.txt"].remote_url
  - artifact.file["test.txt"].write_text()
  - artifact.file["test.txt"].download()

get artifact

- artifact = h.load(artifact_id)

# User story

class AutomaticMetadata

class ManualMetadata

class Storer

- define_remote_url(AutomaticMetadata)
- exists(remote_url)
- hash(remote_url)
- download(remote_url, local_path)
- upload(local_path, remote_url)
- open(remote_url)

class File

- storer
- file_id
- remote_url (should always be unique!!!)
- file_hash
- relpath (do I still need this?! on the other hand, why not...)
- remote_dirpath
- duplicate_of = newer_file_id
- forward_reference
- file_size = "unknown" (if with new)
- methods
  - deduplicate()

class Artifact

- artifact_id
- files: Dict[relpath, File]
- automatic_metadata
- manual_metadata
- fsspec_kwargs ?! Not sure if duplicated...
- method
  - remote_url() -> only custom thing! #
  - upload(localpath_per_remoterelpath)
  - replace_files(...)

class DB

- methods
  - save_file(File)
  - load_file(id, storer) -> File
  - search_file(dct) -> df.DataFrame
  - save_artifact(Artifact) # one table for artifacts, one table for files
  - load_artifact(id, storer) -> Artifact
  - search_artifact(dct) -> df.DataFrame

class Tracker

- track() -> AutomaticMetadata

---

create new files

- h = eio.Handler(fsspec_kwargs, `Tracker`, `db`, `Storer`)
- with h.new(relpaths, ManualMetadata)...
  - AutomaticMetadata = `Tracker`.create()
  - artifact = `Artifact`(relpaths, MMD, AMD, Storer)
  - yield artifact
  - artifact.calculate_file_size_and_hash()
  - db.save(artifact)

save local files

- artifact = h.upload_local_file(filepaths, ManualMetadata)...
  - artifact = Artifact(relpaths, MMD, AMD, Storer)
  - artifact.upload(localpath_per_relpath)
  - artifact.calculate_file_size_and_hash()
  - db.save(artifact)

search

- h.db.search_artifact()
- h.db.search_file()

get(artifact_id)

- artifact = h.db.load(artifact_id)
- artifact.file().download()
- artifact.file().open()
- artifact.file().remote_url

replace duplicate files

- db.get_duplicate_file_ids() -> dict[hash, list[str]]
- file = db.load_file(id_to_replace)
- file.deduplicate(new_id)

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
