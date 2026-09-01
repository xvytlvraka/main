import asyncio
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, GROUP_ID, PREMIUM_CHANNEL_ID, TASKS
from database import add, done, completed
from keep_alive import keep_alive

# ---------------- KEEP ALIVE ---------------- #
keep_alive()

# ---------------- BOT ---------------- #
app = Application.builder().token(BOT_TOKEN).build()


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Complete Task", callback_data="task")]
    ]

    await update.message.reply_text(
        "Welcome!\nJoin all 6 channels to unlock the Premium Channel.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# New member joins group
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:

        username = user.username if user.username else user.first_name

        add(user.id, username)

        # Group message
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"🎉 Thanks for joining @{username}",
        )

        # DM task
        try:
            keyboard = [
                [InlineKeyboardButton("✅ Start Task", callback_data="task")]
            ]

            await context.bot.send_message(
                chat_id=user.id,
                text="Welcome!\nComplete the task to access Premium.",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except:
            pass


# Buttons
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Show tasks
    if query.data == "task":

        rows = []

        for channel in TASKS:
            rows.append(
                [
                    InlineKeyboardButton(
                        text=f"Join {channel}",
                        url=f"https://t.me/{channel.replace('@','')}",
                    )
                ]
            )

        rows.append(
            [InlineKeyboardButton("🔍 Verify", callback_data="verify")]
        )

        await query.edit_message_text(
            "Join all 6 channels, then press Verify.",
            reply_markup=InlineKeyboardMarkup(rows),
        )

    # Verify
    elif query.data == "verify":

        uid = query.from_user.id

        # Already completed
        if completed(uid):
            await query.answer("Already completed!", show_alert=True)
            return

        # Check every channel
        for channel in TASKS:

            try:
                member = await context.bot.get_chat_member(channel, uid)

                if member.status in ["left", "kicked"]:
                    await query.answer(
                        "❌ First join all 6 channels.",
                        show_alert=True,
                    )
                    return

            except:
                await query.answer(
                    "⚠️ Bot must be Admin in every task channel.",
                    show_alert=True,
                )
                return

        # Save DB
        done(uid)

        username = (
            query.from_user.username
            if query.from_user.username
            else query.from_user.first_name
        )

        # Group success
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"✅ @{username} successfully completed",
        )

        # Temporary premium link
        invite = await context.bot.create_chat_invite_link(
            chat_id=PREMIUM_CHANNEL_ID,
            member_limit=1,
            expire_date=datetime.now() + timedelta(minutes=10),
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔓 Join Premium Channel",
                    url=invite.invite_link,
                )
            ]
        ]

        await query.edit_message_text(
            "🎉 Task Completed!\n\nYour Premium Link (valid 10 min):",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ---------------- HANDLERS ---------------- #
app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member)
)

app.add_handler(CallbackQueryHandler(buttons))


# ---------------- RUN (PYTHON 3.14 FIX) ---------------- #
async def main():
    print("BOT STARTED...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
