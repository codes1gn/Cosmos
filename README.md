# Cosmos
Computing Optimisation Experiments Workspace

Cosmos is an automated workspace that orchestrate, manage your research work without suffering from virtual environments, dependencies, benchmarking, and many other stuffs.

You can keep tracking your experiments on many workloads (operators, subgraphs, models), platforms (tensorflow, pytorch, iree, tvm, and your own work), devices (GPU, CPU, ...) and
apply uniform visualisation, analysis, summary to all the experiments records.

At its core, Cosmos requires another repo called Quark, it provides query-based experiment tasks arrangement tools. you can define, collect all parts of experiments (task declare, data, model, workload, result) with config file. You can do anything on them based on query, which is widely known as configuration-based system, and widely used in many complex system.

## Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Invoke (for task automation): you can install by python-pip

Details can be found in pyproject.toml

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cosmos.git
   cd cosmos
   inv bootstrap
   ```
