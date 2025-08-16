from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⭐️ Получить нулевую комиссию")],
        [
            KeyboardButton(text="RU"),
            KeyboardButton(text="EN"),
            KeyboardButton(text="DE"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

loyalty_intro_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Копить баллы"), KeyboardButton(text="Подробнее")],
        [KeyboardButton(text="Вернуться")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

loyalty_details_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

nationality_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="РФ"),
            KeyboardButton(text="Украина"),
            KeyboardButton(text="ЕС"),
            KeyboardButton(text="Казахстан"),
            KeyboardButton(text="Другое"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

fiat_currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="EUR"),
            KeyboardButton(text="USD"),
            KeyboardButton(text="UAH"),
            KeyboardButton(text="PLN"),
            KeyboardButton(text="RUB"),
            KeyboardButton(text="Другое"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

amount_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Далее")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

crypto_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="BTC"),
            KeyboardButton(text="ETH"),
            KeyboardButton(text="USDT"),
            KeyboardButton(text="USDC"),
            KeyboardButton(text="SOL"),
            KeyboardButton(text="Другое"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

payment_method_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="SEPA-перевод (рекомендовано)"),
            KeyboardButton(text="Банковская карта"),
            KeyboardButton(text="Apple Pay / Google Pay"),
            KeyboardButton(text="Revolut/Monobank"),
            KeyboardButton(text="Другое"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

wallet_or_broker_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Крипто-кошелёк"),
            KeyboardButton(text="Инвестиционный счёт"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

user_wallet_direct_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Далее")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

user_wallet_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Далее")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

gen_address_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Инструкция к оплате")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

payment_instructions_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Перейти к оплате")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

kyc_check_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Продолжить"),
            KeyboardButton(text="Отказаться от прохождения KYC"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

manual_high_fee_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить напрямую с комиссией 15%")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

confirmation_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Получил(а) крипту")],
        [KeyboardButton(text="Платёж не прошёл"), KeyboardButton(text="Нужна помощь")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

loyalty_status_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="История операций"),
            KeyboardButton(text="Подробнее о лояльности"),
        ],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

history_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться")],
        [KeyboardButton(text="Связаться с оператором")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

operator_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Вернуться в меню")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)
