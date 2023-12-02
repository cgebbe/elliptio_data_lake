# %%
from pathlib import Path
from pprint import pprint

import dotenv
import elliptio as eio
import git
from elliptio.filetypes import LocalFile

repo = git.Repo(Path(__file__), search_parent_directories=True)
repo_path = Path(repo.working_tree_dir)
paths = [p for p in repo_path.glob("sandbox/test_data/**/*") if p.is_file()]
print(paths)

# %%%
dotenv.load_dotenv()

use_local = True
handler = eio.Handler(
    remote_file_cls=LocalFile,
)

# %%
artifact = handler.upload(
    local_paths=paths,
)

print("saved artifact:")
pprint(artifact)

# %%

print(artifact.files["a.txt"])
