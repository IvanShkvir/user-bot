import re
import random
import string
from time import sleep

from pyrogram import Client, filters, types
from pyrogram.raw import functions
from pyrogram.errors import FloodWait

from additional import REPLACEMENT_MAP as RM
from additional import custom_dict, MY_ID

from config import API_ID, API_HASH

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

groups = [
    -1001445304641,  # KN-112
]


@app.on_message(filters.command(["тайп", "type"], prefixes=".") & filters.me)
def type_msg(_, msg):
    orig_text = msg.text.split(maxsplit=1)[1]
    text = orig_text
    tbp = ""  # to be printed
    typing_symbol = "▒"

    while tbp != orig_text:
        try:
            msg.edit(tbp + typing_symbol)
            sleep(0.05)  # 50 ms

            tbp = tbp + text[0]
            text = text[1:]

            msg.edit(tbp)
            sleep(0.001)

        except FloodWait as e:
            sleep(e.x)


@app.on_message(filters.command("analysis", prefixes=".") & filters.me)
def iq(_, msg):
    progress = 0

    while progress < 100:
        try:
            text = "🧠 Провожу тест на IQ " + str(progress) + "%"
            msg.edit(text)

            progress += random.randint(100, 200) / 30
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


@app.on_message(filters.command("mention", prefixes=".") & filters.me)
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


@app.on_message(filters.command(["mention_all", "mention-all", "ma", "m-a", "m_a", "ма"], prefixes=".") &
                (filters.me | filters.chat(chats=groups)))
def mention_all(_, msg):
    msg.delete()

    if msg.from_user.id != MY_ID:
        app.send_message(msg.chat.id,
                         f"Message was automatically generated by [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})",
                         parse_mode="markdown")

    pattern = r"\[([^\[\]]*)\]"

    arg = re.search(pattern, msg.text)  # for tag
    if arg:
        tag = arg.group(1)
        orig_text = msg.text.replace(arg.group(0), "")

        try:
            app.send_message(msg.chat.id, orig_text.split(maxsplit=1)[1], parse_mode="markdown")
        except IndexError:
            pass
    else:
        try:
            orig_text = msg.text.split(maxsplit=1)[1]
            app.send_message(msg.chat.id, orig_text, parse_mode="markdown")
        except IndexError:
            pass

        tag = "A"

    text = ""
    i = 0
    k = 0
    for member in app.iter_chat_members(msg.chat.id):
        if not member.user.is_bot:
            k += 1
            if tag == "n":
                text += "[{}](tg://user?id={})".format(str(k), member.user.id)
                # text += str(k)
                text += " "
            else:
                text += "[{}](tg://user?id={})".format(str(tag), member.user.id)
                # text += str(tag)
                text += " "
            i += 1
        if i == 5:
            app.send_message(msg.chat.id, text, parse_mode="markdown")
            i = 0
            text = ""
    if text != "":
        app.send_message(msg.chat.id, text, parse_mode="markdown")

    try:
        app.send_message(msg.chat.id, orig_text, parse_mode="markdown")
    except NameError:
        pass


@app.on_message(filters.command(["spam", "спам"], prefixes=".") & filters.me)
def spam(_, msg):
    msg.delete()
    text = msg.text.split(maxsplit=2)[2]
    n = msg.text.split(maxsplit=2)[1]

    for _ in range(int(n)):
        try:
            app.send_message(msg.chat.id, text)
        except FloodWait as e:
            sleep(e.x)


@app.on_message(filters.command(["spam_random", "random_spam", "спам_рандом", "рандом_спам"], prefixes=".") & filters.me)
def spam_random(_, msg):
    msg.delete()
    amount = int(msg.text.split()[1])
    n = int(msg.text.split()[2])

    for _ in range(amount):
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
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


@app.on_message(filters.command("word_count", prefixes=".") & filters.me)
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
    progress: types.Message = app.send_message(msg.chat.id, "`waiting for chat history to be loaded...`")

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


@app.on_message(filters.command(["message_count", "msg_count"], prefixes=".") & filters.me)
def message_counter(_, msg):
    msg.delete()

    slf = False
    try:
        slf = "self" == msg.text.split(maxsplit=1)[1]
    except IndexError:
        pass

    total = app.get_history_count(msg.chat.id)

    name = ""
    if msg.chat.title:
        name = f" in {msg.chat.title}"
    elif msg.chat.id == MY_ID:
        pass
    elif msg.chat.first_name:
        name = f" with {msg.chat.first_name}"

    if slf:
        app.send_message("me", f"`Total amount of messages{name} is {total}`")
    else:
        app.send_message(msg.chat.id, f"`Total amount of messages{name} is {total}`")


@app.on_message(filters.command(["топ", "top"], prefixes=".") & (filters.me | filters.chat(chats=groups)))
def top(_, msg):
    msg.delete()

    if msg.from_user.id != MY_ID:
        app.send_message(msg.chat.id,
                         f"Message was automatically generated by [{msg.from_user.first_name}](tg://user?id={msg.from_user.id})",
                         parse_mode="markdown")

    slf = False

    try:
        slf = "self" == msg.text.split()[-1]
    except IndexError:
        pass

    amount = 10

    try:
        amount = msg.text.split()[1]
    except IndexError:
        pass

    limit = 1000

    try:
        limit = msg.text.split()[2]
    except IndexError:
        pass

    if limit == "all":
        limit = app.get_history_count(msg.chat.id)
    else:
        try:
            limit = int(limit)
        except ValueError:
            limit = 1000

    progress: types.Message = app.send_message(msg.chat.id, "`waiting for chat history to be loaded...`")

    top_dict = custom_dict()

    empty = ""
    total = 0
    for m in app.iter_history(msg.chat.id, limit=limit):
        total += 1
        if total % 100 == 0:
            try:
                progress.edit_text(f"`processed {total} messages...`")
            except FloodWait as e:
                sleep(e.x)

        try:
            if not m.from_user.is_bot:
                top_dict[f"{m.from_user.first_name} {m.from_user.last_name if m.from_user.last_name else empty}"] += 1
        except AttributeError:
            pass

    progress.delete()

    top_sorted = sorted(list(top_dict.items()), key=lambda x: x[1], reverse=True)

    if str(limit)[-1] == '1':
        ending = "message"
    else:
        ending = "messages"

    out = f"Most active users in {msg.chat.title} (for last {limit} {ending}):\n"

    if amount == "all":
        amount = len(top_sorted)
    else:
        try:
            amount = int(amount)
        except ValueError:
            amount = 10

    if amount > len(top_sorted):
        amount = len(top_sorted)

    for i in range(amount):
        out_one = f"   {top_sorted[i][0]}"
        while len(out_one) != 35:
            out_one += " "
        out_one += f" — {round(int(top_sorted[i][1]) / total * 100, ndigits=2)}%\n"
        out_one += "   "
        out_one += "-" * 41
        out += f"{out_one}\n"

    if slf:
        app.send_message("me", f"```{out}```", parse_mode="markdown")
    else:
        app.send_message(msg.chat.id, f"```{out}```", parse_mode="markdown")


@app.on_message(filters.command("info", prefixes=".") & filters.me)
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
