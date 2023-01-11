from typing import Optional
from aiogram.filters.callback_data import CallbackData


class InfoCallbackFactory(CallbackData, prefix='info'):
    action: str
    value: Optional[int | str]
    edit: Optional[str]


class SearchCallbackFactory(CallbackData, prefix='search'):
    pet_type: int
    page: int
    action: str
