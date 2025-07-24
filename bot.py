import asyncio 
import sqlite3
from aiogram import Bot,Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command 
from aiogram.fsm.storage.memory import MemoryStorage # connect the module state storage in RAM
from aiogram.fsm.state import State, StatesGroup
from config import YOUR_TOKEN # Important: config.py is added to .gitignore to prevent token leakage.

bot = Bot(token=YOUR_TOKEN) # Initialize the bot using the token from config.py.
storage = MemoryStorage() # in-memory state store
dp = Dispatcher(storage=storage) # bind storage to the manager


class TaskStates(StatesGroup): # Condition for FSM
    waiting_for_task = State()
    waiting_for_id = State()

def get_main_menu(): # main menu with build-in button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="add task", callback_data="add_task")],
    [InlineKeyboardButton(text="delete task", callback_data="delete_task")],
    [InlineKeyboardButton(text="completed", callback_data="completed")],
    [InlineKeyboardButton(text="list task", callback_data="list_task")],
    ])

def init_db(): # Create database
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
