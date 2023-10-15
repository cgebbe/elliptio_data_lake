# About

Elliptio is a small opinionated application (in python and terraform) which brings sanity to any data lake.

It is named after the Elliptio mussel genus which lives in freshwater lakes and is a food source for many species.

## Problem

Particular in data science you often find data lakes where...

- data cannot be reproduced
- data lineage is unknown
- data is accidentally modified
- data is duplicated
- data has a chaotic directory structure
- relevant metadata (e.g. data type, score, etc.) is missing

## Solution

Elliptio aims to solve these problems in the following way

- data cannot be reproduced
  - When saving files, things like libraries, git-hash, diff, system user, date, etc. are automatically generated and saved as metadata
- data lineage is unknown
  - When using and saving files in one run, the saved filed is always linked to the used file.
- data is accidentally modified
  - Elliptio simply uses S3 object lock.
- data is duplicated
  - Duplicate files with the same hash are automatically removed.
- data has a chaotic directory structure
  - Elliptio simply saves files by date (by default). The ability to search files by metadata makes a directory structure much less important.
- relevant metadata (e.g. data type, score, etc.) is missing
  - Users can easily add any metadata when saving files

## High level architecture

<img src=README.assets/2023-10-15-19-55-53.png height=150>
