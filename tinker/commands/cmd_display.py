import click
from tinker.cli import pass_environment
# import tinker.cli.functions
import digitalio
import board
from adafruit_rgb_display.rgb import color565
from adafruit_rgb_display import st7789
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time


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

    ctx.backlight = digitalio.DigitalInOut(board.D22)
    ctx.backlight.switch_to_output()
    ctx.backlight.value = True
    ctx.buttonA = digitalio.DigitalInOut(board.D23)
    ctx.buttonB = digitalio.DigitalInOut(board.D24)
    ctx.buttonA.switch_to_input(digitalio.Pull.UP)
    ctx.buttonB.switch_to_input(digitalio.Pull.UP)

@cli.command("test", short_help="Test Display")
@pass_environment
def test(ctx):
    '''Basic Display test with buttons'''
    # Main loop:
    while True:
        if ctx.buttonA.value and ctx.buttonB.value:
            ctx.backlight.value = False  # turn off backlight
            ctx.vlog(f'Backlight Off')
        else:
            ctx.backlight.value = True  # turn on backlight
            ctx.vlog(f'Backlight On')
        if ctx.buttonB.value and not ctx.buttonA.value:  # just button A pressed
            ctx.display.fill(color565(255, 0, 0))  # red
            ctx.vlog(f'Button A - RED')
        if ctx.buttonA.value and not ctx.buttonB.value:  # just button B pressed
            ctx.display.fill(color565(0, 0, 255))  # blue
            ctx.vlog(f'Button B - Blue')
        if not ctx.buttonA.value and not ctx.buttonB.value:  # none pressed
            ctx.display.fill(color565(0, 255, 0))  # green
            ctx.vlog(f'Button C - Green')

@cli.command("stats", short_help="Test Display")
@pass_environment
def stats(ctx):
    '''Pillow display stats'''
    ctx.display.rotation = 90
    if ctx.display.rotation % 180 == 90:
        height = ctx.display.width  # we swap height/width to rotate it to landscape!
        width = ctx.display.height
    else:
        width = ctx.display.width  # we swap height/width to rotate it to landscape!
        height = ctx.display.height

    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    ctx.display.image(image)

    # First define some constants to allow easy positioning of text.
    padding = -2
    x = 0

    # Load a TTF font.  Make sure the .ttf font file is in the
    # same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

    while True:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d' ' -f1"
        IP = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Write four lines of text.
        y = padding
        draw.text((x, y), IP, font=font, fill="#FFFFFF")
        y += font.getsize(IP)[1]
        draw.text((x, y), CPU, font=font, fill="#FFFF00")
        y += font.getsize(CPU)[1]
        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
        y += font.getsize(MemUsage)[1]
        draw.text((x, y), Disk, font=font, fill="#0000FF")
        y += font.getsize(Disk)[1]
        draw.text((x, y), Temp, font=font, fill="#FF00FF")

        # Display image.
        ctx.display.image(image)
        time.sleep(0.1)

@cli.command("cmd_test", short_help="Test firing command with a button")
@pass_environment
def test(ctx):
    '''Test firing command with a button'''
    
    # def cmd_sub():
    #     cmd = "/usr/bin/python3 /usr/local/bin/tinker display stats"
    #     Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        

    result = True
    running = False
    prev_state = ctx.buttonB.value
    while result is not False:
        cur_state = ctx.buttonB.value
        if cur_state != prev_state:
            if not cur_state:
                run_once = 0
                while 1:
                    if run_once == 0:
                        print("BTN is down")
                        run_once = 1
            else:
                print("BTN is up")
        # if ctx.buttonB.value and not ctx.buttonA.value:
        #     running = not running
        #     if running:
        #         ctx.log("running command")
        #     else:
        #         ctx.log("not running")
        #     time.sleep(0.2)
        
        # if running:
        #     while running is not False:
        #         result = ctx.log(click.style('cmd fired', fg='red'))
        #         running = not running

@cli.command("menus", short_help="Menu template")
@pass_environment
def test(ctx):
    '''Menu test and templates'''