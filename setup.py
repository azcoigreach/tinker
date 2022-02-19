from setuptools import setup

setup(
    name="tinker",
    version="0.1",
    packages=["tinker", "tinker.commands"],
    include_package_data=True,
    install_requires=[
        "click",
        "coloredlogs"],
    entry_points="""
        [console_scripts]
        tinker=tinker.cli:cli
    """,
)
