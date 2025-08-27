import sqlite3
import asyncio
import random
from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import pyautogui
import logging
import keyboard
from config import TOKEN
from textsforautoclickbot import welcome, help_text

API_TOKEN = TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Clicking(StatesGroup):
     number_click = State()
     intervalclicks = State()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('clicker_bot.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger(__name__)

def init_db():
    try:
        with sqlite3.connect('Clicker.db') as db:
          cursor = db.cursor()
          cursor.execute('''CREATE TABLE IF NOT EXISTS Clicker
                         ( username TEXT, id INTEGER UNIQUE,  Number_of_clicks INTEGER, 
                         Interval INTEGER, Mouse_Button TEXT)''')
          db.commit()
          logging.info('Data_Base create!')
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')

def insert_db(username: str, id: int, Number_of_clicks: int, Interval: int, Mouse_Button: str):
    try:
          with sqlite3.connect('Clicker.db') as db:
               cursor = db.cursor()
               cursor.execute('''INSERT OR IGNORE INTO Clicker
                              ( username, id, Number_of_clicks, Interval, Mouse_Button) VALUES
                              ( ?, ?, ?, ?, ? )''', (username, id, Number_of_clicks, Interval, Mouse_Button))
               db.commit()
               logging.info("the user's data is filled in")
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')

def select_db(user_id: int):
    try:
          with sqlite3.connect('Clicker.db') as db:
               cursor = db.cursor()
               cursor.execute('''SELECT * FROM Clicker WHERE id = ?''', (user_id,))
               data = cursor.fetchone()
               return data
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')
    return None

Mouse_keyboard = InlineKeyboardMarkup(inline_keyboard=[
     [
          InlineKeyboardButton(text='Left mouse', callback_data='left_mouse'),
          InlineKeyboardButton(text='Right mouse', callback_data='Right_mouse')
     ]
])

settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
     [
          InlineKeyboardButton(text='Number of clicks', callback_data='Number_clicks'),
          InlineKeyboardButton(text='Click Interval', callback_data='Click_Interval')
     ],
     [
          InlineKeyboardButton(text='Mouse button', callback_data='Mouse_button'),
          InlineKeyboardButton(text='< Back', callback_data='back2')
     ]    
])

back_main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text= '< Back', callback_data='back')
    ]
])

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Start Clicks', callback_data='start_clicks'),
    ],
    [
        InlineKeyboardButton(text='Settings', callback_data='settings'),
        InlineKeyboardButton(text='Help', callback_data='help')
    ]
])

@dp.message(Command(commands=['start']))
async def start_command(message: types.Message):
    usernames = message.from_user.username
    ids = message.from_user.id
    Number_of_clickss = 10
    Intervals = 1
    Mouse_Buttons = 'left'
    insert_db(username=usernames, id=ids, Number_of_clicks=Number_of_clickss, Interval=Intervals, Mouse_Button=Mouse_Buttons)
    logging.info(f'the username: @{message.from_user.username} ID: {message.from_user.id} clicked /start')
    await message.answer(text=welcome, parse_mode='html', reply_markup=main_keyboard)

@dp.message(Command(commands=['help']))
async def help_command(message: types.Message):
    logging.info(f'the username: @{message.from_user.username} ID: {message.from_user.id} clicked /help')
    await message.answer(text=help_text, parse_mode='html')

@dp.callback_query(F.data == 'help')
async def help(callback: types.CallbackQuery):
    logging.info(f'the username: @{callback.from_user.username} ID: {callback.from_user.id} clicked button: help')
    await callback.message.edit_text(text=help_text, parse_mode='html', reply_markup=back_main)
    await callback.answer()

@dp.callback_query(F.data == 'back')
async def help(callback: types.CallbackQuery):
        logging.info(f'the username: @{callback.from_user.username} ID: {callback.from_user.id} clicked button: Back')
        await callback.message.edit_text(text=welcome, parse_mode='html', reply_markup=main_keyboard)
        await callback.answer()

@dp.callback_query(F.data == 'settings')
async def help(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        current_number = select_db(user_id)

        settings_text = f'''
<b>⚙️ AutoClicker Settings

Current settings:
• <i>Number of clicks: <code>{current_number[2]}</code></i>
• <i>Interval: <code>{current_number[3]}</code> sec</i>
• <i>Mouse button: <code>{current_number[4]}</code></i>
• <i>Coordinates: Not set</i>

Select a setting to change:</b>'''

        logging.info(f'the username: @{callback.from_user.username} ID: {callback.from_user.id} clicked button: Back')
        await callback.message.edit_text(text=settings_text, parse_mode='html', reply_markup=settings_keyboard)
        await callback.answer()

@dp.callback_query(F.data == 'Mouse_button')
async def mouse_button(callback: types.CallbackQuery):
     await callback.message.edit_text(text='<b>Choose one of the options:</b>', parse_mode='html', reply_markup=Mouse_keyboard)

@dp.callback_query(F.data == 'left_mouse')
async def left_mouse(callback: types.CallbackQuery):
    try:
        with sqlite3.connect('Clicker.db') as db:
            cursor = db.cursor()
            mouse = 'left'
            id = callback.from_user.id
            cursor.execute('''UPDATE Clicker SET Mouse_Button = ? WHERE id = ?''', (mouse, id))
            db.commit()
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')
    
    await callback.message.edit_text(text=welcome, parse_mode='html', reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(F.data == 'Right_mouse')
async def Right_mouse(callback: types.CallbackQuery):
    try:
        with sqlite3.connect('Clicker.db') as db:
            cursor = db.cursor()
            mousee = 'right'
            id = callback.from_user.id
            cursor.execute('''UPDATE Clicker SET Mouse_Button = ? WHERE id = ?''', (mousee, id))
            db.commit()
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')
    
    await callback.message.edit_text(text=welcome, parse_mode='html', reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(F.data == 'Number_clicks')
async def number_clicks(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(text='<b>Enter the number of clicks:</b>', parse_mode='html')
    await state.set_state(Clicking.number_click)
    await callback.answer()

@dp.message(Clicking.number_click)
async def numberclick(message: types.Message, state: FSMContext):
    try:
        number = float(message.text)
        if number <= 0:
            await message.answer(text='<b>Please enter a positive number!</b>', parse_mode='html')
            return
    except ValueError:
        await message.answer(text='<b>Please enter a valid number!</b>', parse_mode='html')
        return
    
    await state.update_data(number_clicks = message.text)
    stating = await state.get_data()
    
    try:
        with sqlite3.connect('Clicker.db') as db:
            cursor = db.cursor()
            id = message.from_user.id
            cursor.execute('''UPDATE clicker SET Number_of_clicks = ? WHERE id = ?''', (stating["number_clicks"], id))
            await message.answer(text='<b>successfully!</b>', parse_mode='html')
            db.commit()
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')
    
    await message.answer(text=welcome, parse_mode='html', reply_markup=main_keyboard)

    await state.clear()

@dp.callback_query(F.data == 'Click_Interval')
async def click_interval(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Clicking.intervalclicks)
    await callback.message.answer(text='<b>Enter the interval:</b>', parse_mode='html')
    await callback.answer()

@dp.message(Clicking.intervalclicks)
async def intervalclicks(message: types.Message, state: FSMContext):
    try:
        interval = float(message.text)
        if interval <= 0:
            await message.answer(text='<b>Please enter a positive number!</b>', parse_mode='html')
            return
    except ValueError:
        await message.answer(text='<b>Please enter a valid number!</b>', parse_mode='html')
        return

    await state.update_data(intervalclicks=interval)
    inter = await state.get_data()   

    try:
        with sqlite3.connect('Clicker.db') as db:
            cursor = db.cursor()
            id = message.from_user.id
            cursor.execute('''UPDATE Clicker SET Interval = ? WHERE id = ?''', (inter["intervalclicks"], id))
            await message.answer(text='<b>successfully!</b>', parse_mode='html')
            db.commit()
    except sqlite3.Error as e:
         logging.info(f'Error SQLite3: {e}')
    except Exception as e:
         logging.info(f'Error: {e}')
    
    await message.answer(text=welcome, parse_mode='html', reply_markup=main_keyboard)

    await state.clear()

@dp.callback_query(F.data == 'back2')
async def help(callback: types.CallbackQuery):
    await callback.message.edit_text(text=welcome, parse_mode='html', reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(F.data == 'start_clicks')
async def start_clicks(callback: types.CallbackQuery):
    data = select_db(callback.from_user.id)

    logging.info(f'the username: @{callback.from_user.username} ID: {callback.from_user.id} clicked button: Start Clicks')
    msg = await callback.message.answer(
        text='<b>The autoclicker will start after:</b> <code>5</code>',
        parse_mode='html'
    )
    for i in range(4, 0, -1):
         await asyncio.sleep(1)
         await msg.edit_text(
                text=f'<b>The autoclicker will start after:</b> <code>{i}</code>',
                parse_mode='html'
             )
    await asyncio.sleep(1)
    sts = await msg.edit_text(
        text='<b>The autoclicker is running!</b>',
        parse_mode='html'
    )
    for i in range(data[2], 0, -1):
        pyautogui.click(button=data[4])
        await asyncio.sleep(data[3])
    
    button = InlineKeyboardMarkup(inline_keyboard=[
         [
              InlineKeyboardButton(text='< Back', callback_data='back3')
         ]
    ])

    await sts.edit_text(text='<b>The autoclicker is stopped</b>', parse_mode='html', reply_markup=button)
    await callback.answer()
    
@dp.callback_query(F.data == 'back3')
async def back3(callback: types.CallbackQuery):
    await callback.message.answer(text=welcome, parse_mode='html', reply_markup=main_keyboard)
    await callback.answer()

async def main():
    init_db()
    logging.info('Starting bot!')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())