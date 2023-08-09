from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
main_markup.add(KeyboardButton(text="👤 Ro'yxatdan o'tish"))

status_data = ["O'quvchi", "Talaba", "Ishchi"]

status_markup = InlineKeyboardMarkup(row_width=1)
for item in status_data:
    status_markup.insert(InlineKeyboardButton(text=item, callback_data=item))

confirm_markup = ReplyKeyboardMarkup(resize_keyboard=True)
confirm_markup.add(KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q"))
