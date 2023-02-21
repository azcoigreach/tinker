import os
import json
from typing import List, Dict, Any

import asyncclick as click
from tinker.cli import pass_environment

from PIL import Image, ImageDraw, ImageFont

@click.command("menus")
@pass_environment
async def cli(ctx):
    """Displays the available menus."""

    # Load the menus from the JSON file
    menus = ctx.load_menus()

    # Define the fonts for the menus
    font_large = ImageFont.truetype(os.path.join(ctx.font_folder, "retro_gaming.ttf"), 32)
    font_small = ImageFont.truetype(os.path.join(ctx.font_folder, "retro_gaming.ttf"), 16)

    # Set the initial state
    page = 0
    selected_menu = 0
    selected_sub_menu = 0

    while True:
        # Clear the display
        img = Image.new("RGB", (ctx.display.width, ctx.display.height), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get the current menu and submenu
        current_menu = menus[page][selected_menu]
        current_sub_menu = current_menu.get("sub_menus", [])[selected_sub_menu] if current_menu.get("sub_menus") else None

        # Draw the title of the current menu
        draw.text((10, 0), current_menu["name"], current_menu.get("color", (255, 255, 255)), font=font_large)

        # Draw the options for the current menu
        y_pos = 40
        for i, option in enumerate(current_menu["options"]):
            color = option.get("color", (255, 255, 255))
            if i == selected_sub_menu:
                color = (0, 255, 0)
            draw.text((10, y_pos), option["name"], color, font=font_small)
            y_pos += 20

        # Draw the sub-menus if they exist
        if current_menu.get("sub_menus"):
            y_pos += 20
            for i, sub_menu in enumerate(current_menu["sub_menus"]):
                color = sub_menu.get("color", (255, 255, 255))
                if i == selected_sub_menu:
                    color = (0, 255, 0)
                draw.text((20, y_pos), sub_menu["name"], color, font=font_small)
                y_pos += 20

        # Display the image on the screen
        ctx.display_image(img)

        # Wait for button presses
        while True:
            # Check for button A press
            if not ctx.buttonA.value:
                # Check if there is a sub-menu to load
                if current_sub_menu:
                    cmd_name = current_sub_menu["command"]
                    command = ctx.get_command(cmd_name)
                    if command:
                        # Launch the selected command
                        ctx.vlog(f"Selected command: {cmd_name}")
                        await ctx.invoke(command)
                else:
                    cmd_name = current_menu["options"][selected_sub_menu]["command"]
                    command = ctx.get_command(cmd_name)
                    if command:
                        # Launch the selected command
                        ctx.vlog(f"Selected command: {cmd_name}")
                        await ctx.invoke(command)
                break

            # Check for button B press
            if not ctx.buttonB.value:
                if current_menu.get("sub_menus"):
                    # Switch to the next sub-menu
                    selected_sub_menu += 1
                    if selected_sub_menu >= len(current_menu["sub_menus"]):
                        selected_sub_menu = 0
                else:
                    # Switch to the next menu
                    selected_menu += 1
                    if selected_menu >= len(menus[page]):
                        selected_menu = 0
                break


