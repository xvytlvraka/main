import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
PREMIUM_CHANNEL_ID = int(os.getenv("PREMIUM_CHANNEL_ID"))

TASKS = [
    os.getenv("TASK1"),
    os.getenv("TASK2"),
    os.getenv("TASK3"),
    os.getenv("TASK4"),
    os.getenv("TASK5"),
    os.getenv("TASK6")
]
