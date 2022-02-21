import click
from tinker.cli import pass_environment

@click.group()
@pass_environment
def cli(ctx):
    '''Function calls'''
    ctx.log('Function cli')

@cli.command('func_test', short_help='Function Test')
@pass_environment
def func_test(ctx):
    '''Simple function test'''
    ctx.log(click.style('func_test executed',fg='red'))