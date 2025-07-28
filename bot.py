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
                task_name TEXT,
                is_completed BOOLEAN DEFAULT FALSE
                )
                ''')
    con.commit()
    con.close()

def get_main_menu(): # main menu with build-in button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅Add task", callback_data="add_task")],
        [InlineKeyboardButton(text="❌Delete task", callback_data="delete_task")],
        [InlineKeyboardButton(text="✅Completed", callback_data="completed")],
        [InlineKeyboardButton(text="📑List task", callback_data="list_task")],
    ])
    return keyboard

@dp.message(Command("start"))#
async def start_handler(message:Message): # start command handler
    user_name = message.from_user.first_name
    welcom_text = f"👋Hi {user_name}, a`m a simple task manager.\nManage your time."

    await message.answer(welcom_text, reply_markup=get_main_menu())

@dp.callback_query(lambda c: c.data == "add_task")
async def add_task_handler(callback: CallbackQuery, state: FSMContext): # add task command handler
    await callback.message.edit_text("📑Enter a name for the name task")
    await state.set_state(TaskStates.waiting_for_task)
    await callback.answer()


@dp.message(TaskStates.waiting_for_task)
async def save_task(message: Message, state: FSMContext): # Getting the task text and saving it to the database
    user_id = message.from_user.id
    task_name = message.text

    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute("INSERT INTO tasks ( user_id, task_name) VALUES (?, ?)",
                   (user_id, task_name))
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
            await message.answer(f"❌ Task not find", reply_markup=get_main_menu())

        con.commit()
        con.close()

    except ValueError:
        await message.answer(f"Please entet a valid task number", reply_markup=get_main_menu())

    await state.clear()

@dp.callback_query(lambda c: c.data =='completed')
async def is_completed_handler(callback: CallbackQuery): # handler function command user and creates buttons
    user_id = callback.from_user.id
    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute("SELECT id, task_name FROM tasks WHERE user_id=? AND is_completed=FALSE", (user_id,))
    tasks = cur.fetchall()
    con.close()
    if not tasks:
        await callback.message.edit_text(f"✅ No unfinished tasks ", reply_markup=get_main_menu())
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{task_id}. {task_name[:20]}...", callback_data=f"mark_done_{task_id}")]
            for task_id, task_name in tasks] + [[InlineKeyboardButton(text= "🔃go back", callback_data="go_back")]])


        await callback.message.edit_text(f"✅ Select the task number", reply_markup=keyboard)

    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("mark_done_"))
async def mark_done_task(callback: CallbackQuery): # Functions ubdate task
    task_id = int(callback.data.split('_')[2])
    user_id = callback.from_user.id
    con = sqlite3.connect('user_todo_db')
    cur = con.cursor()
    cur.execute("UPDATE tasks SET is_completed = TRUE WHERE id=? AND user_id=?", (task_id, user_id))
    con.commit()
    con.close()

    await callback.message.edit_text(f"✅ Task number:{task_id} - completed! ", reply_markup=get_main_menu())
    await callback.answer()


@dp.callback_query(lambda c: c.data == "go_back" )
async def go_back_main_menu(callback: CallbackQuery): # Return to home page function
    await callback.message.edit_text("👋 Choose an action", reply_markup=get_main_menu())
    await callback.answer()

async def main():
    init_db()
    print("Bot launched")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
