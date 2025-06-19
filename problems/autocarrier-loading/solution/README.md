To test the functionality you can just run:

```bash
python main.py <instance_file> 
<solution_file>
```
you can run the script with both instance and solution files as arguments:

```bash
python main.py <instance_file> <solution_file>
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
5. Run the script with the instance:

```bash
pypy main.py <instance_file>
```