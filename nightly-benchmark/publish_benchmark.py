import os
from datetime import datetime

from github import Github

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])

operations = ['simple', 'shuffle', 'rand-access']

today = datetime.now().strftime("%Y%m%d")

fname_hist = today + "-benchmark-history.png"
hist_path = fname_hist

if os.path.exists('/etc/dgx-release'):
    with open("dgx_raw_data.txt") as f:
        raw_data = f.read()
else:
    with open("raw_data.txt") as f:
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

## Dask Profiles

- [Shuffle
 Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-shuffle-scheduler.html)
- [Random Access
  Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-rand-access-scheduler.html)
- [Simple
  Profile](https://raw.githack.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{today}-simple-scheduler.html)

"""

issue_name = f"Nightly Benchmark run {today}"
if os.path.exists('/etc/dgx-release'):
    issue_name = "DGX " + issue_name
    sched_graph = f"{today}-sched-graph.png"
    client_graph = f"{today}-client-graph.png"
    for p in [sched_graph, client_graph]:
        repo.create_file(
                path=f"assets/{p}",
                message=f"{p} image {today}",
                content=open(f"{p}", "rb").read(),
                branch="benchmark-images",
        )
    GRAPH_IMAGES = """
## Scheduler Execution Graph
<img width="641" alt="Sched Graph Image"
src="https://raw.githubusercontent.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{sched_graph}">


## Client Execution Graph
<img width="641" alt="Client Graph Image"
src="https://raw.githubusercontent.com/quasiben/dask-scheduler-performance/benchmark-images/assets/{client_graph}">
"""


repo.create_issue(title=issue_name, body=template)
