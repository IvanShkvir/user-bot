from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.errors import FloodWait
from time import sleep
import random

app = Client("my_account")


@app.on_message(filters.command("тайп", prefixes=".") & filters.me)
def type(_, msg):
    orig_text = msg.text.split(".тайп ", maxsplit=1)[1]
    text = orig_text
    tbp = ""  # to be printed
    typing_symbol = "▒"

    while tbp != orig_text:
        try:
            msg.edit(tbp + typing_symbol)
            sleep(0.001)  # 50 ms

            tbp = tbp + text[0]
            text = text[1:]

            msg.edit(tbp)
            sleep(0.001)

        except FloodWait as e:
            sleep(e.x)


@app.on_message(filters.command("analysis", prefixes=".") & filters.me)
def hack(_, msg):
    perc = 0

    while (perc < 100):
        try:
            text = "🧠 Провожу тест на IQ " + str(perc) + "%"
            msg.edit(text)

            perc += random.randint(100, 200) / 30
            sleep(0.05)

        except FloodWait as e:
            sleep(e.x)

    msg.edit("Готово!✅")
    sleep(1.5)
    msg.edit("🧠 Поздравляю, твой IQ - " + str(random.randint(50, 200)))


@app.on_message(filters.command(["s", "screenshot"], prefixes="."))
def take_a_screenshot(app, message):
    message.delete()
    app.send(
        functions.messages.SendScreenshotNotification(
            peer=app.resolve_peer(message.chat.id),
            reply_to_msg_id=0,
            random_id=app.rnd_id(),
        )
    )


@app.on_message(filters.command("mention", prefixes="."))
def mention_user(_, msg):
    orig_text = msg.text.split(".mention")
    name = orig_text[1].split()[0].replace(" ", "")
    text = orig_text[1].split(name)[1]
    identifier = app.get_users(name).id
    chat_id = msg.chat.id
    msg.delete()

    app.send_message(chat_id, ("[{}](tg://user?id={})".format(text, identifier)), parse_mode="markdown")


@app.on_message(filters.command("info", prefixes="."))
def info(_, msg):
    text = ""
    for member in app.iter_chat_members(msg.chat.id):
        print(member)

    msg.delete()
    # app.send_message(msg.chat.id, text, parse_mode="markdown")


@app.on_message(filters.command(["mention_all", "mention-all"], prefixes="."))
def mention_all(_, msg):
    msg.delete()
    orig_text = msg.text.split(maxsplit=1)[1]
    app.send_message(msg.chat.id, orig_text, parse_mode="markdown")
    text = ""
    i = 0
    for member in app.iter_chat_members(msg.chat.id):
        if not member.user.is_bot:
            i += 1
            text += "[A](tg://user?id={})".format(member.user.id)
            text += " "
        if i == 5:
            app.send_message(msg.chat.id, text, parse_mode="markdown")
            i = 0
            text = ""
    if text != "":
        app.send_message(msg.chat.id, text, parse_mode="markdown")


app.run()
