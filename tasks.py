from invoke import task


@task
def rm_s3(c):
    c.run("aws s3 rm --recursive s3://elliptio-561130499334/")


@task
def ls_s3(c):
    c.run("aws s3 ls --recursive s3://elliptio-561130499334/")


@task
def check(c):
    c.run("pre-commit run --all-files", pty=True)
    c.run("pipreqs --mode no-pin --savepath requirements.txt src/")
    c.run("pip freeze --verbose > requirements.lock")
