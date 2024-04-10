import asyncio
import aiofiles
import os

from dotenv import load_dotenv, find_dotenv
from transliterate import translit

from aiogram import Bot, Dispatcher, types
from aiogram import F

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.types import FSInputFile 

from test import parse_file, parse_text

load_dotenv(find_dotenv())

API_TOKEN = os.environ.get("BOT_TOKEN")
SPACE_SIZE = 4

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

res = {}

async def text_answer(text, callback_query):
    await callback_query.message.reply(await parse_text(text))

async def list_answer(list, callback_query):
    for l in list:
        if "txt" in l:
            await callback_query.message.reply(await parse_text(l))
        elif "jpg" in l or "png" in l:
            t_file = FSInputFile(f'files/{l}')
            await bot.send_photo(callback_query.message.chat.id, t_file)

async def buttons_answer(dict, callback_query):
    buttons = []
    for key in dict:
        buttons.append(
            [
                InlineKeyboardButton(text=key, callback_data=translit("btn" + key[:10], language_code='ru', reversed=True))
            ]
        )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.reply("Темы", reply_markup=inline_kb)

async def get_answer(dict_, search, callback_query):
    for r in dict_:
        if translit(r[:10], language_code='ru', reversed=True) == search:
            if type(dict_[r]) == dict:
                return await buttons_answer(dict_[r], callback_query)
            elif type(dict_[r]) == str:
                return await text_answer(dict_[r], callback_query)
            elif type(dict_[r]) == list:
                return await list_answer(dict_[r], callback_query)
        else:
            if type(dict_[r]) == dict:
                await get_answer(dict_[r], search, callback_query)
            

@dp.message(Command("test"))
async def process_command_1(message: types.Message):
    buttons = []
    for key in res:
        buttons.append( 
            [
                InlineKeyboardButton(text=key, callback_data=translit("btn" + key[:10], language_code='ru', reversed=True)) 
            ] 
        )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply("Темы", reply_markup=inline_kb)

@dp.callback_query(F.data.startswith('btn'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    search = callback_query.data.replace('btn', '')
    await get_answer(res, search, callback_query)


async def main():
    global res
    res = await parse_file()
    await dp.start_polling(bot)    

if __name__ == '__main__':
    asyncio.run(main())