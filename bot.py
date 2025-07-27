import asyncio 
import sqlite3 # Connecting the built-in library sqlite3 for storing data in the database
from aiogram import Bot,Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
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

def init_db(): # Create database
    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                user_name TEXT,
                task_name TEXT,
                is_completed BOOLEAN DEFAULT FALSE
                )
                ''')
    con.commit()
    con.close()

def get_main_menu(): # main menu with build-in button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="add task", callback_data="add_task")],
        [InlineKeyboardButton(text="delete task", callback_data="delete_task")],
        [InlineKeyboardButton(text="completed", callback_data="completed")],
        [InlineKeyboardButton(text="list task", callback_data="list_task")],
    ])
    return keyboard

@dp.message(Command("start"))#
async def start_handler(message:Message): # start command handler
    user_name = message.from_user.first_mame
    welcom_text = f"👋Hi {user_name}, a`m a simple task manager.\nManage your time."

    await message.answer(welcom_text, reply_markup=get_main_menu)

@dp.callback_query(lambda c: c.data == "add_task")
async def add_task_handler(callback: CallbackQuery, state: FSMContext): # add task command handler
    await callback.message.edit_text("📑Enter a name for the name task")
    await state.set_state(TaskStates.waiting_for_task)
    await callback.answer()


@dp.message(TaskStates.waiting_for_task)
async def save_task(message: Message, state: FSMContext): # Getting the task text and saving it to the database
    user_name = message.from_user.username
    user_id = message.from_user.id
    task_name = message.text

    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute("INSERT INTO tasks (user_name, user_id, task_name) VALUES (?, ?, ?)",
                   (user_name, user_id, task_name))
    con.commit()
    con.close()

    await message.answer(f"Task {task_name} added", reply_markup=get_main_menu())
    await state.clear()


@dp.callback_query(lambda c: c.data == "list_task")
async def show_task_handler(callback: CallbackQuery ): # function shows all tasks
    user_id = callback.from_user.id
    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute("SELECT id, task_name, is_completed FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cur.fetchall()
    con.close()
    if not tasks:
        await callback.message.edit_text("📑You have no tasks", reply_markup=get_main_menu())
    else:
        text = "📑Your Tasks:"
        for task_id, task_name, is_completed in tasks:
            status = "✅" if is_completed else "⏳"
            text += f"\n\n{status} {task_id} {task_name} {is_completed}"

        await callback.message.edit_text(text, reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(lambda c: c.data == "delete_task")
async def delete_task_handler(callback: CallbackQuery, state: FSMContext): # handler function sets the FSM status
    await callback.message.edit_text(f"📑Enter the number of the task you want to delete:")
    await state.set_state(TaskStates.waiting_for_id)
    await callback.answer()

@dp.message(TaskStates.waiting_for_id)
async def delete_task(message: Message, state: FSMContext): # the function deletes a task from the db. by id
    try:
        task_id = int(message.text)
        user_id = message.from_user.id
        con = sqlite3.connect('user_todo_db')
        cur = con.cursor()
        cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        if cur.rowcount > 0:
            await message.answer(f"✅ Task {task_id} deleted", reply_markup=get_main_menu())
        else:
            await message.answer(f"❌ Task not find")
        con.commit()
        con.close()

    except ValueError:
        await message.answer(f"Please entet a valid task number", reply_markup=get_main_menu())

    await state.clear()

@dp.callback_query(lambda c: c.data =='completed')
async def is_completed_handler(callback: CallbackQuery, state: FSMContext): # handler function sets the FSM status
    await callback.message.edit_text(f"Please enter the task number", reply_markup=get_main_menu())
    await state.set_state(TaskStates.waiting_for_id)
    await callback.answer()