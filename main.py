import telebot
import os
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from collections import Counter

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener el token del archivo .env
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Verificar si el TOKEN esta configurado correctamente
if not TOKEN:
    raise ValueError("⚠ ERROR: No se encontro el TOKEN en el archivo .env")

# Inicializar el bot
bot = telebot.TeleBot(TOKEN)

# Definir un gestor de mensajes para los comandos /start y /help.
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, """
    Hola, soy un bot que tiene distintas funcionalidades, estos son los comandos disponibles:
    \n /count - Contar palabras o caracteres de un texto
    \n /start - Mensaje de bienvenida
    """,)

# Definir un manejador de mensajes para el comando /count
@bot.message_handler(commands=['count'])
def count(message):
	# Crear un teclado personalizado con opciones para contar palabras o caracteres
    board = ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    board.add(
		KeyboardButton("Contar palabras"), 
		KeyboardButton("Contar caracteres"),
        KeyboardButton("Palabras mas frecuentes")
	)
	# Envíar un mensaje para elegir qué contar y registrar el manejador del siguiente paso
    bot.send_message(message.chat.id, "Elige qué quieres contar:", reply_markup=board)
    bot.register_next_step_handler(message, handle_count_choice)

def handle_count_choice(message):
    # Comprobar la elección del usuario y proceder con la función correspondiente
    text = message.text.lower()

    if text == "contar palabras":
        bot.send_message(message.chat.id, "Envía el texto para contar palabras")
        bot.register_next_step_handler(message, count_words)

    elif text == "contar caracteres":
        bot.send_message(message.chat.id, "Envía el texto para contar caracteres")
        bot.register_next_step_handler(message, count_characters)

    elif text == "palabras mas frecuentes":
        bot.send_message(message.chat.id, "Envia el texto para analizar la frecuencia de palabras")
        bot.register_next_step_handler(message, count_word_frequency)

    else:
        bot.send_message(
            message.chat.id, "⚠ Opcion no valida. Usa /count para intentarlo de nuevo."
        )

# Función para contar la cantidad de palabras
def count_words(message):
   words = message.text.split()
   word_count = len(words)
   bot.reply_to(message, f"📝 El texto tiene {word_count} palabras")

# Función para contar la cantidad de caracteres
def count_characters(message):
     char_count = len(message.text)
     bot.reply_to(message, f"📝 El texto tiene {char_count} caracteres")

# Función para contar la frecuencia de palabras
def count_word_frequency(message):
    words = message.text.lower().split()
    word_counts = Counter(words)
    most_common = word_counts.most_common(5)  # Top 5 palabras

    response = "📊 Palabras más frecuentes:\n"
    for word, count in most_common:
        response += f"{word}: {count} veces\n"

    bot.reply_to(message, response)

# Definir un gestor de mensajes para textos generales
@bot.message_handler(content_types=["text"])
def hola(message):
    if message.text.lower() in ["hola", "hello", "hi"]:
        bot.send_message(
            message.chat.id,
            f"👋 Hola {message.from_user.first_name}, ¿En qué te puedo ayudar?",
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Comando no reconocido. Por favor, usa /start para revisar los comandos disponibles",
        )

# Empezar a recibir mensajes
bot.polling()
