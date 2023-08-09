import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from database import insert_user_data, insert_adv_data
from keyboards import main_markup, status_markup, confirm_markup
from state import SignUpState


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

@dp.message_handler(commands=["start"], state="*")
async def do_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = message.from_user
    tg_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    user_name = user.username
    await message.answer(text=f"Assalomu alaykum, {first_name} {last_name}!", reply_markup=main_markup)
    try:
        insert_user_data(tg_id=tg_id, full_name=user.full_name, username=user_name)
    except Exception as error:
        print(error)

@dp.message_handler(text="👤 Ro'yxatdan o'tish")
async def sign_up(message: types.Message):
    await message.answer("Ro'yhatdan o'tish uchun oldin to'liq ism familiyangizni yuboring!", reply_markup=types.ReplyKeyboardRemove())

    await SignUpState.full_name.set()

@dp.message_handler(state=SignUpState.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    await state.update_data(data={"full_name": full_name})
    await message.answer("Endi yoshingizni yuboring")

    await SignUpState.next()

@dp.message_handler(state=SignUpState.age)
async def get_age(message: types.Message, state: FSMContext):
    age = message.text
    if age.isdigit():
        await state.update_data({"age": age})
        await message.answer("Ijtimoiy holatingizni belgilang", reply_markup=status_markup)
        await SignUpState.next()
    else:
        await message.answer("Yoshingizni faqat raqamlarda yuboring")

@dp.callback_query_handler(state=SignUpState.status)
async def get_status(call: types.CallbackQuery, state: FSMContext):
    status = call.data
    await call.answer(f"{status} holati saqlandi", show_alert=True)
    await call.message.delete()
    await state.update_data({"status": status})
    await call.message.answer("Telefon raqamingizni tasdiqlang", reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="📞 Telefon raqam", request_contact=True)]], resize_keyboard=True))
    await SignUpState.next()


@dp.message_handler(state=SignUpState.phone, content_types=["contact"])
async def get_phone_number(message: types.Message, state: FSMContext):
    contact = message.contact.phone_number
    await state.update_data({"phone": contact})
    data = await state.get_data()
    full_name = data.get("full_name")
    age = data.get("age")
    status = data.get("status")
    text = f"FIO: {full_name}\nYOSH: {age} yosh\nHOLAT: {status}\nTELEFON: {contact}"
    await message.answer(text=text)
    await message.answer("Barcha ma'lumotlaringizni tog'riligini tasdiqlaysizmi", reply_markup=confirm_markup)
    await SignUpState.next()

@dp.message_handler(state=SignUpState.confirm, text="❌ Yo'q")
async def cancel_sign_up(message: types.Message, state: FSMContext):
    await message.answer("Barcha ma'lumotlaringiz o'chirildi yana qayta ro'yhatdan o'tishingiz mumkin", reply_markup=main_markup)
    await state.finish()

@dp.message_handler(state=SignUpState.confirm, text="✅ Ha")
async def save_data(message: types.Message, state: FSMContext):
    data = await state.get_data()
    full_name = data.get("full_name")
    age = data.get("age")
    status = data.get("status")
    phone = data.get("phone")
    insert_adv_data(full_name=full_name, age=age, status=status, phone=phone)
    await message.answer("✅ Sizning barcha ma'lumotlaringiz saqlandi", reply_markup=main_markup)
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True)
