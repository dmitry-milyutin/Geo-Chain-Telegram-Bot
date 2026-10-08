import html

import telebot
from telebot import types

from config import API_TOKEN
from database import execute_db, init_db
from apis import weather_icons, get_weather, ask_ai, get_wiki_info
from game import find_city, city_info, validate_city

bot = telebot.TeleBot(API_TOKEN)

# api_hiccup, all the @bot handlers, set_commands, and the __main__ block


def api_hiccup(chatid, service):
    bot.send_message(chatid, f"Couldn't reach {service} right now, skipping that part.")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Name a city to start the game. Type /rules to see how to play.")
    retreived_data = execute_db("SELECT * FROM cities_user_data WHERE chatid = ?", (message.chat.id,))
    if not retreived_data:
        execute_db("INSERT INTO cities_user_data(chatid, score, cities) VALUES (?, 0, '[]')", (message.chat.id,))
    else:
        cities = eval(retreived_data[2])

        if cities:
            last_city = cities[-1]
            next_letter = last_city[-1].upper()
            bot.send_message(message.chat.id,f"Last city was: <b>{last_city}</b>\nYou must now name a city starting with <b>{next_letter}</b>", parse_mode="HTML")

@bot.message_handler(commands=['rules'])
def rules(message):
    rules_text = (
        "<b>How to play Cities:</b>\n"
        "1. You name a real city.\n"
        "2. I answer with a city that starts with the last letter of yours.\n"
        "3. You name a city that starts with the last letter of mine, and so on.\n"
        "4. A city can only be named once per game.\n"
        "5. You get a point for every valid city. If I can't find a city, you win!\n\n"
        "Stuck? Type /help for some suggestions."
        "Want to start over? Type /newgame."
    )
    bot.send_message(message.chat.id, rules_text, parse_mode="HTML")

@bot.message_handler(commands=['newgame'])
def new_game(message):
    retreived_data = execute_db("SELECT * FROM cities_user_data WHERE chatid = ?", (message.chat.id,))
    if not retreived_data:
        bot.send_message(message.chat.id, "Type /start to begin the game.")
        return

    execute_db("UPDATE cities_user_data SET score = 0, cities = '[]' WHERE chatid = ?", (message.chat.id,))
    bot.send_message(message.chat.id, "New game started! Name any city to begin.")
@bot.message_handler(commands=['help'])

def help(message):
    retreived_data = execute_db("SELECT * FROM cities_user_data WHERE chatid = ?", (message.chat.id,))
    if retreived_data:
        cities = eval(retreived_data[2])

        if cities:
            last_city = cities[-1]
            last_letter = last_city[-1]
        else:
            bot.send_message(message.chat.id, "There has not been a city named yet, I cannot help you.")
            return

        content = ask_ai(f"Name three cities starting with the letter {last_letter}, do not use bold text, only respond with the city names, and here is the list of cities that has already been named so you don't name those : {cities} ")
        if content:
            bot.send_message(message.chat.id, content)
        else:
            bot.send_message(message.chat.id, "The AI helper is busy right now, try /help again in a minute.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chatid = message.chat.id
    text = message.text.strip()
    text = text[0].upper() + text[1:]

    retreived_data = execute_db("SELECT cities FROM cities_user_data WHERE chatid = ?", (chatid,))
    if not retreived_data:
        bot.send_message(chatid, "Type /start to begin the game.")
        return

    cities = eval(retreived_data[0])
    validation = validate_city(text, cities)
    if validation:
        bot.send_message(chatid, validation)
        return

    execute_db("UPDATE cities_user_data SET score = score + 1 WHERE chatid = ?", (chatid,))
    bot.send_message(chatid, f"Your city: {text}\nMy city will start with: {text[-1]}")
    cities.append(text)

    bot_city = find_city(text[-1], cities)
    if not bot_city:
        score = execute_db("SELECT score FROM cities_user_data WHERE chatid = ?", (chatid,))[0]
        bot.send_message(chatid, f"I lost, there were {len(cities)} cities named during our round.\nYour final score: {score}")
        execute_db("UPDATE cities_user_data SET score = 0, cities = '[]' WHERE chatid = ?", (chatid,))
        return

    cities.append(bot_city)

    latitude_1, longitude_1, population_1, countrycode_1 = city_info(text)
    bot.send_message(chatid, f"Your city is located here ({countrycode_1})\nPopulation: {population_1}")
    bot.send_location(chatid, latitude_1, longitude_1)

    latitude, longitude, population, countrycode = city_info(bot_city)
    weather = get_weather(latitude, longitude)

    if weather:
        temp, feels_like, main, sea_level, clouds, emoji_id = weather
        bot.send_message(chatid, f"My city is {bot_city}, {countrycode}\nPopulation: {population}\n<b>Conditions: {main}  {weather_icons.get(emoji_id, '')}</b>\n\t\t\tTemperature ~ {temp}°C\n\t\t\tFeels Like ~ {feels_like}°C\n\t\t\tSea Level: {sea_level}\n\t\t\tClouds: {clouds}", parse_mode='HTML')
    else:
        bot.send_message(chatid, f"My city is {bot_city}, {countrycode}\nPopulation: {population}")
        api_hiccup(chatid, "the weather service")
    bot.send_location(chatid, latitude, longitude)

    execute_db("UPDATE cities_user_data SET cities = ? WHERE chatid = ?", (str(cities), chatid))

    summary, url = get_wiki_info(bot_city)
    if summary:
        # send html page as preivous text gandling didn't work with wiki
        bot.send_message(chatid, f"<b>About {bot_city}:</b>\n{html.escape(summary)}", parse_mode="HTML")
        bot.send_message(chatid, f"More info: {url}")
    else:
        bot.send_message(chatid, f"Couldn't find Wikipedia info for {bot_city}.")

    score = execute_db("SELECT score FROM cities_user_data WHERE chatid = ?", (chatid,))[0]
    bot.send_message(chatid, f"Score: {score}")

if __name__ == "__main__":
    init_db()
    print("Bot is running...")
    bot.infinity_polling()