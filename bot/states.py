
from aiogram.dispatcher.filters.state import State, StatesGroup


class BookState(StatesGroup):
    for_book_type = State()

class BookList(StatesGroup):
    for_book_list = State()
class BookAuthState(StatesGroup):
    for_book_auth = State()

