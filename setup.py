from setuptools import setup

# apt-get install fonts-dejavu python3-numpy python3-pil

setup(
    name="tinker",
    version="0.1",
    author="AZcoigreach",
    author_email="azcoigreach@gmail.com",
    packages=["tinker", "tinker.commands", "tinker.configs"],
    include_package_data=True,
    install_requires=[
        "click",
        "coloredlogs",
        "pymongo",
        "adafruit-circuitpython-rgb-display",
        "adafruit-circuitpython-debouncer",
        "numpy",
        "psutil",
        "ifaddr",
        "speedtest-cli",
        "asyncclick",
        "Pillow",
        "anyio",
        "RPI.GPIO",
        "aiohttp",
        "aiofiles",
        ],
    entry_points="""
        [console_scripts]
        tinker=tinker.cli:cli
    """,
)
