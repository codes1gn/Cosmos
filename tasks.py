from invoke import task
from functools import wraps
import os
import sys

# Get the current Python version
CURRENT_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
SANDBOX_PATH = ""

def is_venv_active():
    """
    Check if a virtual environment is active.
    """
    return os.environ.get("VIRTUAL_ENV") is not None

def get_activate_cmd(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Print instructions to activate the virtual environment in the current shell.
    """
    venv_name = f"sandbox_py{python_version.replace('.', '')}"
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

@task
def create_env(ctx, python_version=CURRENT_PYTHON_VERSION):
    """
    Create a virtual environment.
    """
    # Create virtualenv
    venv_name = f"sandbox_py{python_version.replace('.', '')}"
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

@task
@with_venv
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
def build_quark(ctx):
    """
    Build the Quark project using Poetry, ensuring no new virtualenv is created.
    """
    with ctx.cd("Quark"):
        ctx.run("poetry install --no-venv")
        print("Quark project built.")

@task
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
