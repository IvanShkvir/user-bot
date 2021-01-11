from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.errors import FloodWait
from time import sleep
from datetime import datetime, timedelta
import re
import random

from additional import REPLACEMENT_MAP as RM
from additional import custom_dict, ME_ID

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

    while perc < 100:
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
    pattern = r"\[([^\[\]]*)\]"

    msg.delete()

    orig_text = msg.text.split(".mention ")[1]
    name = orig_text.split(maxsplit=1)[0]
    text = orig_text.split(maxsplit=1)[1]
    identifier = app.get_users(name).id
    try:
        tag_in_brackets = re.search(pattern, orig_text).group(0)
        tag = re.search(pattern, orig_text).group(1)
        if tag == "":
            tag = app.get_users(name).first_name
        text = text.replace(tag_in_brackets, "[{}](tg://user?id={})")
        app.send_message(msg.chat.id, text.format(tag, identifier), parse_mode="markdown")
    except AttributeError:
        tag = text
        app.send_message(msg.chat.id, "[{}](tg://user?id={})".format(tag, identifier), parse_mode="markdown")


@app.on_message(filters.command(["mention_all", "mention-all"], prefixes="."))
def mention_all(_, msg):
    msg.delete()
    # pattern = r"\[(.*)\]"
    pattern = r"\[([^\[\]]*)\]"
    try:
        orig_text = msg.text.split(maxsplit=1)[1]
        app.send_message(msg.chat.id, orig_text.split(maxsplit=1)[1], parse_mode="markdown")
    except IndexError:
        pass
    if re.search(pattern, msg.text):
        tag = re.search(pattern, msg.text).group(1)
    else:
        tag = "A"
    text = ""
    i = 0
    k = 0
    for member in app.iter_chat_members(msg.chat.id):
        if not member.user.is_bot:
            k += 1
            if tag == "n":
                text += "[{}](tg://user?id={})".format(str(k), member.user.id)
                text += " "
            else:
                text += "[{}](tg://user?id={})".format(str(tag), member.user.id)
                text += " "
            i += 1
        if i == 5:
            app.send_message(msg.chat.id, text, parse_mode="markdown")
            i = 0
            text = ""
    if text != "":
        app.send_message(msg.chat.id, text, parse_mode="markdown")


@app.on_message(filters.command(["spam", "спам"], prefixes="."))
def spam(_, msg):
    msg.delete()
    text = msg.text.split(maxsplit=2)[2]
    n = msg.text.split(maxsplit=2)[1]

    for _ in range(int(n)):
        try:
            app.send_message(msg.chat.id, text)
        except FloodWait as e:
            sleep(e.x)


@app.on_message(filters.command("flip", prefixes=".") & filters.me)
def flip(_, msg):
    msg.delete()
    text = msg.text.split(".flip", maxsplit=1)[1]
    final_str = ""
    text = text[::-1]
    for char in text:
        if char in RM.keys():
            new_char = RM[char]
        else:
            new_char = char
        final_str += new_char
    app.send_message(msg.chat.id, final_str)


@app.on_message(filters.command("word_count", prefixes="."))
def word_counter(_, msg):
    msg.delete()
    try:
        limit = int(msg.text.split()[1])
    except (ValueError, IndexError):
        limit = 2000

    try:
        k = int(msg.text.split()[2])
    except (ValueError, IndexError):
        k = 0

    words = custom_dict()
    progress = app.send_message(msg.chat.id, "`waiting for chat history to be loaded...`")

    total = 0
    for m in app.iter_history(msg.chat.id, limit=limit):
        total += 1
        if total % 100 == 0:
            try:
                progress.edit_text(f"`processed {total} messages...`")
            except FloodWait as e:
                sleep(e.x)
        if m.text:
            for word in m.text.split():
                if len(word) >= k:
                    words[word.lower()] += 1
        if m.caption:
            for word in m.caption.split():
                if len(word) >= k:
                    words[word.lower()] += 1

    progress.delete()
    app.send_message(msg.chat.id, f"`processed {total} messages...`")

    freq = sorted(words, key=words.get, reverse=True)

    if k == 0:
        out_additional = f"(any words)"
    else:
        out_additional = f"({k} and more letters)"
    out = f"Most common words {out_additional}:\n"
    for i in range(50):
        space = "    "
        if i >= 9:  # 10
            space = "  "
        out += f"{i + 1}.{space}{freq[i]} - {words[freq[i]]}\n"

    app.send_message(msg.chat.id, out, parse_mode=None)


@app.on_message(filters.command(["message_count", "msg_count"], prefixes="."))
def message_counter(_, msg):
    msg.delete()

    slf = False
    try:
        slf = "self" == msg.text.split(maxsplit=1)[1]
    except IndexError:
        pass

    total = app.get_history_count(msg.chat.id)

    # total = 0
    # for m in app.iter_history(msg.chat.id):
    #     total += 1

    name = ""
    if msg.chat.title:
        name = f" in {msg.chat.title}"
    elif msg.chat.id == ME_ID:
        pass
    elif msg.chat.first_name:
        name = f" with {msg.chat.first_name}"

    if slf:
        app.send_message("me", f"`Total amount of messages{name} is {total}`")
    else:
        app.send_message(msg.chat.id, f"`Total amount of messages{name} is {total}`")


@app.on_message(filters.command("self_test", prefixes="."))
def send_self(_, msg):
    msg.delete()
    app.send_message("me", msg.text.split(maxsplit=1)[1])


@app.on_message(filters.command("info", prefixes="."))
def info(_, msg):
    msg.delete()
    slf = False
    try:
        slf = "self" == msg.text.split(maxsplit=1)[1]
    except IndexError:
        pass

    if slf:
        app.send_message("me", f"`{msg}`")
    else:
        print(msg)


app.run()

# @app.on_message(filters.command("until_ny", prefixes="."))
# def time_until_ny(_, msg):
#     new_year = datetime(year=2021, month=1, day=1, hour=0, minute=0, second=1)
#
#     while True:
#         time_now = datetime.now()
#         print("Before adding:")
#         print(time_now)
#         d = timedelta(hours=2)
#         time_now += d
#         print("After adding two hours:")
#         print(time_now)
#
#         if time_now == new_year:
#             msg.edit(msg.chat.id, "✨ ВСІХ З НОВИМ РОКОМ!!! ✨")
#             app.send_message(msg.chat.id, "Усіх вітаю зі святом, бажаю усього найкращого в новому 2021 році!🥳")
#             app.send_message(msg.chat.id, "А тепер просто нагадування😂")
#             app.send_message(msg.chat.id, ".until_session")
#             break
#         try:
#             string = "🎄 До Нового Року "
#
#             print("New Year Date:")
#             print(new_year)
#             print("Time Now:")
#             print(time_now)
#             print("Their difference")
#             delta = str(new_year - time_now)[:-7]
#             print(delta)
#
#             h, m, s = map(int, delta.split(":"))
#
#             if h == 1 or h == 21:
#                 ending = " година, "
#             elif 1 < h < 5 or 21 < h < 25:
#                 ending = " години, "
#             else:
#                 ending = " годин, "
#
#             string += str(h)
#             string += ending
#
#             if str(m)[-1] == '1' and m != 11:
#                 ending = " хвилина, "
#             elif str(m)[-1] in ['2', '3', '4'] and not str(m).startswith('1'):
#                 ending = " хвилини, "
#             else:
#                 ending = " хвилин, "
#
#             string += str(m)
#             string += ending
#
#             if str(s)[-1] == '1' and s != 11:
#                 ending = " секунда! 🎄"
#             elif str(s)[-1] in ['2', '3', '4'] and not str(s).startswith('1'):
#                 ending = " секунди! 🎄"
#             else:
#                 ending = " секунд! 🎄"
#
#             string += str(s)
#             string += ending
#
#             msg.edit(string)
#             sleep(0.9)
#
#         except FloodWait as e:
#             sleep(e.x)

