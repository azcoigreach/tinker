from tinker.cli import pass_context

import click


@click.command("init", short_help="Initializes a repo.")
@click.argument("path", required=False, type=click.Path(resolve_path=True))
@pass_context
def cli(ctx, path):
    """Initializes a repository."""
    if path is None:
        path = ctx.home
    ctx.log(f"Initialized the repository in {click.format_filename(path)}")
