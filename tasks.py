from invoke import task


@task
def rm_s3(c):
    c.run("aws s3 rm --recursive s3://elliptio-561130499334/")


@task
def ls_s3(c):
    c.run("aws s3 ls --recursive s3://elliptio-561130499334/")


@task
def lint(c):
    c.run("pre-commit run --all-files", pty=True)

    # create .env.example, see https://github.com/motdotla/dotenv/issues/119
    # Alternatively, use `dotenv.dotenv_values()->dict`
    c.run("sed 's/=.*/=/' .env > .env.example")

    # create `requirements.txt` and lock file (not sure about naming)
    c.run("pipreqs --mode no-pin --savepath requirements.txt src/")
    c.run("pip freeze --verbose > requirements.lock")
