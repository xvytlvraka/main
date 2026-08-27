from telegram import *
from telegram.ext import *
from datetime import datetime, timedelta

from config import *
from database import *
from keep_alive import keep_alive

keep_alive()

app = Application.builder().token(BOT_TOKEN).build()

# START
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):

    kb = [[InlineKeyboardButton("✅ Complete Task",callback_data="task")]]

    await update.message.reply_text(
        "Join 6 channels and unlock premium.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# GROUP JOIN
async def join(update:Update, context):

    for user in update.message.new_chat_members:

        add(user.id,user.username or user.first_name)

        await context.bot.send_message(
            GROUP_ID,
            f"🎉 Thanks for joining @{user.username}"
        )

        try:
            kb=[[InlineKeyboardButton("📋 Start Task",callback_data="task")]]
            await context.bot.send_message(
                user.id,
                "Welcome! Complete the task.",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        except:
            pass

# BUTTONS
async def button(update:Update, context):

    q = update.callback_query
    await q.answer()

    if q.data=="task":

        rows=[]

        for ch in TASKS:
            rows.append([
                InlineKeyboardButton(
                    f"Join {ch}",
                    url=f"https://t.me/{ch.replace('@','')}"
                )
            ])

        rows.append([InlineKeyboardButton("🔍 Verify",callback_data="verify")])

        await q.edit_message_text(
            "Join all 6 channels then Verify.",
            reply_markup=InlineKeyboardMarkup(rows)
        )

    elif q.data=="verify":

        uid=q.from_user.id

        for ch in TASKS:

            try:
                m = await context.bot.get_chat_member(ch,uid)

                if m.status in ["left","kicked"]:
                    await q.answer("Join all channels first",show_alert=True)
                    return

            except:
                await q.answer("Bot must be admin in all channels",show_alert=True)
                return

        if completed(uid):
            await q.answer("Already completed")
            return

        done(uid)

        await context.bot.send_message(
            GROUP_ID,
            f"✅ @{q.from_user.username} successfully completed"
        )

        link = await context.bot.create_chat_invite_link(
            chat_id=PREMIUM_CHANNEL_ID,
            member_limit=1,
            expire_date=datetime.now()+timedelta(minutes=10)
        )

        await q.edit_message_text(
            f"🎁 Premium Link\n\n{link.invite_link}"
        )

app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS,join))
app.add_handler(CallbackQueryHandler(button))

print("BOT STARTED...")
app.run_polling(drop_pending_updates=True)
