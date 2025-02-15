import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from bot import Bot  # Ensure this is correctly set up in your bot

# IMDb URLs
IMDB_TOP_MOVIES_URL = "https://www.imdb.com/chart/top/"
IMDB_TRENDING_MOVIES_URL = "https://www.imdb.com/chart/moviemeter/"
IMDB_SEARCH_URL = "https://www.imdb.com/find?q={query}&s=tt"

# Function to fetch and parse IMDb pages
def fetch_imdb_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

# Function to get top movies from IMDb
def get_top_movies():
    soup = fetch_imdb_page(IMDB_TOP_MOVIES_URL)
    movies = []
    
    for row in soup.select("tbody.lister-list tr")[:10]:  # Get top 10 movies
        title_column = row.select_one(".titleColumn a")
        rating_column = row.select_one(".imdbRating strong")
        
        if title_column and rating_column:
            title = title_column.text
            url = f"https://www.imdb.com{title_column['href']}"
            rating = rating_column.text
            movies.append({"title": title, "url": url, "rating": rating})
    
    return movies

# Function to get trending movies
def get_trending_movies():
    soup = fetch_imdb_page(IMDB_TRENDING_MOVIES_URL)
    movies = []

    for row in soup.select("tbody.lister-list tr")[:10]:  # Get top 10 trending movies
        title_column = row.select_one(".titleColumn a")
        rating_column = row.select_one(".imdbRating strong")

        if title_column:
            title = title_column.text
            url = f"https://www.imdb.com{title_column['href']}"
            rating = rating_column.text if rating_column else "N/A"
            movies.append({"title": title, "url": url, "rating": rating})
    
    return movies

# Function to search for a movie on IMDb
def search_movie(query):
    soup = fetch_imdb_page(IMDB_SEARCH_URL.format(query=query.replace(" ", "+")))
    movies = []

    for row in soup.select(".findList .findResult")[:10]:  # Get top 10 search results
        title_column = row.select_one(".result_text a")

        if title_column:
            title = title_column.text
            url = f"https://www.imdb.com{title_column['href']}"
            movies.append({"title": title, "url": url})
    
    return movies

# Function to style movie titles
def style_movie_title(title):
    return f"**{title}**".replace("A", "𝔸").replace("B", "𝔹").replace("C", "ℂ").replace("D", "𝔻").replace("E", "𝔼").replace("F", "𝔽").replace("G", "𝔾").replace("H", "ℍ").replace("I", "𝕀").replace("J", "𝕁").replace("K", "𝕂").replace("L", "𝕃").replace("M", "𝕄").replace("N", "ℕ").replace("O", "𝕆").replace("P", "ℙ").replace("Q", "ℚ").replace("R", "ℝ").replace("S", "𝕊").replace("T", "𝕋").replace("U", "𝕌").replace("V", "𝕍").replace("W", "𝕎").replace("X", "𝕏").replace("Y", "𝕐").replace("Z", "ℤ")

# Command to get top movies
@Bot.on_message(filters.command('top_movies') & filters.private)
async def top_movies_command(client: Client, message: Message):
    movies = get_top_movies()
    if not movies:
        await message.reply("No top movies found at the moment.")
        return

    keyboard = [[InlineKeyboardButton(f"{style_movie_title(movie['title'])} ⭐ {movie['rating']}", url=movie['url'])] for movie in movies]
    keyboard.append([InlineKeyboardButton("✖️✨ 𝕮𝖑𝖔𝖘𝖊 ✨✖️", callback_data='close')])

    await message.reply_text(
        "🎬 *Top Movies on IMDb* 🎬",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# Command to get trending movies
@Bot.on_message(filters.command('trending_movies') & filters.private)
async def trending_movies_command(client: Client, message: Message):
    movies = get_trending_movies()
    if not movies:
        await message.reply("No trending movies found at the moment.")
        return

    keyboard = [[InlineKeyboardButton(f"{style_movie_title(movie['title'])} ⭐ {movie['rating']}", url=movie['url'])] for movie in movies]
    keyboard.append([InlineKeyboardButton("✖️✨ 𝕮𝖑𝖔𝖘𝖊 ✨✖️", callback_data='close')])

    await message.reply_text(
        "🔥 *Trending Movies on IMDb* 🔥",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# Command to search for a movie
@Bot.on_message(filters.command('search_movie') & filters.private)
async def search_movie_command(client: Client, message: Message):
    query = " ".join(message.text.split()[1:])
    if not query:
        await message.reply("Please provide a movie name to search.")
        return

    movies = search_movie(query)
    if not movies:
        await message.reply("No movies found for the search query.")
        return

    keyboard = [[InlineKeyboardButton(f"{style_movie_title(movie['title'])}", url=movie['url'])] for movie in movies]
    keyboard.append([InlineKeyboardButton("✖️✨ 𝕮𝖑𝖔𝖘𝖊 ✨✖️", callback_data='close')])

    await message.reply_text(
        f"🔍 *Search Results for '{query}'* 🔍",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

# Callback handler for close button
@Bot.on_callback_query()
async def callback_query_handler(client: Client, callback_query: CallbackQuery):
    if callback_query.data == 'close':
        await callback_query.message.delete()
