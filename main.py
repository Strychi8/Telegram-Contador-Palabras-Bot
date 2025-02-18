import telebot
import os, io, re
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from collections import Counter
import PyPDF2
import traceback

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
    \n /count - Contar palabras, caracteres o palabras mas frecuentes de un texto
    \n /upload_file - Contar palabras, caracteres y palabras mas frecuentes de un archivo txt o pdf
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
   bot.reply_to(message, f"📝 El texto tiene {len(words)} palabras")

# Función para contar la cantidad de caracteres
def count_characters(message):
     char_count = len(message.text)
     bot.reply_to(message, f"📝 El texto tiene {char_count} caracteres")

# Función para mensajes de texto
def count_word_frequency(message):
    response = count_word_frequency_from_text(message.text)
    bot.reply_to(message, response)

# Función generica para contar la frecuencia de palabras
def count_word_frequency_from_text(text):
    words = re.findall(r'\b\w+\b', text.lower(), re.UNICODE)  # Extrae palabras
    word_counts = Counter(words)
    most_common = word_counts.most_common(5)  # Top 5 palabras mas frecuentes

    response = "📊 Palabras más frecuentes:\n"
    for word, count in most_common:
        response += f"{word}: {count} veces\n"

    return response

# Comando /upload_file para procesar archivos .txt o .pdf
@bot.message_handler(commands=['upload_file'])
def request_document(message):
    bot.send_message(message.chat.id, "📂 Envíame un archivo de texto (.txt) o un PDF (.pdf) para analizar.")
    bot.register_next_step_handler(message, handle_document_step)

# Función para procesar el archivo enviado
def handle_document_step(message):
    if not message.document:
        bot.send_message(message.chat.id, "⚠ No enviaste un documento. Usa /upload_file y envía un archivo valido.")
        return

    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Detectar extensión del archivo
        file_extension = message.document.file_name.split(".")[-1].lower()

        if file_extension == "txt":
            # Decodificar el contenido del archivo
            text = downloaded_file.decode("utf-8")
        elif file_extension == "pdf":
            text = extract_text_from_pdf(downloaded_file)
        else:
            bot.reply_to(message, "⚠ Formato no soportado. Envíame un archivo .txt o .pdf.")
            return

        # Contar palabras, caracteres y palabras mas frecuentes
        words = re.findall(r'\b\w+\b', text.lower(), re.UNICODE) 
        char_count = len(text)
        word_freq_response = count_word_frequency_from_text(text)

        # Enviar respuesta
        bot.reply_to(message, f"📄 El archivo tiene {len(words)} palabras y {char_count} caracteres.\n{word_freq_response}")
        
    except Exception as e:
        error_details = traceback.format_exc()
        bot.reply_to(message, f"⚠ Error al procesar el archivo:\n {error_details}")

# Función para extraer texto de un archivo PDF
def extract_text_from_pdf(pdf_data):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        text = f"⚠ No se pudo leer el PDF: {str(e)}"
    return text

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
