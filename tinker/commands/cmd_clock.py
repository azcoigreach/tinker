import os
import time
import click
from tinker.cli import pass_environment

from PIL import Image, ImageDraw, ImageFont

@click.command()
@pass_environment
def cli(env):
    # Set the display rotation
    env.display.rotation = 270
    if env.display.rotation % 180 == 90:
        height = env.display.width  # we swap height/width to rotate it to landscape!
        width = env.display.height
    else:
        width = env.display.width  # we swap height/width to rotate it to landscape!
        height = env.display.height

    # Define the font and text for the clock
    clock_font = env.default_font
    clock_text = ""

    # Define the font and text for the date
    date_font = ImageFont.truetype(os.path.join(env.font_folder, "retro_gaming.ttf"), 12)
    date_text = ""

    # Display the initial clock and date on the screen
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    env.display_image(img)

    # Start the loop to update the clock and date
    while True:
        # Clear the image
        draw.rectangle((0, 0, width, height), (0, 0, 0))

        # Get the current time and date
        now = time.localtime()
        clock_text = time.strftime("%H:%M:%S", now)
        date_text = time.strftime("%a %d %b %Y", now)

        # Draw the clock and date onto the image
        draw.text((10, 10), clock_text, (255, 255, 255), font=clock_font)
        draw.text((width / 2 - 60, height / 2 - 10), date_text, (255, 255, 255), font=date_font)

        # Display the updated image on the screen
        env.display_image(img)

        # Check if button A has been pressed
        if not env.buttonA.value:
            break

        # Sleep for a short time to limit the update rate
        time.sleep(0.1)
