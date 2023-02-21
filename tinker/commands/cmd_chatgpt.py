import os
import openai
import asyncio
import asyncclick as click
import curses
from tinker.cli import pass_environment
import json
from tinker.configs import chatgpt

openai.api_key = chatgpt.api_key

# initial set up 
@click.command()
@click.option('--model', default="text-davinci-003", show_default=True)
@click.option('--temperature', default=0.9, show_default=True)
@click.option('--max_tokens', default=150, show_default=True)
@click.option('--top_p', default=1, show_default=True)
@click.option('--frequency_penalty', default=0.0, show_default=True)
@click.option('--presence_penalty', default=0.6, show_default=True)
@pass_environment
def cli(env, model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
    # Initialize the curses library
    stdscr = curses.initscr()
    curses.cbreak()
    curses.echo()
    curses.start_color()

    # Set up the color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # Split the terminal window into two panes
    input_pane = curses.newwin(8, curses.COLS, curses.LINES - 1, 0)
    history_pane = curses.newwin(curses.LINES - 8, curses.COLS, 0, 0)

    # Variable to store conversation history
    conversation_history = []
    try:
        while True:
            # Display the conversation history in the history pane
            history_pane.clear()
            for i, message in enumerate(conversation_history):
                history_pane.addstr(i, 0, message, curses.color_pair(2))
            history_pane.refresh()

            # Add the horizontal line separating the history from the input pane
            input_pane.hline(0, 0, curses.ACS_HLINE, curses.COLS)
            input_pane.refresh()

            # Prompt the user for input in the input pane
            input_pane.clear()
            input_pane.addstr(0, 0, "You: ", curses.color_pair(1))
            user_input = input_pane.getstr().decode()
            if user_input.strip() == "":
                break

            # Add the user's input to the conversation history
            conversation_history.append("You: " + user_input)

            # Send the user's input to OpenAI's GPT-3 language model
            resp = openai.Completion.create(
                model=model,
                prompt=user_input,  
                temperature=float(temperature), 
                max_tokens=int(max_tokens),
                top_p=top_p, 
                frequency_penalty=float(frequency_penalty), 
                presence_penalty=float(presence_penalty),
                stop=[ 'Human:', 'AI:' ] 
            )
            
            # Add the response to the conversation history
            conversation_history.append(f"ChatGPT: {resp['choices'][0]['text']}")
            
    except KeyboardInterrupt:
        # End the curses session
        curses.nocbreak()
        curses.echo()
        curses.endwin()

        # When the loop ends, write conversation.json into env.json_folder
        with open(os.path.join(env.json_folder, "conversation.json"), "w") as f:
            json.dump(conversation_history, f)
        
