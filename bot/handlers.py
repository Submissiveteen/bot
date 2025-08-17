from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states import CryptoBotStates
from .keyboards import *

router = Router()


@router.message(F.text == "/start")
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "👋 Добро пожаловать в CryptoBot!\n\n⭐⭐⭐⭐⭐\n[⭐️ Получить нулевую комиссию]\n\n[RU] [EN] [DE]",
        reply_markup=start_kb,
    )
    await state.set_state(CryptoBotStates.start)


@router.message(CryptoBotStates.start)
async def loyalty_intro_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Чтобы получить нулевую комиссию, выполните 10 успешных транзакций с помощью бота или общий объём покупок — от 100,000$.\nВаш прогресс: 0/10 | $0/$100,000",
        reply_markup=loyalty_intro_kb,
    )
    await state.set_state(CryptoBotStates.loyalty_intro)


@router.message(CryptoBotStates.loyalty_intro)
async def loyalty_details_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Вы получаете баллы за каждую успешную сделку. Нулевая комиссия — эксклюзив для лояльных пользователей. Всё прозрачно, прогресс виден после каждой сделки.",
        reply_markup=loyalty_details_kb,
    )
    await state.set_state(CryptoBotStates.loyalty_details)


@router.message(CryptoBotStates.loyalty_details)
async def nationality_handler(msg: Message, state: FSMContext):
    await msg.answer("🌐 Укажите свою национальность:", reply_markup=nationality_kb)
    await state.set_state(CryptoBotStates.nationality)


@router.message(CryptoBotStates.nationality)
async def residence_handler(msg: Message, state: FSMContext):
    await msg.answer("🌍 В какой стране вы сейчас находитесь?", reply_markup=None)
    await state.set_state(CryptoBotStates.residence)


@router.message(CryptoBotStates.residence)
async def fiat_currency_handler(msg: Message, state: FSMContext):
    await msg.answer("💶 В какой валюте у вас средства?", reply_markup=fiat_currency_kb)
    await state.set_state(CryptoBotStates.fiat_currency)


@router.message(CryptoBotStates.fiat_currency)
async def amount_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "💸 На какую сумму хотите купить криптовалюту?", reply_markup=amount_kb
    )
    await state.set_state(CryptoBotStates.amount)


@router.message(CryptoBotStates.amount)
async def crypto_handler(msg: Message, state: FSMContext):
    await msg.answer("💱 Какую криптовалюту хотите купить?", reply_markup=crypto_kb)
    await state.set_state(CryptoBotStates.crypto)


@router.message(CryptoBotStates.crypto)
async def payment_method_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "🏦 Выберите способ оплаты:\nSEPA — рекомендовано сервисом (минимальная комиссия)\nКарта — удобно для небольших сумм, но возможны отказы.",
        reply_markup=payment_method_kb,
    )
    await state.set_state(CryptoBotStates.payment_method)


@router.message(CryptoBotStates.payment_method)
async def wallet_or_broker_handler(msg: Message, state: FSMContext):
    await msg.answer("Что вы хотите пополнить?", reply_markup=wallet_or_broker_kb)
    await state.set_state(CryptoBotStates.wallet_or_broker)


@router.message(CryptoBotStates.wallet_or_broker)
async def broker_code_handler(msg: Message, state: FSMContext):
    if msg.text == "Инвестиционный счёт":
        await msg.answer("Пожалуйста, введите код вашего брокера:")
        await state.set_state(CryptoBotStates.broker_code)
    else:
        await msg.answer(
            "🛡️ Для самой быстрой и безопасной сделки укажите адрес вашего кошелька, куда хотите получить криптовалюту.",
            reply_markup=user_wallet_kb,
        )
        await state.set_state(CryptoBotStates.user_wallet)


@router.message(CryptoBotStates.broker_code)
async def user_wallet_direct_handler(msg: Message, state: FSMContext):
    # TODO: валидация кода брокера по whitelist
    await msg.answer(
        "✅ Код подтверждён. Укажите адрес кошелька для пополнения:",
        reply_markup=user_wallet_direct_kb,
    )
    await state.set_state(CryptoBotStates.user_wallet_direct)


@router.message(CryptoBotStates.user_wallet_direct)
async def kyc_check_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "⚠️ Для суммы и выбранного способа оплаты платформа может запросить подтверждение личности (KYC).",
        reply_markup=kyc_check_kb,
    )
    await state.set_state(CryptoBotStates.kyc_check)


@router.message(CryptoBotStates.user_wallet)
async def gen_address_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "⏳ Генерируем индивидуальный защищённый адрес для вашей операции...",
        reply_markup=gen_address_kb,
    )
    await state.set_state(CryptoBotStates.gen_address)


@router.message(CryptoBotStates.gen_address)
async def payment_instructions_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "❗️Перед оплатой:\n1️⃣ Скопируйте персональный адрес выше...\n4️⃣ После оплаты вернитесь в чат и подтвердите перевод.",
        reply_markup=payment_instructions_kb,
    )
    await state.set_state(CryptoBotStates.payment_instructions)


@router.message(CryptoBotStates.payment_instructions)
async def kyc_check2_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "⚠️ Для суммы и выбранного способа оплаты платформа может запросить подтверждение личности (KYC).",
        reply_markup=kyc_check_kb,
    )
    await state.set_state(CryptoBotStates.kyc_check)


@router.message(CryptoBotStates.kyc_check)
async def manual_high_fee_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "⚠️ Без прохождения проверки личности возможна только индивидуальная обработка с повышенной комиссией — 15%.",
        reply_markup=manual_high_fee_kb,
    )
    await state.set_state(CryptoBotStates.manual_high_fee)


@router.message(CryptoBotStates.manual_high_fee)
async def confirmation_handler(msg: Message, state: FSMContext):
    await msg.answer("✅ Покупка прошла успешно?", reply_markup=confirmation_kb)
    await state.set_state(CryptoBotStates.confirmation)


@router.message(CryptoBotStates.confirmation)
async def loyalty_status_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "🌟 Ваш прогресс к нулевой комиссии:", reply_markup=loyalty_status_kb
    )
    await state.set_state(CryptoBotStates.loyalty_status)


@router.message(CryptoBotStates.loyalty_status)
async def history_handler(msg: Message, state: FSMContext):
    await msg.answer("📝 История ваших операций:", reply_markup=history_kb)
    await state.set_state(CryptoBotStates.history)


@router.message(CryptoBotStates.history)
async def operator_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "💬 Наш оператор на связи 24/7! Опишите ваш вопрос.", reply_markup=operator_kb
    )
    await state.set_state(CryptoBotStates.operator)


@router.message(CryptoBotStates.operator)
async def back_to_menu_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "👋 Добро пожаловать в CryptoBot!\n\n⭐⭐⭐⭐⭐\n[⭐️ Получить нулевую комиссию]\n\n[RU] [EN] [DE]",
        reply_markup=start_kb,
    )
    await state.set_state(CryptoBotStates.start)


def get_start_message() -> str:
    """Return the localized start prompt."""
    import json
    from pathlib import Path

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["start"]


def get_service_status_message() -> str:
    """Return human readable status of dummy service."""
    import json
    from pathlib import Path
    from core.utils import dummy_service_status

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    status = dummy_service_status()
    if status == "ok":
        return data["service_ok"]
    if status == "timeout":
        return data["service_timeout"]
    return data["service_fail"]


def get_farewell_message() -> str:
    """Return farewell template."""
    import json
    from pathlib import Path

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["farewell"]


def get_secure_service_message(url: str) -> str:
    """Return message based on URL security."""
    import json
    from pathlib import Path
    from core.utils import secure_service_ok

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["service_ok"] if secure_service_ok(url) else data["service_insecure"]


def get_stage6_title() -> str:
    """Return title for roadmap stage 6."""
    import json
    from pathlib import Path

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["stage6_title"]


def get_codegen_intro_message() -> str:
    """Return intro message for code generation phase."""
    import json
    from pathlib import Path

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["codegen_intro"]


def get_evidence_message() -> str:
    """Return message for evidence matrix stage."""
    import json
    from pathlib import Path

    data = json.loads(Path("templates/messages_ru.json").read_text(encoding="utf-8"))
    return data["evidence_intro"]
