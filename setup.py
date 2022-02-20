from setuptools import setup

# apt-get install fonts-dejavu python3-numpy python3-pil

setup(
    name="tinker",
    version="0.1",
    author="AZcoigreach",
    author_email="azcoigreach@gmail.com",
    packages=["tinker", "tinker.commands", "tinker.commands.configs"],
    include_package_data=True,
    install_requires=[
        "click",
        "coloredlogs",
        "colorama",
        "pymongo",
        "adafruit-circuitpython-rgb-display",
        ],
    entry_points="""
        [console_scripts]
        tinker=tinker.cli:cli
    """,
)
