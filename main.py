import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === CONFIGURATION ===
BOT_TOKEN = "7002558853:AAFX0gEwS8RJh6MY8g1qw2P_oVdQYu1_GNc"
OWNER_ID = 1209978813
FORCE_JOIN_CHANNEL = "-1001857302142"
BOT_USERNAME = "@Image_colour_changer_bot"
API_URL = "https://clothchangertech.usefullbots.workers.dev/clothchangertech"

# === INIT DB ===
if not os.path.exists("db.json"):
    with open("db.json", "w") as f:
        json.dump({}, f)

with open("db.json") as f:
    users = json.load(f)

def save():
    with open("db.json", "w") as f:
        json.dump(users, f)

# === COMMAND: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if str(user.id) not in users:
        users[str(user.id)] = {"count": 0}
        save()
        await context.bot.send_message(
            OWNER_ID,
            f"👤 New user: @{user.username or 'NoUsername'}\n🆔 ID: {user.id}\n📊 Total users: {len(users)}"
        )

    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/+ZUXtxXBzR_VkMjU1")],
        [InlineKeyboardButton("💬 Join Group", url="https://t.me/girl_group_chating_group")],
        [InlineKeyboardButton("✅ Joined (Verify)", callback_data="verify")]
    ]
    await update.message.reply_text(
        "💠 *This bot can help you to change anyone's clothes colour*\nYou need to join the developer channel first 👇👇👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# === CALLBACK: verify button ===
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        member = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL, query.from_user.id)
        if member.status not in ("member", "creator", "administrator"):
            raise Exception()
    except:
        await query.edit_message_text("❌ You must join the channel first.")
        return

    await query.edit_message_text("✅ You are verified!\nSend me a person image to change clothes colour")

# === PHOTO HANDLER ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in users:
        users[user_id] = {"count": 0}

    if users[user_id]["count"] >= 2:
        keyboard = [[InlineKeyboardButton("📤 Forward Bot", url=f"https://t.me/{BOT_USERNAME[1:]}")]]
        await update.message.reply_text(
            "🚫 You have reached your limit.\nRefer 2 people for more image generations:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("♻️ Wait I am changing cloth colour, please wait a few seconds... ⏳")

    file = await update.message.photo[-1].get_file()
    img_url = file.file_path

    print("🖼️ Image URL:", img_url)

    # Send request to API
    resp = requests.post(API_URL, json={
        "person": img_url,
        "cloth": "https://i.ibb.co/fNtfsHP/cloth1.png"
    })

    print("🌐 API Response:", resp.text)

    try:
        result = resp.json()
        if "result_url" in result:
            users[user_id]["count"] += 1
            save()
            await update.message.reply_photo(result["result_url"], caption="🎉 Congratulations!\nI sent you your image ✅")
        else:
            raise Exception()
    except Exception as e:
        print("❌ Error processing image:", str(e))
        await update.message.reply_text("❌ Failed to process image. Try again later.")

# === MAIN ===
async def main():
    # Delete webhook (clean)
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    print("✅ Webhook removed (if set previously)")

    # Init application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Bot is running... (Press Ctrl+C to stop)")
    await app.run_polling()

# === RUN ===
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
