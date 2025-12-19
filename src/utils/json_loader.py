import json

CONFIG_PATH = "../config/config.json"
MESSAGES_PATH = "../config/messages.json"

def load_config_file():
    try:
        with open(CONFIG_PATH, "r", encoding="UTF-8") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Could not load config.json: {e}")

def load_messages_file(language):
    try:
        with open(MESSAGES_PATH, "r", encoding="UTF-8") as messages_file:
            all_messages = json.load(messages_file)
            return all_messages[language]
    except Exception as e:
        print(f"Could not load messages.json: {e}")
