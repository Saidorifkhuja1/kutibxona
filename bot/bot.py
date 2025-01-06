from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from states import BookState, BookAuthState, BookList
import requests
from aiogram.dispatcher import FSMContext
import json
from config import BOT_TOKEN, NEWS_LIST_URL, BOOK_LIST_URL, BOOK_TYPE_LIST_URL, BOOK_AUTHOR_LIST_URL, \
    RECOMMENDED_BOOKS_URL, BOOK_NAME_SEARCH_URL, BOOK_TYPE_SEARCH_URL, BOOK_AUTHOR_SEARCH_URL

# Initialize bot and dispatcher
TOKEN = BOT_TOKEN
bot = Bot(token=TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


# Command to start the bot and show the main menu
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Yangiliklar"), KeyboardButton("Kitoblar"))
    await message.answer("Bizning Kutubxonamiz telegram botiga xush kelibsiz. "
                         "Afsuski, biz bu yerda sizga barcha ma'lumotlarni bera olmaymiz."
                         "Ko'proq ma'lumotga ega bo'lish uchun bizning kutubxonaga tashrif buyuring. "
                         "Manzil: Namangan shahri, Davlatobod tumani. "
                         "Mo'ljal: Tennis korti yonida.", reply_markup=keyboard)


# Handler for the "Kitoblar" button
@dp.message_handler(lambda message: message.text == "Kitoblar")
async def show_books_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("Kitoblar Ro’yxati"),
        KeyboardButton("Janrlar Ro’yxati"),
        KeyboardButton("Yozuvchilar Ro’yxati"),
        KeyboardButton("Tavfsiya etilgan kitoblar"),
        KeyboardButton("Asosiy Menyuga qaytish")
    )
    await message.answer("Quyidagilardan birini tanlang:", reply_markup=keyboard)


# Handler for the "Back to Books Menu" button
@dp.message_handler(lambda message: message.text == "Kitoblar Menyusiga qaytish", state="*")
async def back_to_books_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await show_books_menu(message)


@dp.message_handler(lambda message: message.text == "Kitoblar Ro’yxati")
async def list_books(message: Message, state: FSMContext):
    response = requests.get(BOOK_LIST_URL)

    try:
        books = response.json()
        if 'results' in books and isinstance(books['results'], list):
            limited_books = books['results'][:5]  # Limit to the first 5 books

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for book in limited_books:
                keyboard.add(KeyboardButton(f"Kitob: {book['title']}"))

            keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))
            await message.answer("Quyidagilardan birini tanlang:", reply_markup=keyboard)
            await BookList.for_book_list.set()
        else:
            await message.answer("Kitoblar topilmadi.")
    except Exception as e:
        await message.answer(f"Kitoblarni olishda xatolik: {e}")


@dp.message_handler(state=BookList.for_book_list)
async def show_book_details_by_name(message: types.Message, state: FSMContext):
    book_name = message.text[6:]
    response = requests.get(BOOK_NAME_SEARCH_URL, params={'search': book_name})

    try:
        books = response.json()
        if books['results']:
            book = books['results'][0]  # Assuming you want the first result
            cover_image = book['cover_image'] if book['cover_image'] else None
            title = book['title']
            description = book.get('truncated_description', 'Malumot mavjud emas')

            # Send the cover image if available
            if cover_image:
                await message.answer_photo(cover_image)

            # Send the title and description
            await message.answer(f"Title: {title}\n\n{description}")
        else:
            await message.answer("Kitob topilmadi")
    except Exception as e:
        await message.answer(f"Kitobni izlashda xatolik: {e}")


# Handler for the "Janrlar Ro’yxati" button
@dp.message_handler(lambda message: message.text == "Janrlar Ro’yxati")
async def list_book_types(message: types.Message):
    response = requests.get(BOOK_TYPE_LIST_URL)

    try:
        types = response.json()['results'][:5]

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for item in types:
            keyboard.add(KeyboardButton(f"Janr: {item['name']}"))

        keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))

        await message.answer("Quyidagilardan birini tanlang:", reply_markup=keyboard)
        await BookState.for_book_type.set()
    except Exception as e:
        await message.answer(f"Kitob janrlarini olishda xatolik: {e}")

# Handler for showing books by type


@dp.message_handler(lambda message: message.text.startswith("Janr: "), state=BookState.for_book_type)
async def show_books_by_type(message: types.Message, state: FSMContext):
    book_type_name = message.text[6:]  # Extract the type name from the message text
    response = requests.get(BOOK_TYPE_SEARCH_URL, params={'name': book_type_name})

    try:
        books = response.json()
        if 'results' in books and isinstance(books['results'], list) and books['results']:
            limited_books = books['results'][:5]  # Limit to the first 5 books (adjust as needed)
            for book in limited_books:
                cover_image = book.get('cover_image', '')
                title = book['title']
                description = book.get('truncated_description', 'Malumot mavjud emas')

                if cover_image:
                    await message.answer_photo(cover_image)

                await message.answer(f"Title: {title}\n\n{description}")

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))
            await message.answer("Quyidagilardan birini tanlang:", reply_markup=keyboard)
        else:
            await message.answer("Bu janrda kitoblar topilmadi.")
    except Exception as e:
        await message.answer(f"Janr uchun kitoblarni olishda xatolik '{book_type_name}': {e}")


@dp.message_handler(lambda message: message.text == "Yozuvchilar Ro’yxati")
async def list_authors(message: types.Message):
    response = requests.get(BOOK_AUTHOR_LIST_URL)

    try:
        authors_data = response.json()
        if 'results' in authors_data and isinstance(authors_data['results'], list):
            authors = authors_data['results'][:5]  # Limit to the first 5 authors
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for author in authors:
                keyboard.add(KeyboardButton(f"Yozuvchi: {author['name']}"))

            keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))
            await message.answer("Yozuvchini tanlang:", reply_markup=keyboard)
            await BookAuthState.for_book_auth.set()
        else:
            await message.answer("Yozuvchilar topilmadi.")
    except Exception as e:
        await message.answer(f"Yozuvchilarni olishda xatolik: {e}")


@dp.message_handler(state=BookAuthState.for_book_auth)
async def show_books_by_author(message: types.Message, state: FSMContext):
    book_auth_name = message.text

    # Check if the message contains a colon
    if ":" not in book_auth_name:
        await message.answer("Yozuvchi formatida xatolik. Iltimos, haqiqiy yozuvchini tanlang.")
        return

    # Extract the author's name
    book_auth_name = book_auth_name.split(":")[1].strip()
    response = requests.get(BOOK_AUTHOR_SEARCH_URL, params={'name': book_auth_name})

    try:
        books = response.json()
        if 'results' in books and isinstance(books['results'], list) and books['results']:
            limited_books = books['results'][:5]
            for book in limited_books:
                cover_image = book.get('cover_image', '')
                title = book['title']
                description = book.get('truncated_description', 'Malumot mavjud emas')
                if cover_image:
                    await message.answer_photo(cover_image)
                await message.answer(f"Title: {title}\n\n{description}")

            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))
            await message.answer("Kitoblar Menyusiga qaytish", reply_markup=keyboard)
        else:
            await message.answer("Bu yozuvchi uchun kitoblar topilmadi.")
    except Exception as e:
        await message.answer(f"Yozuvchi uchun kitoblarni olishda xatolik '{book_auth_name}': {e}")


@dp.message_handler(lambda message: message.text == "Tavfsiya etilgan kitoblar")
async def show_recommended_books(message: types.Message):
    response = requests.get(RECOMMENDED_BOOKS_URL)

    try:
        books = response.json()['results']

        for book in books:
            cover_image = book.get('cover_image', '')
            title = book['title']
            description = book.get('truncated_description', 'Malumot mavjud emas')

            await message.answer_photo(cover_image)
            await message.answer(f"Title: {title}\n\n{description}")

        # Add a "Back to Books Menu" button
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Kitoblar Menyusiga qaytish"))
        await message.answer("Tavfsiya etilgan kitoblar:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Tavfsiya etilgan kitoblarni olishda xatolik: {e}")


# Handler for the "Yangiliklar" button
@dp.message_handler(lambda message: message.text == "Yangiliklar")
async def show_news_titles(message: types.Message):
    try:
        response = requests.get(NEWS_LIST_URL)
        news = response.json()

        # Limiting to the first 5 news items
        limited_news = news['results'][:5]

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for item in limited_news:
            keyboard.add(KeyboardButton(item['title']))

        keyboard.add(KeyboardButton("Asosiy Menyuga qaytish"))
        await message.answer("Yangilik maqolasini tanlang:", reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"Yangiliklarni olishda xatolik: {e}")


# Handler for showing news details
@dp.message_handler(lambda message: message.text not in ["Yangiliklar", "Asosiy Menyuga qaytish", "Kitoblar", "Kitoblar Menyusiga qaytish", "Janr: "])
async def show_news_details(message: types.Message):
    selected_news_title = message.text
    response = requests.get(NEWS_LIST_URL)

    try:
        news = response.json()
        selected_news = next((item for item in news['results'] if item['title'] == selected_news_title), None)

        if selected_news:
            await message.answer_photo(selected_news['image'])
            await message.answer(f"Title: {selected_news['title']}\n\n{selected_news['body']}")

            # Add a "Back to Main Menu" button
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        else:
            await message.answer("Yangilik topilmadi")
    except Exception as e:
        await message.answer(f"Yangilik tafsilotlarini olishda xatolik: {e}")


# Handler for "Asosiy Menyuga qaytish" button
@dp.message_handler(lambda message: message.text == "Asosiy Menyuga qaytish")
async def back_to_main_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Yangiliklar"), KeyboardButton("Kitoblar"))
    await message.answer("Asosiy Menyu", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


