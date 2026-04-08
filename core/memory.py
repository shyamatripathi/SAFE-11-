# core/memory.py

user_memory = {}

def get_memory_context(user_id):
    history = user_memory.get(user_id, [])
    return "\n".join(history[-5:])  # last 5 messages

def update_memory(user_id, user_message, bot_reply):
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append(f"User: {user_message}")
    user_memory[user_id].append(f"Bot: {bot_reply}")