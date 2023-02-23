import os
import json
import asyncclick as click
import time
import aiohttp
import aiofiles
from tinker.cli import pass_environment
from tinker.configs import chatgpt

@pass_environment
async def log_prompt_data(ctx, data):
    try:
        with open(f"{ctx.json_folder}/prompt_data_log.json", "a") as f:
            f.write(json.dumps(data) + "\n")
            f.flush()
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))

@pass_environment
async def log_completion_response(ctx, resp):
    try:
        with open(f"{ctx.json_folder}/completions_log.json", "a") as f:
            f.write(json.dumps(resp) + "\n")
            f.flush()
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))

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
    try: 
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/completions", headers=headers, json=data) as resp:
                if resp.status != 200:
                    click.echo(click.style(f"Error: {resp.text}", fg='red'))
                    return None
                json_resp = await resp.json()
                usage = json_resp["usage"]["total_tokens"]
                result = json_resp["choices"][0]["text"]
            
                # Write prompt data to log
                await log_prompt_data(data)

                # Write completion response to log
                await log_completion_response(json_resp)

                return usage, result
    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'))
        return None


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
    max_history = 5
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
        conversation_history = conversation_history[-max_history:]

    click.echo("Conversation saved to file.")

