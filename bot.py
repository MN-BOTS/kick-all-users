#credit spechide



import asyncio
import os
import sys
from pymongo import MongoClient
from pyrogram import Client
from pyrogram.errors import RPCError

# Install dependencies if missing
try:
    from pyrogram import Client
except ImportError:
    os.system("pip install --no-cache --upgrade pyrogram tgcrypto pymongo")
    from pyrogram import Client

# MongoDB Connection (Change this to your MongoDB URI)
MONGO_URI = "mongodb://localhost:27017"  # Change for MongoDB Atlas
DB_NAME = "telegram_bot"
COLLECTION_NAME = "banned_users"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

async def auto_ban_unban():
    if len(sys.argv) != 3:
        print("Usage: python bot.py <BOT_TOKEN> <CHAT_ID>")
        sys.exit(1)

    bot_token = sys.argv[1]
    chat_id = int(sys.argv[2])

    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API HASH: ")

    # Initialize bot
    app = Client(
        "bot",
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        in_memory=True,
        sleep_threshold=1800
    )

    await app.start()
    print(f"Bot started successfully!\nProcessing chat: {chat_id}")

    success_count, fail_count = 0, 0

    # Iterate through chat members
    async for member in app.get_chat_members(chat_id):
        if not member.user:
            continue  # Skip invalid users

        user_id = member.user.id
        first_name = member.user.first_name

        try:
            print(f"Banning user: {user_id} ({first_name})")
            await app.ban_chat_member(chat_id, user_id)
            await asyncio.sleep(5)  # Avoid Telegram rate limits

            print(f"Unbanning user: {user_id}")
            await app.unban_chat_member(chat_id, user_id)

            # Store banned user in MongoDB
            collection.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "chat_id": chat_id
            })

            success_count += 1

        except RPCError as ex:
            print(f"Error Occurred: {user_id} - {ex}")
            fail_count += 1

    await app.stop()
    print(f"\nProcess Completed!\nTotal Success: {success_count}\nTotal Failures: {fail_count}")

if __name__ == "__main__":
    try:
        asyncio.run(auto_ban_unban())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(auto_ban_unban())
