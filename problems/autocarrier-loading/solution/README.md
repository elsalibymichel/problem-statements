To get a help about the functionality you can just run:

```bash
pypy main.py 
```
<solution_file>
```


```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Command line interface for the ACL problem.

Options:
  --help  Show this message and exit.

Commands:
  constructive-search  Run constructive search algorithms on the ACL...
  local-search         Run local search algorithms on the ACL problem.
```

## Setting up the pypy environment

To set up the pypy environment, you can use uv to create a virtual environment and install the required packages. Here are the steps:
1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows users, you can use the following command to install uv:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Create a new virtual environment using uv:

```bash
uv venv --python pypy3.11
```

3. Activate the virtual environment:
```bash
uv activate
``` 

4. Install the required packages:

```bash
uv pip install -r requirements.txt
```
5. Run the command line script

```bash
pypy main.py constructive-search <instance_file> 
```

or 

```bash
pypy main.py local-search first_improvement <instance_file> 
```