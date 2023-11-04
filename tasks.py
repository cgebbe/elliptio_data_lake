from invoke import task


@task
def export_requirements(c):
    c.run("pipreqs --mode no-pin --savepath requirements.txt src/")
    c.run("pip freeze --verbose > requirements.lock")


@task
def list_bucket(c):
    # Note: to empty bucket, replace ls with rm
    c.run("aws s3 ls --recursive s3://elliptio-561130499334/")
