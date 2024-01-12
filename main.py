import os
#from flask import Flask, request
from pymongo import MongoClient
import telebot
from telebot.types import *
from telebot import custom_filters
from OpsAi import Ai
import requests
import PyPDF2
import os
import tempfile, datetime, time, math 
from gtts import gTTS
#from googletrans import LANGCODES, Translator
from mtranslate import translate

languages = []#list(LANGCODES.items())
languages.append(("English","en"))
languages.append(("Oromic","om"))
languages.append(("Amharic","am"))
languages.append(("Tigrigna","ti"))
languages.append(("German","de"))
languages.append(("Hindi","hi"))
languages.append(("Arabic","ar"))
languages.append(("French","fr"))

TOKEN = "5714196179:AAHOHc9e64kAbQ6zH4dlQEAJhjVAleKGX0I"
bot = telebot.TeleBot(TOKEN, parse_mode="html")
#server = Flask(__name__)


channel = ["@mt_projectz"]

def check_sub(message):
    for i in channel:
        a = bot.get_chat_member(i, message.from_user.id)
        if a.status == "left":
            return False
    return True

users = []

admin = [1365625365, 1170583016, 6118912816]

buttons = ["🧑‍💻Ask Code🧑‍💻", "🤖Explain Code🤖", "🌀Generate Images🌀", "⚙️Image Settings⚙️", "🎧Text To Voice🎧", "📑Ask PDF📑", "📸Ask Photo📸", "🌍Language🌍"]

markup = InlineKeyboardMarkup()
ma = InlineKeyboardButton("🕹Join My Updates🕹", url="t.me/mt_projectz")
markup.add(ma)

back = ReplyKeyboardMarkup(resize_keyboard=True)
back.add("⏪Back")

client = MongoClient("mongodb+srv://really651:gSPMW6u9WuStXIwD@cluster0.pxc2foz.mongodb.net/?retryWrites=true&w=majority")

db = client["Products"]
collection = db["coll"]

def markups():
    btns = []
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for btn in buttons:
        btns.append(KeyboardButton(btn))
    markup.add(*btns)
    markup.add("❤Donate💛")
    return markup

def ask_coder(message, text):
    bot.send_chat_action(message.chat.id, "typing")
    try:
        s = Ai(query = text)
        cd = s.code()
        return bot.send_message(message.chat.id, cd, parse_mode="MARKDOWN")
    except:
        bot.send_message(message.chat.id, "Ohh, Dear Programmer, Something went wrong!\nPlease Try Again Later:)")

testbtn = InlineKeyboardMarkup()
testbtn.add(InlineKeyboardButton("🎧Let me hear this text🎧", callback_data="voice"))

@bot.inline_handler(lambda query: True)
def inline_query(query):    
    result = InlineQueryResultArticle(
        id='1',
        title="Channel Membership Required!",
        description="Before using this bot, kindly Join Our Channel:)",
        input_message_content=InputTextMessageContent(f"⚠️{query.from_user.first_name} before using this bot, kindly Join Our Channel👇"),
        reply_markup=markup
    )

    if bot.get_chat_member("@mt_projectz", query.from_user.id).status == "left":
        return bot.answer_inline_query(query.id, [result],
                                       button=InlineQueryResultsButton(text="Click here to Join:)",
                                                                      start_parameter="start"),
                                       cache_time=1, is_personal=True)
    photo_urls = []
    response = requests.get(f"https://lexica.art/api/v1/search?q={query.query}")
    data = response.json()  
    for image in data["images"]:
        if image["nsfw"] is not True:        	
            photo_urls.append(image["src"])
            if len(photo_urls) == 10:
                break 
    results = []
    for i, src in enumerate(photo_urls):
        results.append(
            telebot.types.InlineQueryResultPhoto(
                id=str(i),
                photo_url=src,
                thumbnail_url=src
            )
        )       

    bot.answer_inline_query(query.id, results,
                            button=InlineQueryResultsButton(text="Generate Images:",
                                                            start_parameter="start"),
                            is_personal=True)

def render_chat(message, text, lang):
    try:
        s = Ai(query = text)
        cd = s.chat()
        res = translate(cd, lang)
        return bot.reply_to(message, res, parse_mode ="MARKDOWN", reply_markup=testbtn)
    except Exception as e:
        bot.send_message(message.chat.id, "Ohh, Something went wrong!\nPlease Try Again Later:)")

def render_chat_gt(message, text, lang):
    try:
        s = Ai(query = text)
        cd = s.chat()
        res = translate(cd, lang)
        return bot.reply_to(message, res, parse_mode ="MARKDOWN",reply_markup=testbtn)		
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "Ohh, Something went wrong!\nPlease Try Again Later:)")

def ask_chat(message, text):
    #bot.send_message(-1001882951482, f"username: {message.from_user.username}\nfirst-name: {message.from_user.first_name}\nprompt: {text}")
    bot.send_chat_action(message.chat.id, "typing")
    user = collection.find_one({"user_id": message.from_user.id})
    lang = user["lang"]
    if lang == "om" or lang == "ti":
        data = translate(text, "en")
        return render_chat(message=message, text=data, lang=lang)
    else:
        data = translate(text, "en")
        return render_chat_gt(message=message, text=data, lang=lang)

def ex_coder(message, text):
    bot.send_chat_action(message.chat.id, "typing")
    try:
        s = Ai(query = text)
        cd = s.explain()
        return bot.send_message(message.chat.id, cd, parse_mode="MARKDOWN")
    except:
        bot.send_message(message.chat.id, "Ohh, Dear Programmer, Something went wrong!\nPlease Try Again Later:)")

def convert_pdf_to_text(pdf_path, message):
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    pdf_file.close()

    return ask_chat(message, text)


@bot.message_handler(commands = ["stats"])
def sats(message):
    users = list(collection.find())
    count = len(users)
    if message.chat.id in admin:
        bot.send_message(message.chat.id, f"Total Users: {count}")
    else:
        pass

cancelb = ReplyKeyboardMarkup(resize_keyboard=True)
cancelb.add("❌Cancel")

@bot.message_handler(func = lambda message: True, state="broadcast")
def cast_state(message):
    if message.text == "❌Cancel":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        bot.delete_state(message.from_user.id, message.chat.id)
        users = collection.find({})
        for i in users:
            user = i["user_id"]
            try:
                bot.send_message(user, message.text, parse_mode ="html")
            except:
                pass

@bot.message_handler(commands =["broadcast"])
def broadcast(message):
    if message.chat.id in admin:
        bot.set_state(message.from_user.id, "broadcast", message.chat.id)
        bot.send_message(message.chat.id, "📥Send me a message to be sent to users || ❌Cancel", reply_markup=cancelb)


def welcome(message):
    return bot.send_message(message.from_user.id, f"{message.from_user.first_name}, Hello and welcome to poweful ChatGPT Bot👋\n\n<b>This bot can help you to do so many things and it\'s completely free🌀</b>\n\n<i>✨Select an option below or Just Ask me questions directly👇</i>", reply_markup=markups())		

@bot.message_handler(commands=["start"], chat_types=["private"])
def start(message):
    user = collection.find_one({"user_id": message.from_user.id})
    state = bot.get_state(message.from_user.id, message.chat.id)
    if state:
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        pass
    if user:
        if not "is_gallery" or "lang" in user:
            collection.update_one({"user_id": message.from_user.id}, {"$set": {"is_gallery": False, "lang": "en"}})
            return welcome(message)
        #if bot.get_chat_member("@mt_projectz", message.from_user.id).status != "left":
            #bot.send_message(message.chat.id, f"{message.from_user.first_name}, Hello and welcome to poweful ChatGPT Bot👋\n\n<b>This bot can help you to do so many things and it\'s completely free🌀</b>\n\n<i>✨Select an option below or Just Ask me questions directly👇</i>", reply_markup=markups())
        else:
            #pass
            return welcome(message)
            #bot.send_message(message.chat.id, f"⚠️{message.from_user.first_name} before using this bot, kindly Join Our Channel👇", reply_markup=markup)
    else:
        collection.insert_one({"user_id": message.from_user.id, "is_premium": False, "is_gallery": False, "lang": "en"})
        return welcome(message)
        #if bot.get_chat_member("@mt_projectz", message.from_user.id).status != "left":
            #bot.send_message(message.chat.id, f"{message.from_user.first_name}, Hello and welcome to poweful ChatGPT Bot👋\n\n<b>This bot can help you to do so many things and it\'s completely free🌀</b>\n\n<i>✨Select an option below or Just Ask me questions directly👇</i>", reply_markup=markups())
        #else:
            #bot.send_message(message.chat.id, f"⚠️{message.from_user.first_name} before using this bot, kindly Join Our Channel👇", reply_markup=markup)

def answer_photo(message):
    b = bot.reply_to(message,"✨Reading what you sent....")
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)    
    api_key = 'K81164834388957'
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'apikey': api_key,
        'language': 'eng',
        'isOverlayRequired': False
    }
    files = {
        'filename': ('image.jpg', downloaded_file, 'image/jpeg')
    }
    response = requests.post(url, data=payload, files=files)
    if response.status_code == 200:
        response_data = response.json()
        if response_data['IsErroredOnProcessing']:
            error_message = response_data['ErrorMessage']
            bot.send_message(message.chat.id, f'Error: {error_message}\nReport to @MT_ProjectzChat')
        else:
            extracted_text = response_data['ParsedResults'][0]['ParsedText']
            bot.delete_message(message.chat.id, b.id)
            ask_chat(message, extracted_text)
    else:
        bot.send_message(message.chat.id, 'Error: Report to @MT_ProjectzChat')

def answer_pdf(message):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        if message.document.file_name.endswith('.pdf'):          
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.write(downloaded_file)
            temp.close()          
            text = convert_pdf_to_text(temp.name, message)                   
            os.unlink(temp.name)
    except Exception as e:
        bot.reply_to(message, f'Oops, something went wrong. Error: {e}NB: Only PDF format is supported!')	

def generate_gallery(text):
    photos = []
    album = []
    response = requests.get(f"https://lexica.art/api/v1/search?q={text}")
    data = response.json() 
    for image in data["images"]:
         if image["nsfw"] is not True:
           photos.append(image)
           if len(photos) == 10:
            break
    for img in photos:
        album.append(InputMediaPhoto(img["gallery"]))  
    return album

def voice(text, chat_id):
    bot.send_chat_action(chat_id, "upload_voice")
    tts = gTTS(text=text, lang='en')
    tts.save('voice.mp3')  
    with open('voice.mp3', 'rb') as voice:
        bot.send_voice(chat_id, voice, reply_markup=markups(), caption="Generated by @ChatGPT_v4_Robot ")  
    os.remove('voice.mp3')

crypto = """
<b>❤Donate the developer to encourage for new features via Crypto:💚</b>

<b>Bitcoin</b>: <code>17mBRrYZQtFwfHDdDAe6HtGdAc8TmZMKQA</code>

<b>USDT(TRC20)</b>: <code>TV6FUqCKGUq7SE4K2S3X19uc8te1uLYU5T</code>

<b>Binance Coin</b>: <code>0x8cF185cBF72E40b1B5B6DFdFAb2E5CB19175b22a</code>

<b>Tron(TRX)</b>: <code>TV6FUqCKGUq7SE4K2S3X19uc8te1uLYU5T</code>

<i>🌍For others payment methods contact the admin - @BetterParrot:)</i>
"""

inline = InlineKeyboardMarkup()
inline.add(InlineKeyboardButton("📝Try Inline Search📝", switch_inline_query_current_chat="Goat"))

def generate_src(text):
    photos = []
    album = []
    response = requests.get(f"https://lexica.art/api/v1/search?q={text}")
    data = response.json() 
    for image in data["images"]:
         if image["nsfw"] is not True:
           photos.append(image)
           if len(photos) == 10:
            break
    for img in photos:
        album.append(InputMediaPhoto(img["src"]))  
    return album

def render_src(text, chat_id):
    bot.send_chat_action(chat_id, "upload_photo")
    data = {
        "user_id": chat_id,
        "time": time.time()}
    try:
        album = generate_src(text)
        bot.send_media_group(chat_id, album)
        users.append(data)
    except Exception as e:        
        bot.send_message(chat_id, "The image couldn't be generated.")

def render_gallery(text, chat_id):
    bot.send_chat_action(chat_id, "upload_photo")
    data = {
        "user_id": chat_id,
        "time": time.time()}
    try:
        album = generate_gallery(text)
        bot.send_media_group(chat_id, album)
        users.append(data)
    except Exception as e:        
        bot.send_message(chat_id, "The image couldn't be generated.")

@bot.message_handler(content_types=["text"], state="ask_code")
def ask_code_state(message):
    data = {
        "user_id": message.from_user.id,
        "time": time.time()
    }
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        user_time = [usr for usr in users if usr["user_id"] == data["user_id"]]
        if user_time:
            if time.time() - user_time[0]["time"] >= 30:
                user_time[0]["time"] = time.time()
                bot.send_message(-1001882951482, f"username: {message.from_user.username}\nfirst-name: {message.from_user.first_name}\nprompt: {message.text}")
                return ask_coder(message, message.text)         
            else:
                limit = time.time() - user_time[0]["time"]
                time_limit = 30 - limit
                return bot.send_message(message.chat.id, f"Please wait {math.floor(time_limit)} seconds before asking another code.")
        else:
            users.append(data)
            return ask_coder(message, message.text)

@bot.message_handler(content_types=["text"], state="ex_code")
def ex_code_state(message):
    data = {
        "user_id": message.from_user.id,
        "time": time.time()
    }
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        user_time = [usr for usr in users if usr["user_id"] == data["user_id"]]
        if user_time:
            if time.time() - user_time[0]["time"] >= 10:
                user_time[0]["time"] = time.time()
                #bot.send_message(-1001882951482, f"username: {message.from_user.username}\nfirst-name: {message.from_user.first_name}\nprompt: {message.text}")
                return ex_coder(message, message.text)         
            else:
                limit = time.time() - user_time[0]["time"]
                time_limit = 10 - limit
                return bot.send_message(message.chat.id, f"Please wait {math.floor(time_limit)} seconds before making another request.")
        else:
            users.append(data)
            return ex_coder(message, message.text)

@bot.message_handler(content_types =["document"], state="pdf")
def resp_pdf(message):
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        bot.delete_state(message.from_user.id, message.chat.id)
        return answer_pdf(message)

@bot.message_handler(content_types =["text"], state="pdf")
def resp_pdf3(message):
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)

@bot.message_handler(content_types =["text"], state="voice")
def resp_pdf4(message):
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        bot.delete_state(message.from_user.id, message.chat.id)
        return voice(message.text, message.from_user.id)  

@bot.message_handler(content_types =["text"], state="photo")
def resp_pdf1(message):
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)               

@bot.message_handler(content_types =["photo"], state="photo")
def resp_pdf2(message):
    if message.text == "⏪Back":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        bot.delete_state(message.from_user.id, message.chat.id)
        return answer_photo(message)

@bot.message_handler(content_types=["text"], state="generate_image")
def generate_img(message):
    data = {
        "user_id": message.from_user.id,
        "time": time.time()
    }
    if message.text == "⏪Back" or message.text == "/start":
        bot.delete_state(message.from_user.id, message.chat.id)
        return welcome(message)
    else:
        user = collection.find_one({"user_id": message.from_user.id})
        user_time = [usr for usr in users if usr["user_id"] == data["user_id"]]
        if user_time:
            if time.time() - user_time[0]["time"] >= 10:
                user_time[0]["time"] = time.time()
                if user["is_gallery"]:                 
                    return render_gallery(message.text, message.from_user.id)
                else:                
                    return render_src(message.text, message.from_user.id)
            else:
                limit = time.time() - user_time[0]["time"]
                time_limit = 10 - limit
                return bot.send_message(message.chat.id, f"Please wait {math.floor(time_limit)} seconds before asking another question.")
        else:
            users.append(data)
            if user["is_gallery"]:
               return render_gallery(message.text, message.from_user.id)
            else:
                return render_src(message.text, message.from_user.id)


img_type = InlineKeyboardMarkup(row_width=2)
i1 = InlineKeyboardButton("📸Single Images📸", callback_data="single")
i2 = InlineKeyboardButton("🗞Gallery Images🗞", callback_data="gallery")
i3 = InlineKeyboardButton("❌Cancel", callback_data="cancel")
img_type.add(i1, i2, i3)


@bot.message_handler(content_types =["text"], chat_types =["private"])
def resp(message):
    user = collection.find_one({"user_id": message.from_user.id})
    if not "lang" in user:
        return collection.update_one({"user_id": message.from_user.id}, {"$set": {"is_gallery": False, "lang": "en"}})
    else:
        pass
    #if bot.get_chat_member("@mt_projectz", message.from_user.id).status == "left":
        #return bot.send_message(message.chat.id, f"⚠️{message.from_user.first_name} before using this bot, kindly Join Our Channel: @Mt_Projectz")
    data = {
        "user_id": message.from_user.id,
        "time": time.time()
    }    
    if message.text == "🧑‍💻Ask Code🧑‍💻":
        bot.set_state(message.from_user.id, "ask_code", message.chat.id)
        return bot.send_message(message.chat.id, "What do you wanna me to code for you:", reply_markup=back)
    if message.text == "🌀Generate Images🌀":
        bot.set_state(message.from_user.id, "generate_image", message.chat.id)
        bot.send_message(message.chat.id, "What do you wanna me to Imagine:", reply_markup=back)
        return bot.send_message(message.chat.id, "<i>You can also use Inline mode</i>", reply_markup=inline)
    if message.text == "⚙️Image Settings⚙️":
        return bot.send_message(message.chat.id, "Choose Images format:", reply_markup = img_type)  
    if message.text == "🤖Explain Code🤖":
        bot.set_state(message.from_user.id, "ex_code", message.chat.id)
        return bot.send_message(message.chat.id, "Just send me a code, i\'ll explain as much as I can:", reply_markup=back)
    if message.text == "📑Ask PDF📑":
        bot.set_state(message.from_user.id, "pdf", message.chat.id)
        return bot.send_message(message.chat.id, "Just upload your PDF, i\'ll analyse it:", reply_markup=back)
    if message.text == "📸Ask Photo📸":
        bot.set_state(message.from_user.id, "photo", message.chat.id)
        return bot.send_message(message.chat.id, "Just send your photo, i\'ll analyse it:", reply_markup=back)
    if message.text == "🎧Text To Voice🎧":
        bot.set_state(message.from_user.id, "voice", message.chat.id)
        return bot.send_message(message.chat.id, "Just send your some text, i\'ll convert it to voice:", reply_markup=back)
    if message.text == "🌍Language🌍": 	
        buttons = []
        markup = InlineKeyboardMarkup(row_width=2)
        for btn in languages[:10]:
            buttons.append(InlineKeyboardButton(btn[0].title(), callback_data=btn[1]))
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("🔙Go Back", callback_data="cancel"), InlineKeyboardButton("⏩", callback_data="page_2"))
        return bot.send_message(message.chat.id, "Choose your language🌍", reply_markup=markup)
    if message.text == "❤Donate💛":
        return bot.send_message(message.chat.id, crypto)
    if message.text == "⏪Back":
        return welcome(message)
    else:        
        user_time = [usr for usr in users if usr["user_id"] == data["user_id"]]
        if user_time:
           if time.time() - user_time[0]["time"] >= 10:
                user_time[0]["time"] = time.time()
                return ask_chat(message, message.text)
           else:
                limit = time.time() - user_time[0]["time"]
                time_limit = 10 - limit
                return bot.send_message(message.chat.id, f"Please wait {math.floor(time_limit)} seconds before asking another question.")
        else:
            users.append(data)
            return ask_chat(message, message.text)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith("page_"))
def handle_callback_query(callback):  
    page = int(callback.data.split("_")[1])
    start_index = (page - 1) * 10
    end_index = start_index + 10
    page_items = languages[start_index:end_index]
    buttons = []
    markup = InlineKeyboardMarkup(row_width=2)
    for item in page_items:
        buttons.append(InlineKeyboardButton(item[0].title(), callback_data=item[1]))   
    if page > 1:        
        buttons.append(InlineKeyboardButton("⏪", callback_data=f"page_{page - 1}"))
    if end_index < len(languages):
        buttons.append(InlineKeyboardButton("⏩", callback_data=f"page_{page + 1}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙Go Back", callback_data="cancel"))
    bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func = lambda callback: True)
def ans_callback(callback):
    donate = InlineKeyboardMarkup()
    donate.add(InlineKeyboardButton("❤Donate❤", callback_data="donate"))
    if callback.data == "single":
        collection.update_one({"user_id": callback.from_user.id}, {"$set": {"is_gallery": False}})
        return bot.edit_message_text(chat_id = callback.message.chat.id, message_id = callback.message.message_id, text="📸The format of image is changed to Single Images📸")
    if callback.data == "gallery":
        collection.update_one({"user_id": callback.from_user.id}, {"$set": {"is_gallery": True}})
        return bot.edit_message_text(chat_id = callback.message.chat.id, message_id = callback.message.message_id, text="📸The format of image is changed to Gallery Images📸")
    if callback.data == "cancel":
        return bot.edit_message_text(chat_id = callback.message.chat.id, message_id = callback.message.message_id, text=f"❌Cancelled.")
    if callback.data == "donate":
        menu = InlineKeyboardMarkup()
        menu.add(InlineKeyboardButton("🔙Back to menu", callback_data="menu"))
        return bot.edit_message_text(chat_id = callback.message.chat.id, message_id = callback.message.message_id, text=crypto, reply_markup=menu)
    if callback.data == "menu":
        bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        return welcome(callback)
    if callback.data == "voice":
        bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)
        return voice(callback.message.text, callback.message.chat.id)
    else:		
        collection.update_one({"user_id": callback.from_user.id}, {"$set": {"lang": callback.data}})
        return bot.edit_message_text(chat_id = callback.message.chat.id, message_id = callback.message.message_id, text=f"Great, I\'ll answer your questions by this language🌍", reply_markup = donate)

bot.add_custom_filter(custom_filters.StateFilter(bot))

print("Successful")
bot.delete_webhook()
bot.infinity_polling()

"""@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://flask1.tolasaa.repl.co/' + TOKEN, drop_pending_updates=True)
    return "ok", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))"""
