import os
import time
import click
from tinker.cli import pass_environment

from PIL import Image, ImageDraw, ImageFont

import psutil
import ifaddr

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

    # Define the font for the stats
    font = ImageFont.truetype(os.path.join(env.font_folder, "retro_gaming.ttf"), 16)

    # Display the initial stats on the screen
    img = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    env.display_image(img)

    # Get a list of all network interfaces
    adapters = ifaddr.get_adapters()

    # Find the eth0 and wlan0 interfaces
    usb0 = None
    wlan0 = None
    for adapter in adapters:
        if adapter.nice_name == 'usb0':
            usb0 = adapter
        elif adapter.nice_name == 'wlan0':
            wlan0 = adapter

    # Start the loop to update the stats
    while True:
        # Clear the image
        draw.rectangle((0, 0, width, height), (0, 0, 0))

        # Get the system stats
        # Print the IP addresses for each interface
        if usb0 is not None:
            for ip in usb0.ips:
                if ip.is_IPv4:
                    draw.text((10, 10), f"usb0: {ip.ip}", (255, 255, 255), font=font)
        if wlan0 is not None:
            for ip in wlan0.ips:
                if ip.is_IPv4:
                    draw.text((10, 30), f"wlan0: {ip.ip}", (255, 255, 255), font=font)
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        disk_usage = os.popen('df -h / | awk \'NR==2{printf "DISK: %d/%dGB %s", $3,$2,$5}\'').read()

        # Draw the stats onto the image
        draw.text((10, 50), f"CPU: {str(cpu_usage)}", (255, 255, 255), font=font)
        draw.text((10, 70), f"MEM: {str(mem_usage)}", (255, 255, 255), font=font)
        draw.text((10, 90), disk_usage, (255, 255, 255), font=font)

        # Display the updated image on the screen
        env.display_image(img)

        # Check if button A has been pressed
        if not env.buttonA.value:
            break

        # Sleep for a short time to limit the update rate
        time.sleep(0.5)
