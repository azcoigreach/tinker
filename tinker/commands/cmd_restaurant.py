import click
from tinker.cli import pass_environment

@click.group()
@pass_environment
def cli(ctx):
    '''Restaurant cli'''
    ctx.log('Restaurant cli')

@cli.group()
@pass_environment
def lunch(ctx):
    '''Lunch Menu'''
    ctx.log(click.style('Lunch Menu',fg='yellow'))

@cli.group()
@pass_environment
def dinner(ctx):
    '''Dinner Menu'''
    ctx.log(click.style('Dinner Menu',fg='yellow'))

@click.command()
@pass_environment
def burger(ctx):
    ctx.log(click.style('Enjoy your burger!',fg='cyan'))

lunch.add_command(burger)
dinner.add_command(burger)