import os
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again with 'sudo'. Exiting.")

import asyncclick as click
# import click
import coloredlogs, logging

import digitalio
import board
from adafruit_rgb_display import st7789

from PIL import Image, ImageDraw, ImageFont

CONTEXT_SETTINGS = dict(auto_envvar_prefix="TINKER")

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

# Configuration for CS and DC pins for Raspberry Pi
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
BAUDRATE = 64000000  # The pi can be very fast!
# Create the ST7789 display:
display = st7789.ST7789(
    board.SPI(),
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    rotation=270, # Landscape orientation
    x_offset=53,
    y_offset=40,
)

# Setup buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)

class Environment:
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        logger.info(msg)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            logger.debug(msg, *args)

    def display_image(self, image):
        """Displays an image on the miniPiTFT display."""

        # Convert the image to RGB format and get the pixel data
        image = image.convert("RGB")

        # Display the image on the screen
        self.display.image(image)

    def load_menus(self):
        """Loads the menus from the configs folder."""
        menus = []
        for filename in os.path.abspath(os.path.join(os.path.dirname(__file__), "configs")):
            if filename.endswith(".json"):
                menus.append(filename[:-5])
        return menus

    


pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))
font_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts"))


class TinkerCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"tinker.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=TinkerCLI, context_settings=CONTEXT_SETTINGS)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_environment
async def cli(ctx, verbose):
    """Tinker Server command line interface."""
    ctx.verbose = verbose
    ctx.display = display
    ctx.buttonA = buttonA
    ctx.buttonB = buttonB
    ctx.vlog("Display Width: %s Height: %s Rotation: %s", ctx.display.width, ctx.display.height, ctx.display.rotation)
    ctx.font_folder = font_folder
    # Default font
    ctx.default_font = ImageFont.truetype(os.path.join(font_folder, "retro_gaming.ttf"), 20)
