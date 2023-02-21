import os
import time
import asyncio
import asyncclick as click
from tinker.cli import pass_environment

from PIL import Image, ImageDraw, ImageFont

import psutil
import ifaddr
import speedtest

@click.command()
@pass_environment
async def cli(env):
    # Set the display rotation
    env.display.rotation = 270
    if env.display.rotation % 180 == 90:
        height = env.display.width  # we swap height/width to rotate it to landscape!
        width = env.display.height
    else:
        width = env.display.width  # we swap height/width to rotate it to landscape!
        height = env.display.height

    # Define the fonts for the stats
    font_large = ImageFont.truetype(os.path.join(env.font_folder, "retro_gaming.ttf"), 32)
    font_small = ImageFont.truetype(os.path.join(env.font_folder, "retro_gaming.ttf"), 16)

    # Define the states for the speedtest
    SPEEDTEST_STATE_IDLE = 0
    SPEEDTEST_STATE_TESTING = 1
    SPEEDTEST_STATE_CANCELLED = 2
    
    # Initialize the speedtest state
    speedtest_state = SPEEDTEST_STATE_IDLE

    # Define the initial page to display
    page = 1

    # Polling buttons
    loop = asyncio.get_event_loop()
    buttonA_state = True
    buttonB_state = True
    
    async def poll_buttons():
        nonlocal buttonA_state
        nonlocal buttonB_state
        nonlocal page
        nonlocal speedtest_state
        while True:
            new_state_A = env.buttonA.value
            new_state_B = env.buttonB.value
            
            if new_state_A != buttonA_state:
                buttonA_state = new_state_A
                if buttonA_state:
                    env.vlog(f"Button A pressed, speedtest_state = {speedtest_state}")                    

            if new_state_B != buttonB_state:
                buttonB_state = new_state_B
                if buttonB_state:
                    page = page + 1
                    if page > 2:
                        page = 1
                    env.vlog(f"Button B pressed, page = {page}")

            await asyncio.sleep(0.05)

    asyncio.ensure_future(poll_buttons())
    

    while True:
        # Display the initial stats on the screen
        img = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)        
        
        if page == 1:
            # Clear the image
            draw.rectangle((0, 0, width, height), (0, 0, 0))
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


            # Get the system stats
            # Print the IP addresses for each interface
            if usb0 is not None:
                for ip in usb0.ips:
                    if ip.is_IPv4:
                        draw.text((10, 10), f"usb0: {ip.ip}", (255, 255, 255), font=font_small)
            if wlan0 is not None:
                for ip in wlan0.ips:
                    if ip.is_IPv4:
                        draw.text((10, 30), f"wlan0: {ip.ip}", (255, 255, 255), font=font_small)
            cpu_usage = psutil.cpu_percent(interval=1)
            mem_usage = psutil.virtual_memory().percent
            disk_usage = os.popen('df -h / | awk \'NR==2{printf "DISK: %d/%dGB %s", $3,$2,$5}\'').read()

            # Draw the stats onto the image
            draw.text((10, 50), f"CPU: {str(cpu_usage)}", (255, 255, 255), font=font_small)
            draw.text((10, 70), f"MEM: {str(mem_usage)}", (255, 255, 255), font=font_small)
            draw.text((10, 90), disk_usage, (255, 255, 255), font=font_small)

            # Display the updated image on the screen
            env.display_image(img)

        elif page == 2:
            # Clear the image
            draw.rectangle((0, 0, width, height), (0, 0, 0))

            # Write "Speedtest" at the top of the screen and "Press A to start" at the bottom
            draw.text((10, 0), "Speedtest", (255, 255, 255), font=font_large)
            # env.display_image(img)
            
            if speedtest_state == SPEEDTEST_STATE_IDLE:
                if not buttonA_state:
                    # Start the speedtest
                    draw.text((10, height - 20), "Testing...", (255, 255, 255), font=font_small)
                    env.display_image(img)
                    s = speedtest.Speedtest()
                    s.get_best_server()
                    s.download()
                    s.upload()
                    results_dict = s.results.dict()
                    speedtest_state = SPEEDTEST_STATE_TESTING
                else:
                    # Draw the stats onto the image
                    draw.text((10, height - 20), "Press A to start", (255, 255, 255), font=font_small)

                    # Display the updated image on the screen
                    env.display_image(img)

            elif speedtest_state == SPEEDTEST_STATE_TESTING:
                # Check if the test has been cancelled
                if not buttonA_state:
                    draw.text((10, height - 20), "Cancelled", (255, 255, 255), font=font_small)
                    speedtest_state = SPEEDTEST_STATE_CANCELLED
                else:
                    # Draw the stats onto the image
                    draw.text((10, height - 70), f"Download: {str(round(results_dict['download'] / 1000000, 2))} Mbps", (255, 255, 255), font=font_small)
                    draw.text((10, height - 50), f"Upload: {str(round(results_dict['upload'] / 1000000, 2))} Mbps", (255, 255, 255), font=font_small)
                    draw.text((10, height - 30), f"Ping: {str(round(results_dict['ping'], 2))} ms", (255, 255, 255), font=font_small)

                    # Display the updated image on the screen
                    env.display_image(img)

            elif speedtest_state == SPEEDTEST_STATE_CANCELLED:
                # Check if the test should be restarted
                if not buttonA_state:
                    draw.text((10, height - 20), "Testing...", (255, 255, 255), font=font_small)
                    env.display_image(img)
                    s = speedtest.Speedtest()
                    s.get_best_server()
                    s.download()
                    s.upload()
                    results_dict = s.results.dict()
                    speedtest_state = SPEEDTEST_STATE_TESTING


        #     # Sleep for a short time to limit the update rate
        env.vlog("Main loop")
        await asyncio.sleep(0.5)



    # loop = asyncio.get_event_loop()
    # buttonA_state = False
    # buttonB_state = False

    # async def poll_buttons():
    #     nonlocal buttonA_state
    #     nonlocal buttonB_state
    #     while True:
    #         new_state_A = env.buttonA.value
    #         new_state_B = env.buttonB.value
            
    #         if new_state_A != buttonA_state:
    #             buttonA_state = new_state_A
    #             loop.call_soon_threadsafe(handle_buttonA, buttonA_state)
            
    #         if new_state_B != buttonB_state:
    #             buttonB_state = new_state_B
    #             loop.call_soon_threadsafe(handle_buttonB, buttonB_state)
    #         env.vlog(f"Button A state = {buttonA_state}, Button B state = {buttonB_state}")
    #         await asyncio.sleep(0.05)

    

    # async def handle_buttonA(state):
    #     env.vlog(f"Button B pressed, state = {state}")
    #     # nonlocal speedtest_state
    #     # if speedtest_state == SPEEDTEST_STATE_TESTING:
    #     #     speedtest_state = SPEEDTEST_STATE_CANCELLED
    #     #     env.vlog(f"Button B pressed, cancelling speedtest")
    #     # if speedtest_state == SPEEDTEST_STATE_IDLE:
    #     #     env.vlog(f"Button B pressed, starting speedtest")
    #     #     speedtest_state = SPEEDTEST_STATE_TESTING

    # asyncio.ensure_future(poll_buttons())