from tinker.cli import pass_environment

# import sys
import os
import time
import math
import click
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from colorsys import hsv_to_rgb
# import digitalio



@click.command()
@pass_environment
def cli(env):
    env.display.rotation = 270
    if env.display.rotation % 180 == 90:
        height = env.display.width  # we swap height/width to rotate it to landscape!
        width = env.display.height
    else:
        width = env.display.width  # we swap height/width to rotate it to landscape!
        height = env.display.height

    # Create a new image with a black background
    img = Image.new("RGB", (width, height), (0, 0, 0))    
    env.vlog(f"Image width: {img.width} height: {img.height}")

    # Define the gradient colors
    num_colors = 256
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1, 1)]
        colors.append((r, g, b))

    # Initialize the first frame of the animation
    prev_row = np.random.randint(num_colors, size=width)
    draw = ImageDraw.Draw(img)
    
    # Set up the font
    font = env.default_font
    text = "FPS: 00"
    text_width, text_height = draw.textsize(text, font)

    # Calculate the position of the FPS indicator
    text_x = width - text_width
    text_y = 0

    # Draw the static text onto the image
    draw.text((0, 0), f"Width: {width}", (255, 255, 255), font=font)
    draw.text((0, text_height), f"Height: {height}", (255, 255, 255), font=font)
    draw.text((text_x, text_y), text, (255, 255, 255), font=font)

    # Display the initial frame on the screen
    env.display_image(img)

    # Start the loop to animate the image
    start_time = time.monotonic()
    fps = 0
    while True:
        # Check for button 1 press
        if not env.buttonA.value:
            env.vlog("Button A pressed")
            break
        # Generate the next row of the animation
        row = np.random.randint(num_colors, size=width)
        for y in range(height):
            for x in range(width-1):
                # Calculate the gradient between the current pixel and the next pixel
                color1 = colors[row[x]]
                color2 = colors[row[x+1]]
                gradient = [(color1[i] + color2[i]) // 2 for i in range(3)]
                
                # Draw a horizontal line from the previous pixel to the current pixel
                draw.line((x, y, x+1, y), fill=tuple(gradient))
        
        # Draw the FPS indicator
        frame_time = time.monotonic() - start_time
        fps = int(1 / frame_time)
        text = f"FPS: {fps}"
        draw.text((text_x, text_y), text, (255, 255, 255), font=font)

        # Display the updated image on the screen
        env.display_image(img)

        # Sleep for a short time to limit the frame rate
        time.sleep(1 / 60)  # Max 60 FPS