from invoke import Program
from .tasks import namespace

program = Program(namespace=namespace, name="cosmos")

if __name__ == "__main__":
    program.run()
