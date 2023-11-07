# More Functional features

## include pandas

```python
with eio.create(rel_paths="", ...) as artifact:
  df.to_csv(artifact.file.uri)
  df2.to_csv(artifact.files["foo.bar"].uri)

  # only write metadata now!
  # maybe even delete existing ones?
```

```python
import elliptio as eio

eio = elliptio.Handler(
  # local requires ROOT_PATH
  # aws requires credentials, s3_bucket_name
  file_handler=["local","aws"]
  ...
  # URI is with username and password, so need nothing else
  monogodb_uri="mongodb://localhost:27017",
)
eio.based_on
artifact = eio.upload(["foo.txt","bar.md"])

# CHECK: Does autocompletion work in e.g. JupyterLab? -> yes
artifact = eio.get(id=...)
artifact.metadata
local_path = artifact.files["subdir/foo.txt"].download("foo.txt")
some_bytes = artifact.file.get_bytes()
artifact.file.uri
artifact.logs["..."]
```

## File handlers

- remote_urls_per_local_paths = define_remote_urls(local_paths)
- upload(local_path, remote_url)
- download(remote_url, local_path)
- sent_bytes(byte_stream, remote_url)
- fetch_bytes(remote_url)

AbstractFile

- properties
  - remote_uri
- upload(local_path)
- download(local_path)
- sent_bytes(byte_stream)
- fetch_bytes()

## classes

```python
@class Metadata:
  version: 0

  def dump():
    pass

def load_metadata_v0():
  ...



@dataclass
class Artifact:
  metadata: Metadata
  files: dict[str,File]
  logs: dict[str,File]

@dataclass
@class File:
  s3_url: ...

  def download():
    ...

  def get_bytes():
    ...

eio.collection.find().limit(3)

eio.load()
# default: load artifact metadata from mongodb
eio._load_from_mongodb()

# if id=s3-path to metadata (maybe rather artifact.yaml)??
eio._load_from_s3()
```

```python
file.hash
file.s3_url
file.download()
file.get_bytes()

# How to make it such that
artifact.id_
artifact.files.keys()
artifact.files["asdfs"].get_bytes()

# this works if there is only one file
artifact.file.download()
```

- For finding, simply return `eio.collection.find().limit(10)`

# FIXMEs

Things I know are poor, but won't fix now

## save

- metadata should be dataclass

## ETL

- terraform: password in parameter store should be encrypted
- lambda: currently each lambda setups its own `MongoClient`, which is very non-performant with high load
  - https://www.mongodb.com/docs/atlas/manage-connections-aws-lambda/
  - https://www.mongodb.com/docs/atlas/manage-connections-aws-lambda/#connection-example
- mongoDB is currently accessible from anywhere (0.0.0.0)
  - For M0 instance I likely need to setup a NAT
  - see https://github.com/AndrewGuenther/fck-nat
  - would cost around 3$/month
- lambda could return a better message
