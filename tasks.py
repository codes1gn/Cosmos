import json
import os
import shutil
import sys
from functools import wraps

from invoke import task

# Get the current Python version
CURRENT_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

#################################################################################
####  Cosmos Setup  ####
#################################################################################


def get_venv_name():
    """
    Generate the virtual environment name based on the Python version.
    """
    return f"~/.venv/sandbox_py{CURRENT_PYTHON_VERSION.replace('.', '')}"


def is_venv_active():
    """
    Check if a virtual environment is active.
    """
    return os.environ.get("VIRTUAL_ENV") is not None


def get_activate_cmd(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Print instructions to activate the virtual environment in the current shell.
    """
    venv_name = get_venv_name()
    activate_script = "bin/activate" if os.name != "nt" else "Scripts/activate"
    activate_path = os.path.join(venv_name, activate_script)

    # Optional: Prompt the user to run the command
    print(f"Activating virtualenv: source {activate_path}")
    return f"source {activate_path}"


def with_venv(func):
    """
    Decorator to ensure the task runs in a virtual environment.
    """

    @wraps(func)
    def wrapper(ctx, *args, **kwargs):
        if not is_venv_active():
            activate_cmd = get_activate_cmd(ctx)
            with ctx.prefix(activate_cmd):
                return func(ctx, *args, **kwargs)

    return wrapper


def load_config():
    """Load project configuration from config.json."""
    with open("repositories.json", "r") as f:
        config = json.load(f)
    return config["projects"]


@task
def create_env(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Create a virtual environment.
    """
    # Create virtualenv
    venv_name = get_venv_name()
    ctx.run(f"python{python_version} -m venv {venv_name}")
    print(f"Virtualenv '{venv_name}' created.")


@task(pre=[create_env])
@with_venv
def configure_poetry(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Install Poetry and configure it to automatically accept licenses.
    """
    # Install Poetry
    ctx.run(f"python{python_version} -m pip install poetry")
    # Configure Poetry to automatically accept licenses
    ctx.run("poetry config virtualenvs.create false")
    print("Poetry installed and configured to automatically accept licenses.")


@task(pre=[create_env, configure_poetry])
@with_venv
def install_deps(ctx):
    """
    Install project dependencies using Poetry.
    """
    # Install dependencies
    ctx.run("poetry install --no-root")
    print("Project dependencies installed.")


# First entry for easy-to-start
@task(pre=[create_env, configure_poetry, install_deps])
def bootstrap(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Run all bootstrap tasks: create virtualenv, configure Poetry, and install dependencies.
    """
    pass


#################################################################################
####  Cosmos Utils  ####
#################################################################################


@task
@with_venv
def format(ctx):
    """
    Format the code using black and isort.
    """
    venv_name = get_venv_name()
    activate_cmd = get_activate_cmd(ctx)

    # excluding rule weirdly fails with decorator here, use ctx.prefix to workaround
    with ctx.cd("."):
        print("Formatting code...")
        ctx.run("black .")
        ctx.run("isort .")


@task
def clean(ctx):
    """
    Clean up the virtual environment and temporary files.
    """
    venv_name = get_venv_name()
    print("Cleaning up...")

    # Remove virtual environment
    if os.path.exists(venv_name):
        shutil.rmtree(venv_name)
        print(f"Removed virtual environment '{venv_name}'.")

    # Remove other temporary files
    temp_files = ["build", "dist", "*.egg-info", "__pycache__", "*.pyc"]
    for pattern in temp_files:
        ctx.run(f"rm -rf {pattern}")
        print(f"Removed {pattern}.")


@task
def group_commit(ctx, m):
    """
    Perform git add, git commit, and git push for Cosmos and quark subdirectory.
    Usage: inv group-commit -m="<your_message>"
    """
    # Define directories
    cosmos_dir = "."
    subprojects = load_config()

    # Perform git operations for Cosmos
    print("Committing changes in Cosmos...")
    with ctx.cd(cosmos_dir):
        ctx.run("git add .")
        ctx.run(f'git commit -m "{m}"')
        ctx.run("git push")

    # Perform git operations for subprojects
    for project in projects:
        project_name = project["name"]
        project_dir = os.path.join(".", project_name)

        print(f"Committing changes in {project_name}...")
        with ctx.cd(project_dir):
            ctx.run("git add .")
            ctx.run(f'git commit -m "{m}"')
            ctx.run("git push")

    print("Group commit and push completed successfully!")


#################################################################################
####  Quark  ####
#################################################################################


@task
def pull_quark(ctx):
    """
    Clone the Quark repository.
    """
    if not os.path.exists("Quark"):
        ctx.run("git clone git@github.com:codes1gn/Quark.git")
        print("Quark project cloned.")
    else:
        print("Quark project already exists.")


@task
@with_venv
def build_quark(ctx):
    """
    Build the Quark project using Poetry, ensuring no new virtualenv is created.
    """
    with ctx.cd("Quark"):
        ctx.run("poetry install --no-venv")
        print("Quark project built.")


@task
@with_venv
def test_quark(ctx):
    """
    Run tests for the Quark project.
    """
    with ctx.cd("Quark"):
        ctx.run("poetry run pytest")
        print("Quark tests completed.")


@task
def all(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Execute all tasks: bootstrap (create virtualenv, configure Poetry, install dependencies),
    pull Quark, build Quark, and run tests.
    """
    bootstrap(ctx, python_version=python_version)
    pull_quark(ctx)
    build_quark(ctx)
    test_quark(ctx)
