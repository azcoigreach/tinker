import asyncio
import asyncclick as click
from tinker.cli import pass_environment

@click.command()
@pass_environment
async def cli(env):
    loop = asyncio.get_event_loop()
    buttonA_state = True
    buttonB_state = True

    async def poll_buttons():
        nonlocal buttonA_state
        nonlocal buttonB_state
        while True:
            new_state_A = env.buttonA.value
            new_state_B = env.buttonB.value
            
            if new_state_A != buttonA_state:
                buttonA_state = new_state_A
                if buttonA_state:
                    env.log("Button A pressed")

            if new_state_B != buttonB_state:
                buttonB_state = new_state_B
                if buttonB_state:
                    env.log("Button B pressed")

            await asyncio.sleep(0.05)

    asyncio.ensure_future(poll_buttons())

    while True:
        env.log("Main loop")
        await asyncio.sleep(2.0)  # Wait for user to exit command
