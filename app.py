import os
from pyrogram import Client
from dotenv import load_dotenv
import tiktoken
import openai
import time

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Initialize the Pyrogram client
app = Client("my_account", api_id=api_id, api_hash=api_hash)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

def count_tokens(text, model=MODEL):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)

def format_message(text, date):
    # Make each message clearer with dates and proper formatting
    return f"Date: {date}\nMessage: {text}\n\n"

def get_text_messages_from_channel(client, channel_username, limit=50, filename="messages.txt"):
    if not client.join_chat(channel_username):
        client.join_chat(channel_username)
    
    messages = client.get_chat_history(channel_username, limit=limit)
    messages_list = list(messages)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for message in messages_list:
            text = getattr(message, "text", None) or getattr(message, "caption", None)
            date = message.date.strftime('%Y-%m-%d %H:%M:%S')  # Get message date
            if text:
                formatted_message = format_message(text, date)
                f.write(formatted_message)

def get_gpt_summary_from_file(input_file, output_file, model=MODEL, max_tokens=500):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    summary = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes text in a very concise way."},
            {"role": "user", "content": content}
        ],
        max_tokens=max_tokens,
        temperature=0.0
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary.choices[0].message.content + '\n')

# Function to be called on client startup
def on_startup():
    channel_username = "@bitcoin"  # Replace with your target channel username
    get_text_messages_from_channel(app, channel_username)

    # Process and summarize the text
    get_gpt_summary_from_file("messages.txt", "summarized.txt")
    print("starting new cycle...")

# Starting the client and running in a loop every minute
while True:
    with app:
        on_startup()
    time.sleep(30)  # Sleep for one minute (60 seconds)
