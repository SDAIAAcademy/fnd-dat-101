# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb==2.0.1"]
# ///
# %% [markdown]
# # Setup check
#
# Run every cell before Day 1. The notebook writes the grocery delivery company's six synthetic
# tables, builds the database file, checks the tables against the course's digest and runs one
# query. It ends with **setup ok**.

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/fnd-dat-101.git"
    if not Path("/content/fnd-dat-101").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/fnd-dat-101"], check=True)
    os.chdir("/content/fnd-dat-101/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("_tools").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())

# %%
import duckdb, sqlite3
print("duckdb", duckdb.__version__, "· sqlite", sqlite3.sqlite_version, "· python", sys.version.split()[0])
import sqllab as U
con = U.db()
names = [r[0] for r in U.rows("SELECT table_name FROM duckdb_tables() ORDER BY table_name", con)]
print(names)
assert {"stores", "products", "customers", "orders", "order_lines", "deliveries"} <= set(names)
U.show("SELECT COUNT(*) AS order_lines FROM order_lines", con)
print("setup ok")
