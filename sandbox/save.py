# %%
from pathlib import Path
from pprint import pprint

import dotenv
import elliptio as eio
import git

repo = git.Repo(Path(__file__), search_parent_directories=True)
repo_path = Path(repo.working_tree_dir)
paths = [p for p in repo_path.glob("sandbox/test_data/**/*") if p.is_file()]
paths

# %%%
dotenv.load_dotenv()

artifact = eio.save(paths)

# %%

print("saved artifact:")
pprint(artifact)

# %%
