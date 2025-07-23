buyer_handlers_code = '''
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from core.aggregator_selector import AggregatorSelector
from core.deeplink_generator import DeeplinkGenerator
import pandas as pd

router = Router()

tbl1 = pd.read_csv("data/table_1.csv")
tbl2 = pd.read_csv("data/table_2.csv")
tbl3_500 = pd.read_csv("data/table_3_500.csv")
tbl3_2000 = pd.read_csv("data/table_3_2000.csv")
tbl3_10000 = pd.read_csv("data/table_3_10000.csv")
tbl4 = pd.read_csv("data/table_4.csv")

selector = AggregatorSelector(tbl2, tbl3_500, tbl3_2000, tbl3_10000, tbl1)
deeplink_gen = DeeplinkGenerator(tbl4)

class CryptoBuy(StatesGroup):
    country = State()
    method = State()
    amount = State()
    fiat = State()
    crypto = State()
    wallet = State()

@router.message(F.text == "/start")
async def start(msg: Message, state: FSMContext):
    await msg.answer("🌍 Введите вашу страну:")
    await state.set_state(CryptoBuy.country)

@router.message(CryptoBuy.country)
async def get_country(msg: Message, state: FSMContext):
    await state.update_data(country=msg.text)
    await msg.answer("💳 Выберите способ оплаты (card, sepa, bank):")
    await state.set_state(CryptoBuy.method)

@router.message(CryptoBuy.method)
async def get_method(msg: Message, state: FSMContext):
    await state.update_data(method=msg.text)
    await msg.answer("💰 Введите сумму в фиате:")
    await state.set_state(CryptoBuy.amount)

@router.message(CryptoBuy.amount)
async def get_amount(msg: Message, state: FSMContext):
    await state.update_data(amount=msg.text)
    await msg.answer("💱 Введите фиатную валюту (например, EUR):")
    await state.set_state(CryptoBuy.fiat)

@router.message(CryptoBuy.fiat)
async def get_fiat(msg: Message, state: FSMContext):
    await state.update_data(fiat=msg.text)
    await msg.answer("🪙 Выберите криптовалюту (например, BTC, ETH, USDT):")
    await state.set_state(CryptoBuy.crypto)

@router.message(CryptoBuy.crypto)
async def get_crypto(msg: Message, state: FSMContext):
    await state.update_data(crypto=msg.text)
    await msg.answer("📥 Введите адрес кошелька:")
    await state.set_state(CryptoBuy.wallet)

@router.message(CryptoBuy.wallet)
async def generate_link(msg: Message, state: FSMContext):
    await state.update_data(wallet=msg.text)
    data = await state.get_data()

    country = data["country"]
    method = data["method"]
    amount = float(data["amount"])
    fiat = data["fiat"]
    crypto = data["crypto"]
    wallet = data["wallet"]

    aggs = selector.select_top(country, method, amount, True)
    if not aggs:
        await msg.answer("⚠️ Нет доступных агрегаторов. Попробуйте другую сумму или способ.")
        return

    agg = aggs[0]
    row = tbl1[tbl1["Aggregator"].str.lower().str.contains(agg.lower())].iloc[0]
    base_url = str(row.get("DeeplinkExample", f"https://{agg}.com/"))

    params = {
        "fiat": fiat,
        "crypto": crypto,
        "fiatAmount": amount,
        "walletAddress": wallet,
        "country": country,
        "email": "test@email.com"
    }

    try:
        link = deeplink_gen.generate(agg, base_url, params)
    except Exception as e:
        await msg.answer(f"Ошибка генерации ссылки: {e}")
        return

    await msg.answer(f"✅ Агрегатор: <b>{agg}</b>\\n[Перейти к покупке]({link})", parse_mode="HTML")
    await state.clear()
'''

updated_buyer_handlers_path = "bot/buyer_handlers.py"

# Сохраняем buyer_handlers.py
with open(updated_buyer_handlers_path, 'w') as f:
    f.write(buyer_handlers_code)

# Проверим main.py — покажем весь код
main_py_path = os.path.join(bot_main_path, "main.py")
with open(main_py_path, 'r') as f:
    main_code = f.read()

main_code
