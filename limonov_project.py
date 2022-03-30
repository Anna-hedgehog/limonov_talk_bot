import telebot
import os
import re 
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE

"""### **Сначала подготовим тексты**

Собираем всё в один файл:
"""

text = ""
for book in os.listdir("/home/annushkaLimonova/limonov_talk_bot/limonov_books/"):
   texts = open(os.path.join("/home/annushkaLimonova/limonov_talk_bot/limonov_books/", book), 'r', encoding='utf-8')
   for line in texts:
       text += line
   texts.close()

"""Собираем список предложений, разбитый на слова:"""

lim_text = [word_tokenize(sent) for sent in sent_tokenize(text)]

"""### **Теперь займёмся созданием генератора:**

Создаём 5-граммы:
"""

n = 5
train, sents = padded_everygram_pipeline(n, lim_text)

"""создаём и тренируем модель:"""

lim_model = MLE(n) 
lim_model.fit(train, sents)

"""функция генерации:


"""

from nltk.tokenize.treebank import TreebankWordDetokenizer

detokenize = TreebankWordDetokenizer().detokenize

def generate_sent(model, text_seed):
    content = []
    for token in model.generate(1000, text_seed=text_seed):
        if token == '<s>':
            continue
        if token == '</s>':
            break
        content.append(token)
    return detokenize(content)

"""### **Теперь подключаем бота:**"""

bot = telebot.TeleBot("5261158647:AAHf4BhORbSOIRn2UdihGagTVQeT92F52Gw", parse_mode=None)

"""Сразу создаём словарь состояний пользователя:"""

dict_users_states = {}

"""Кнопочная панель:"""

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row("Хай!", "идите вы, дед, куда подальше","/help", "пройди опрос, насколько я, это я")

"""Реакция бота на команды:"""

@bot.message_handler(commands=["start"])
def send_welcome(message):
	bot.reply_to(message, "Хай, поболтаем? /start", reply_markup=keyboard1)
 
@bot.message_handler(commands=["help"])
def bot_messages(message):
    text = "Что я могу?\nНапиши мне слово или словосочентание, а я найду, что ответить.\n\nP.s.НЕ ИСПОЛЬЗУЙ ЗНАКИ ПУНКТУАЦИИ!"
    bot.send_message(message.chat.id, text)

"""Сгенерированный ответ и интерактив (картиночки в ответ):"""

path_photo_1 = "/home/annushkaLimonova/limonov_talk_bot/lb.jpg"
path_photo_2 = "/home/annushkaLimonova/limonov_talk_bot/lh.jpg"

@bot.message_handler(content_types=["text"])
def send_text(message):
   if message.text == "пройди опрос, насколько я, это я":
       bot.send_poll(update.message.chat_id, 'Я тот самый дед?', options=['да', 'нет'])
   elif dict_users_states.get(message.chat.id) != "stop_now_word":
     if message.text == "идите вы, дед, куда подальше":
       bot.send_photo(message.chat.id, photo=open(path_photo_1, "rb"))
     elif message.text == "Хай!":
       bot.send_photo(message.chat.id, photo=open(path_photo_2, "rb"))
     else:
       word_from_user = message.text
       gen_text = generate_sent(lim_model, list(word_from_user))  #подключаем генератор через функцию
       gen_text = re.sub("<.*>", "", gen_text)   #не очень чистый момент, очистка результата от случайно попавших файловых тегов
       bot.send_message(message.chat.id, gen_text)

bot.polling()
