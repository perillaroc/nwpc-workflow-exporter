# coding: utf-8
import click
from workflow_exporter.node_status import node_status as node_status_command


@click.group()
def cli():
    pass


cli.add_command(node_status_command)


if __name__ == "__main__":
    cli()
