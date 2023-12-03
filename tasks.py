import os
from pathlib import Path

import papermill as pm
from invoke import task


@task
def rm_s3(c):
    s3_bucket_url = _get_s3_bucket_url()
    c.run(f"aws s3 rm --recursive {s3_bucket_url}")


@task
def ls_s3(c):
    s3_bucket_url = _get_s3_bucket_url()
    c.run(f"aws s3 ls --recursive {s3_bucket_url}")


@task
def lint(c):
    c.run("pre-commit run --all-files", pty=True)

    # NOTE: Don't run mypy in precommit to use local venv
    c.run("mypy src")

    # create .env.example, see https://github.com/motdotla/dotenv/issues/119
    # Alternatively, use `dotenv.dotenv_values()->dict`
    c.run("sed 's/=.*/=/' .env > .env.example")

    # create `requirements.txt` and lock file (not sure about naming)
    c.run("pipreqs --mode no-pin --savepath requirements.txt src/")
    c.run("pip freeze --verbose > requirements.lock")
    c.run("python --version > .python-version")


@task
def docs(c):
    del c
    nb_path = Path(__file__).parent / "docs/user_story.ipynb"
    pm.execute_notebook(input_path=nb_path, output_path=None)


def _get_s3_bucket_url():
    bucket_name = os.environ["ELLIPTIO_S3_BUCKET_NAME"]
    return f"s3://{bucket_name}/"
