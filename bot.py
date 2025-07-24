import asyncio 
import sqlite3
from aiogram import Bot,Dispatcher
from config import YOUR_TOKEN # Important: config.py is added to .gitignore to prevent token leakage.

bot = Bot(token=YOUR_TOKEN) # Initialize the bot using the token from config.py.
dp = Dispatcher 

# Create database
def init_db():
    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY,
                title TEXT
                done BOOLEAN
                )
                ''')
    con.commit()
    con.close()