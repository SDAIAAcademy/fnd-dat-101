"""Run the lab sources as scripts, from labs/.

    uv run python _tools/run_all.py              # every source, strict: a wrong or blank answer fails
    uv run python _tools/run_all.py D1           # the sources whose name starts with D1
    uv run python _tools/run_all.py --record D1  # the trainer's tool: write data/reference/ from the solutions

Recording trusts the solutions, so _tools/crosscheck.py then compares the key references with
numbers the data generator computed in plain Python, without SQL.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
record = "--record" in args
prefixes = [a for a in args if not a.startswith("--")] or [""]
env = dict(os.environ, PYTHONIOENCODING="utf-8")
env["FNDDAT101_RECORD" if record else "FNDDAT101_STRICT"] = "1"
failed = []
for src in sorted((LABS / "_src").glob("*.py")):
    if not any(src.stem.startswith(p) for p in prefixes):
        continue
    r = subprocess.run([sys.executable, str(src.relative_to(LABS))], cwd=LABS, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    status = "ok" if r.returncode == 0 else "FAILED"
    print(f"{src.stem:34s} {status}")
    if r.returncode:
        failed.append(src.stem)
        print(r.stdout[-1500:], r.stderr[-2500:])
print(f"{len(failed)} failed" if failed else "all ran")
sys.exit(1 if failed else 0)
