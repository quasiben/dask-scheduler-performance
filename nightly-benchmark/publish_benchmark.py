import os
from datetime import datetime

from github import Github

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])

operations = ['simple', 'shuffle', 'rand-access']

today = datetime.now().strftime("%Y%m%d")

fname_hist = today + "-benchmark-history.png"
hist_path = fname_hist

d = "."
with open(os.path.join(d, "raw_data.txt")) as f:
    raw_data = f.read()

repo = g.get_repo("quasiben/dask-scheduler-performance")

print("Uploading HTML Profiles...")

for op in operations:
    profile_name = f"{today}-{op}-scheduler.html"
    profile_path = os.path.join(d, profile_name)

    repo.create_file(
        path=f"assets/{profile_name}",
        message=f"dask {op} profile {today}",
        content=open(f"{profile_path}", "rb").read(),
        branch="benchmark-images",
    )

print("Uploading images...")
print(f"\t{fname_hist}")

repo.create_file(
    path=f"assets/{fname_hist}",
    message=f"historical benchmark image {today}",
    content=open(f"{hist_path}", "rb").read(),
    branch="benchmark-images",
)

print("Creating Issue...")
template = f"""
## Historical Throughput
<img width="641" alt="Benchmark Image"
src="https://raw.githubusercontent.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{fname_hist}">

## Raw Data
{raw_data}

## Dask Profile

- [Shuffle
 Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-shuffle-scheduler.html)
- [Random Access
  Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-rand-access-scheduler.html)
- [Simple
  Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-simple-scheduler.html)
"""

repo.create_issue(title=f"Nightly Benchmark run {today}", body=template)
