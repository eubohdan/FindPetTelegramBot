from typing import Optional
from aiogram.filters.callback_data import CallbackData


class InfoCallbackFactory(CallbackData, prefix='info'):
    action: str
    value: Optional[int | str]
    edit: Optional[str]
