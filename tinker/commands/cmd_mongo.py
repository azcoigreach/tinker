import click
from tinker.cli import pass_environment


@click.group()
@pass_environment
def cli(ctx):
    """Shows file changes in the current working directory."""
    ctx.log("Changed files: none")
    ctx.vlog("bla bla bla, debug info")


@cli.command("server", short_help="Start Mongodb Server")
@pass_environment
def server(ctx):
    '''Mongodb Server commands'''
    ctx.log("Starting Mongodb Server")


@cli.command("query", short_help="Query Mongodb Server")
@pass_environment
def query(ctx):
    '''Mongodb Server commands'''
    ctx.log("Mongodb Query Command Group")
