from bale import InlineKeyboardButton, InlineKeyboardMarkup, MenuKeyboardButton, MenuKeyboardMarkup


def build_inline(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    for row_num, row in enumerate(rows, start=1):
        for text, callback_data in row:
            markup.add(InlineKeyboardButton(text=text, callback_data=callback_data), row=row_num)
    return markup


def build_menu(rows: list[list[MenuKeyboardButton]]) -> MenuKeyboardMarkup:
    markup = MenuKeyboardMarkup()
    for row_num, row in enumerate(rows, start=1):
        for button in row:
            markup.add(button, row=row_num)
    return markup


def menu_button(text: str, *, request_contact: bool = False) -> MenuKeyboardButton:
    return MenuKeyboardButton(text, request_contact=request_contact)
