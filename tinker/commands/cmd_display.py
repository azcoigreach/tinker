import click
from tinker.cli import pass_environment
from tinker.cli import get_menu_items
import digitalio
import board
from adafruit_rgb_display.rgb import color565
from adafruit_rgb_display import st7789
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time
# from .. import menus

# from . import fonts


@click.group()
@pass_environment
def cli(ctx):
    """Manage Display and Buttons"""
    ctx.log("Starting Display")
    
    # Configuration for CS and DC pins for Raspberry Pi
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = None
    BAUDRATE = 64000000  # The pi can be very fast!
    # Create the ST7789 display:
    ctx.display = st7789.ST7789(
        board.SPI(),
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        baudrate=BAUDRATE,
        width=135,
        height=240,
        x_offset=53,
        y_offset=40,
    )

    # Set rotation to 90 degrees
    ctx.display.rotation = 90
    if ctx.display.rotation % 180 == 90:
        ctx.height = ctx.display.width  # we swap height/width to rotate it to landscape!
        ctx.width = ctx.display.height
    else:
        ctx.width = ctx.display.width  # we swap height/width to rotate it to landscape!
        ctx.height = ctx.display.height

    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    ctx.image = Image.new("RGB", (ctx.width, ctx.height))

    # Create drawing object to draw on image.
    ctx.draw = ImageDraw.Draw(ctx.image)

    # Setup backlight
    ctx.backlight = digitalio.DigitalInOut(board.D22)
    ctx.backlight.switch_to_output()
    ctx.backlight.value = True

    # Setup buttons
    ctx.buttonA = digitalio.DigitalInOut(board.D23)
    ctx.buttonB = digitalio.DigitalInOut(board.D24)
    ctx.buttonA.switch_to_input(digitalio.Pull.UP)
    ctx.buttonB.switch_to_input(digitalio.Pull.UP)
    
    # Set Font
    # Load a TTF font.  Make sure the .ttf font file is in the
    # same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php

    ctx.font = ImageFont.truetype("/home/pi/tinker/tinker/fonts/retro_gaming.ttf", 24)

    # Context x and padding
    ctx.x = 0
    ctx.padding = -2

@cli.command("menus", short_help="Menu template")
@pass_environment
def menus_template(ctx):
    '''Menu system controlled with button A and button B'''
    ctx.log("Starting menu system")
    
    # Draw a black filled box to clear the image.
    ctx.draw.rectangle((0, 0, ctx.width, ctx.height), outline=0, fill=0)
    # Display image.
    ctx.display.image(ctx.image)

    '''
    Create a menu system with 3 menus and 3 submenus 
    Using button A to go down and button B to enter a submenu
    There will be an arrow point down at the top-left of the screen, inlcude varibles for padding
    and an arrow pointing right at the bottom-left of the screen, include variables for padding
    with a line spanning from the top to bottom of the screen, seperating the text from the arrows, invlude variables for padding
    '''
    # Variable to keep track of which menu is selected
    ctx.menu_selected = 0
    # Variable to keep track of which submenu is selected
    ctx.submenu_selected = 0

    # # Import menu data from json file


    # Function for arrows and lines
    def arrows_lines():
        # Variables for arrows and lines
        # Arrow width
        arrow_width = 15
        # Arrow padding for top-left
        arrow_padding_top = 20
        # Arrow padding for bottom-left
        arrow_padding_bottom = 20
        # Arrow padding from left of screen
        arrow_padding_left = 5
        # Line padding
        line_padding = 30
        # Draw arrows
        # Top-left arrow, pointing down with padding from top, left and width
        ctx.draw.polygon([(arrow_padding_left, arrow_padding_top), (arrow_padding_left + arrow_width, arrow_padding_top), (arrow_padding_left + (arrow_width / 2), arrow_padding_top + arrow_width)], fill="white")
        # Bottom-left arrow, pointing right with padding from bottom, left and width
        ctx.draw.polygon([(arrow_padding_left, ctx.height - arrow_padding_bottom), (arrow_padding_left, ctx.height - arrow_padding_bottom - arrow_width), (arrow_padding_left + arrow_width, ctx.height - arrow_padding_bottom - (arrow_width / 2))], fill="white")
        # Draw line with padding from left of screen
        ctx.draw.line((line_padding, 0, line_padding, ctx.height), fill="white", width=2)

    # Function for menu text
    def menu_text(menu_line_1, menu_line_1_color, menu_line_2, menu_line_2_color, menu_line_3, menu_line_3_color, menu_line_4, menu_line_4_color):
        # Padding from left of screen
        menu_text_padding = 40
        # Menu Line 1 text
        menu_line_1 = menu_line_1
        # Menu Line 1 text padding from top of screen
        menu_line_1_padding = ctx.padding + 37
        # Menu Line 1 text color
        menu_line_1_color = menu_line_1_color
        # Menu Line 2 text
        menu_line_2 = menu_line_2
        # Menu Line 2 text padding from top of screen
        menu_line_2_padding = ctx.padding + 69
        # Menu Line 2 text color
        menu_line_2_color = menu_line_2_color
        # Menu Line 3 text
        menu_line_3 = menu_line_3
        # Menu Line 3 text padding from top of screen
        menu_line_3_padding = ctx.padding + 101
        # Menu Line 3 text color
        menu_line_3_color = menu_line_3_color
        # Menu Line 4 text
        menu_line_4 = menu_line_4
        # Menu Line 4 text padding from top of screen
        menu_line_4_padding = ctx.padding + 133
        # Menu Line 4 text color
        menu_line_4_color = menu_line_4_color
        # Draw menu line 1 text
        ctx.draw.text((menu_text_padding, menu_line_1_padding), menu_line_1, font=ctx.font, fill=menu_line_1_color)
        # Draw menu line 2 text
        ctx.draw.text((menu_text_padding, menu_line_2_padding), menu_line_2, font=ctx.font, fill=menu_line_2_color)
        # Draw menu line 3 text
        ctx.draw.text((menu_text_padding, menu_line_3_padding), menu_line_3, font=ctx.font, fill=menu_line_3_color)
        # Draw menu line 4 text
        ctx.draw.text((menu_text_padding, menu_line_4_padding), menu_line_4, font=ctx.font, fill=menu_line_4_color)

    # Function to get top level menu items from menu_system
    def populate_menus():
        '''
        Example Menu Item:
        {
            "menu_system": [
                {
                    "index": 0,
                    "name": "Menu 1",
                    "menu_position": "1",
                    "default_color": "white",
                    "selected_color": "red",
                    "function": {
                        "type": "sub_menu",
                        "args": ["1_1"]
                    }
                }
            ]
        }
        '''
        # read JSON file from menus
        ctx.log("Reading menu system")
        # retrieve menu data from menus.get_menu_items()
        ctx.menu_data = get_menu_items()
        # loop through menu data
        for menu in ctx.menu_data:
            # ctx.vlog menu elements for debugging
            # index of menu
            ctx.vlog("Menu Index: " + str(ctx.menu_data.index(menu)))
            # name of menu
            ctx.vlog("Menu Name: " + menu["name"])
            # menu position
            ctx.vlog("Menu Position: " + menu["menu_position"])
            # default color
            ctx.vlog("Menu Default Color: " + menu["default_color"])
            # selected color
            ctx.vlog("Menu Selected Color: " + menu["selected_color"])
            # function type
            ctx.vlog("Menu Function Type: " + menu["function"]["type"])
            # function args
            ctx.vlog("Menu Function Args: " + str(menu["function"]["args"]))

    populate_menus()


    while True:
        # Draw a black filled box to clear the image.
        ctx.draw.rectangle((0, 0, ctx.width, ctx.height), outline=0, fill=0)
        # Draw arrows and lines
        arrows_lines()
        # menu_text()

        # check for buttonA press only once and increment menu_selected
        if not ctx.buttonA.value:
            ctx.log("Button A pressed")
            ctx.menu_selected += 1
            if ctx.menu_selected > 3:
                ctx.menu_selected = 0
            ctx.log("Menu Selected: " + str(ctx.menu_selected))
            time.sleep(0.5)

        if ctx.buttonB.value:
            enter_pressed = False

        while not ctx.buttonB.value and enter_pressed:
            ctx.vlog("Button B pressed for more than 0.5s")
            time.sleep(1)
                # enter_pressed = False

        # check for buttonB press and select menu item
        if not ctx.buttonB.value:
            enter_pressed = True
            ctx.log("Button B pressed")
            ctx.log("Enter Menu: " + str(ctx.menu_selected))
            # if button still pressed after 0.5 seconds, ignore press with enter_pressed = False
            time.sleep(0.5)
            
        

        # Display image.
        ctx.display.image(ctx.image)
        time.sleep(0.1)

        