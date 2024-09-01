import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from database import Database

# Bot tokeni
TOKEN = "7283967119:AAGQIxkyTlu22edfqtenisW_f7SProT_c5A"

# Dispatcher va botni sozlash
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Ma'lumotlar bazasi bilan bog'lanish
db = Database(
    database="online_shop",
    user="root",
    password="87654321",
    host="localhost",
    port=3306
)
db.connect()

# Bot holatlarini yaratish
class Registration(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_contact = State()

class ProductSelection(StatesGroup):
    waiting_for_product_choice = State()

# /start komandasi bilan boshlanish
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    print(message.from_user.id)
    await message.answer("Ismingizni kiriting:")
    await state.set_state(Registration.waiting_for_first_name)

@dp.message(Registration.waiting_for_first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Registration.waiting_for_last_name)

# @dp.message(Registration.waiting_for_last_name)
# async def process_last_name(message: types.Message, state: FSMContext):
#     await state.update_data(last_name=message.text)
#     await message.answer("Telefon raqamingizni kiriting:")
#     await state.set_state(Registration.waiting_for_contact)


@dp.message(Registration.waiting_for_last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    # Kontakt yuborish tugmasini yaratish
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[
                                       [
                                           KeyboardButton(text="Kontaktni yuboring", request_contact=True)
                                       ]
                                   ])

    await message.answer("Kontakt ma'lumotlaringizni yuboring:", reply_markup=keyboard)
    await state.set_state(Registration.waiting_for_contact)


@dp.message(Registration.waiting_for_contact, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    first_name = data['first_name']
    last_name = data['last_name']
    # phone = data['phone_number']
    phone_number = message.contact.phone_number

    # Foydalanuvchini bazaga qo'shish
    db.add_user(first_name, last_name, phone_number) #phone)

    # Registratsiya tugagandan so'ng, mahsulot tanlash
    await message.answer("Registratsiya muvaffaqiyatli o'tdi! Endi mahsulot tanlang:")
    await show_products(message)
    await state.set_state(ProductSelection.waiting_for_product_choice)

async def show_products(message: types.Message):
    products = [
        ("Rossiya Oq oyna", "10$"),
        ("Titan", "15$"),
        ("Royal Blue", "20$"),
        ("Layt Bronza", "25$")
    ]

    # Mahsulotlar ro'yxatini shakllantirish
    product_buttons = (types.KeyboardButton(text=f"{name} - {price}") for name, price in products)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=[[btn] for btn in product_buttons]
                                   )

    await message.answer("Mavjud mahsulotlar:", reply_markup=keyboard)

@dp.message(ProductSelection.waiting_for_product_choice)
async def process_product_choice(message: types.Message, state: FSMContext):
    selected_product = message.text
    user_data = await state.get_data()

    # Admin raqamiga xabar yuborish
    admin_chat_id = 5687088705  # Bu yerda adminning haqiqiy chat ID sini kiriting
    # contact = "+998951303213"

    await bot.send_message(admin_chat_id, f"Foydalanuvchi "
                                                   f"{user_data['first_name']}"
                                                   f"{user_data['last_name']} mahsulotni sotib oldi: {selected_product}")

    await message.answer(f"Siz {selected_product} ni tanladingiz. Tez orada siz bilan bog'lanamiz!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler('bot.log'),
                            logging.StreamHandler(sys.stdout)
                        ]
                        )

    asyncio.run(main())
