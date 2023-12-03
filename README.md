- [About](#about)
- [Problems and solution approach](#problems-and-solution-approach)
- [FAQ](#faq)
  - [How to use](#how-to-use)
  - [How to install](#how-to-install)
- [Further considerations](#further-considerations)
  - [Alternatives](#alternatives)
  - [Licensing](#licensing)
  - [Cost](#cost)
  - [TODOs](#todos)

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

# FAQ

## How to use

Please find an exemplary user story in [docs/user_story.ipynb](docs/user_story.ipynb). It explains the following features

- saving files
- finding files via metadata
- using files
- reproducing files
- finding files via lineage

## How to install

Elliptio is not yet published to pypi, so simply `git clone` and `pip install -e .` it. Elliptio requires two things:

- MongoDB database
- File storage interface. Currently there are two concrete implementations:
  - S3File
  - LocalFile

Their configuration parameters need to be specified in the `.env` file (see [.env.example](.env.example)).

You can setup the database and file storage any way you like: The simplest way is likely to run MongoDB community edition as a Docker container and use the `LocalFile` interface. To setup a MongoDB Atlas Database on AWS as well as an AWS S3 bucket, run `cd terraform/aws && terraform apply`.

Optionally, you can run [Metabase](https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker) to create dashboards and a GUI for browsing the database.

# Further considerations

## Alternatives

Object stores such as S3 or Ceph already provide the option to store metadata. However, this does not cover all required data for reproducibility. Also, querying metadata is not as efficient as querying a database.

Weights and Biases is an amazing python library, from which a lot of inspiration is drawn. It also offers the option to search and filter run- and artifact- tables. However, it can be rather expensive and focuses on a lot more things than just data storage.

## Licensing

MongoDB is licenced under the "Server Side Public License". This prohibits "selling" MongoDB as a service, but you can use it as database, see https://www.mongodb.com/licensing/server-side-public-license/faq

> What are the implications of this new license on applications built using MongoDB and made available as a service (SaaS)? The copyleft condition of Section 13 of the SSPL applies only when you are offering the functionality of MongoDB, or modified versions of MongoDB, to third parties as a service. _There is no copyleft condition for other SaaS applications that use MongoDB as a database._

Metabase, without the enterprise features, is APGL licensed. You have to be careful when modifying the code or incorporating it into your application, but running the app without modifications internally in "vanilla mode" seems to be fine [according to them](https://discourse.metabase.com/t/licensing-and-agpl-implicaitons-in-different-usage-scenarios/3115/5):

> Our posture is a little different if you’re trying to embed our entire interface in your application, modify the actual program itself, etc. The situations you describe are standard vanilla modes of operation that we definitely don’t want to encumber in any way.

## Cost

- MongoDB Atlas has a free option for databases up to 512 MB
- Metabase itself is free if self-hosted (and used for internal purposes according to its license)

## TODOs

- Use ![fsspec](https://github.com/fsspec) as file system interface
- automatically log git-hash and `git diff`
- Publish elliptio to pypi
- tests for different filesystems
