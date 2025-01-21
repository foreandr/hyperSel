import requests
import json

'''NEED TOOLING TO CREATE THE TELEGRAM BOT TOO'''

# Load the BOT_TOKEN from config.json
with open('./hypersel_extras/config.json', 'r') as config_file:
    config = json.load(config_file)
    BOT_TOKEN = config["BOT_TOKEN"]

def get_unique_chat_ids():
    """
    Fetches and returns a list of unique chat IDs from users who have messaged the bot.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        chat_ids = set()  # Use a set to avoid duplicate chat IDs
        
        for update in data['result']:
            # Extract the chat ID from each update
            chat_id = update['message']['chat']['id']
            chat_ids.add(chat_id)
        
        return list(chat_ids)
    else:
        print("Failed to retrieve updates:", response.text)
        return []

def broadcast_message(text):
    """
    Sends the specified message to all unique chat IDs who have messaged the bot.
    
    Parameters:
        text (str): The message content to send to all users.
    """
    chat_ids = get_unique_chat_ids()
    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"Message sent to {chat_id}")
        else:
            print(f"Failed to send message to {chat_id}: {response.text}")

# Example usage
if __name__ == '__main__':
    broadcast_message("Hello! This is a broadcast message to all users who have messaged the bot.")
