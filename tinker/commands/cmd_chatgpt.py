import os
import json
import asyncclick as click
import time
import aiohttp
import aiofiles
from tinker.cli import pass_environment
from tinker.configs import chatgpt

async def prompt_user(prompt, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, conversation_history):
    prompt_with_history = "\n".join(conversation_history + [prompt])
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {chatgpt.api_key}",
    }
    data = {
        "model": model,
        "prompt": prompt_with_history,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/completions", headers=headers, json=data) as resp:
            if resp.status != 200:
                click.echo(click.style(f"Error: {resp.text}", fg='red'))
                return None

            usage = (await resp.json())["usage"]["total_tokens"]
            result = (await resp.json())["choices"][0]["text"]
            return usage, result


@click.command()
@click.option('--model', default="text-davinci-003", show_default=True)
@click.option('--temperature', default=0.9, show_default=True)
@click.option('--max_tokens', default=250, show_default=True)
@click.option('--top_p', default=1, show_default=True)
@click.option('--frequency_penalty', default=0.0, show_default=True)
@click.option('--presence_penalty', default=0.6, show_default=True)
@pass_environment
async def cli(env, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
    conversation_history = []

    async with aiofiles.open(os.path.join(env.json_folder, "conversation.json"), "w") as f:
        while True:
            user_input = click.prompt(click.style("You: ", fg='green'), type=str)
            if not user_input.strip():
                break

            prompt = user_input.strip()
            start_time = time.perf_counter()
            usage, resp = await prompt_user(prompt, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, conversation_history)
            end_time = time.perf_counter()

            if not resp:
                continue

            response_time = end_time - start_time
            click.echo(click.style(f"ChatGPT: {resp}", fg='yellow'))
            click.echo(click.style(f"Response time: {response_time:.2f} seconds, token usage: {usage}", fg='cyan'))

            conversation_history.extend([f"You: {user_input}", f"ChatGPT: {resp}"])
            await f.write(json.dumps(conversation_history) + "\n")
            await f.flush()

    click.echo("Conversation saved to file.")

