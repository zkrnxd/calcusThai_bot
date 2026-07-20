# handlers/main.py

import os
import logging
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile

from config import EXPORT_DIR, TEMP_DIR
from data.rents import RENTS
from data.costs import MAINTENANCE_RATES
from utils import *
from utils.pdf_exporter import export_to_pdf

router = Router()
logger = logging.getLogger(__name__)


# ============================================
# FSM СОСТОЯНИЯ
# ============================================

class InvestForm(StatesGroup):
    region = State()
    district = State()
    property_type = State()
    rent_type = State()
    price = State()
    downpayment = State()
    installment_rate = State()
    installment_term = State()
    uk_commission = State()
    management_class = State()
    ownership_type = State()
    result = State()


# ============================================
# ХЕНДЛЕР: /start
# ============================================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    text = (
        "🏝️ **Инвестиционный калькулятор недвижимости Таиланда**\n\n"
        "Рассчитайте реальную доходность с учётом всех расходов:\n"
        "• Аренда (High/Low сезон)\n"
        "• Рост рынка и этапов строительства\n"
        "• Рассрочка 0-7% на 1-15 лет\n"
        "• Все налоги, УК, Maintenance\n\n"
        "Нажмите **«Новый расчет»**, чтобы начать."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 Новый расчет", callback_data="new_calc")]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


# ============================================
# ОТМЕНА
# ============================================

@router.callback_query(F.data == "cancel")
async def cancel_calc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    text = "❌ Расчет отменен.\n\nНажмите **«Новый расчет»**, чтобы начать заново."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🧮 Новый расчет", callback_data="new_calc")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


# ============================================
# ВЫБОР РЕГИОНА
# ============================================

@router.callback_query(F.data == "new_calc")
async def select_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(InvestForm.region)
    await state.update_data(page=0)
    await show_regions(callback.message, state)


async def show_regions(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    page = data.get("page", 0)
    
    keyboard = get_regions_keyboard(page)
    regions = list(RENTS.keys())
    total_pages = (len(regions) + 1) // 2
    
    text = f"📍 **Выберите регион:**\n\n(страница {page+1}/{max(1, total_pages)})"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_region")
async def back_to_region(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.region)
    await state.update_data(page=0)
    await show_regions(callback.message, state)


@router.callback_query(F.data.startswith("region_page_"))
async def region_pagination(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)
    
    if "prev" in callback.data:
        page = max(0, page - 1)
    elif "next" in callback.data:
        page = max(0, page + 1)
    
    await state.update_data(page=page)
    await show_regions(callback.message, state)


@router.callback_query(F.data.startswith("region_"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    region = callback.data.replace("region_", "")
    await state.update_data(region=region, page=0)
    await state.set_state(InvestForm.district)
    await show_districts(callback.message, state)


# ============================================
# ВЫБОР РАЙОНА
# ============================================

async def show_districts(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    region = data.get("region", "Пхукет")
    page = data.get("page", 0)
    
    keyboard = get_districts_keyboard(region, page)
    districts = list(RENTS[region].keys())
    total_pages = (len(districts) + 2) // 3
    
    text = f"🏘️ **Выберите район:**\n\n📍 {region}\n\n(страница {page+1}/{max(1, total_pages)})"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_district")
async def back_to_district(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.district)
    await state.update_data(page=0)
    await show_districts(callback.message, state)


@router.callback_query(F.data.startswith("district_page_"))
async def district_pagination(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)
    
    if "prev" in callback.data:
        page = max(0, page - 1)
    elif "next" in callback.data:
        page = max(0, page + 1)
    
    await state.update_data(page=page)
    await show_districts(callback.message, state)


@router.callback_query(F.data.startswith("district_"))
async def select_property_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    district = callback.data.replace("district_", "")
    await state.update_data(district=district, page=0)
    await state.set_state(InvestForm.property_type)
    await show_property_types(callback.message, state)


# ============================================
# ВЫБОР ТИПА ОБЪЕКТА
# ============================================

async def show_property_types(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    region = data.get("region")
    district = data.get("district")
    page = data.get("page", 0)
    
    keyboard = get_property_types_keyboard(region, district, page)
    types = list(RENTS[region][district].keys())
    total_pages = (len(types) + 2) // 3
    
    text = f"🏠 **Выберите тип объекта:**\n\n📍 {region} / {district}\n\n(страница {page+1}/{max(1, total_pages)})"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_ptype")
async def back_to_property_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.property_type)
    await state.update_data(page=0)
    await show_property_types(callback.message, state)


@router.callback_query(F.data.startswith("ptype_page_"))
async def ptype_pagination(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)
    
    if "prev" in callback.data:
        page = max(0, page - 1)
    elif "next" in callback.data:
        page = max(0, page + 1)
    
    await state.update_data(page=page)
    await show_property_types(callback.message, state)


@router.callback_query(F.data.startswith("ptype_"))
async def select_rent_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    prop_type = callback.data.replace("ptype_", "")
    await state.update_data(property_type=prop_type)
    await state.set_state(InvestForm.rent_type)
    
    data = await state.get_data()
    region = data.get("region")
    district = data.get("district")
    rent_data = RENTS[region][district][prop_type]
    
    text = (
        f"✅ **Выбрано:** {prop_type}\n\n"
        f"📍 {region} / {district}\n"
        f"📏 Площадь: {rent_data.get('sqm', '—')} м²\n"
        f"🏖️ High Season: {rent_data['high']:,} ฿/мес\n"
        f"🌴 Low Season: {rent_data['low']:,} ฿/мес\n"
        f"📊 Заполняемость: {rent_data['occupancy']}%\n\n"
        "Выберите тип аренды:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🏖️ Посуточная", callback_data="rent_short")],
        [InlineKeyboardButton("📅 Долгосрочная (от 6 мес)", callback_data="rent_long")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_ptype")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


# ============================================
# ТИП АРЕНДЫ → ЦЕНА
# ============================================

@router.callback_query(F.data.startswith("rent_"))
async def ask_price(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rent_type = "short" if callback.data == "rent_short" else "long"
    await state.update_data(rent_type=rent_type)
    await state.set_state(InvestForm.price)
    
    text = (
        "💰 **Введите стоимость объекта** (в тайских батах)\n\n"
        "Например: 5000000"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data="back_rent_type")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_rent_type")
async def back_to_rent_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.rent_type)
    
    data = await state.get_data()
    region = data.get("region")
    district = data.get("district")
    prop_type = data.get("property_type")
    rent_data = RENTS[region][district][prop_type]
    
    text = (
        f"✅ **Выбрано:** {prop_type}\n\n"
        f"📍 {region} / {district}\n"
        f"📏 Площадь: {rent_data.get('sqm', '—')} м²\n"
        f"🏖️ High Season: {rent_data['high']:,} ฿/мес\n"
        f"🌴 Low Season: {rent_data['low']:,} ฿/мес\n"
        f"📊 Заполняемость: {rent_data['occupancy']}%\n\n"
        "Выберите тип аренды:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🏖️ Посуточная", callback_data="rent_short")],
        [InlineKeyboardButton("📅 Долгосрочная (от 6 мес)", callback_data="rent_long")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_ptype")],
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(InvestForm.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text.replace(",", "").replace(" ", ""))
        if price <= 0:
            raise ValueError
        await state.update_data(price=price)
        await state.set_state(InvestForm.downpayment)
        await state.update_data(page=0)
        await show_downpayment(message, state)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (только цифры)")


# ============================================
# ПЕРВЫЙ ВЗНОС
# ============================================

async def show_downpayment(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    page = data.get("page", 0)
    price = data.get("price", 0)
    
    keyboard = get_downpayment_keyboard(page)
    options = list(range(20, 105, 5))
    total_pages = (len(options) + 4) // 5
    
    text = f"💵 **Выберите первый взнос (ПВ)**\n\n💰 Цена: {price:,} ฿\n\n(страница {page+1}/{total_pages})"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_price")
async def back_to_price(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.price)
    
    text = "💰 **Введите стоимость объекта** (в тайских батах)\n\nНапример: 5000000"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data="back_rent_type")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("dp_page_"))
async def dp_pagination(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)
    
    if "prev" in callback.data:
        page = max(0, page - 1)
    elif "next" in callback.data:
        page = max(0, page + 1)
    
    await state.update_data(page=page)
    await show_downpayment(callback.message, state)


@router.callback_query(F.data.startswith("dp_"))
async def process_downpayment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    dp_percent = int(callback.data.replace("dp_", ""))
    await state.update_data(downpayment=dp_percent)
    
    data = await state.get_data()
    price = data.get("price", 0)
    dp_amount = price * dp_percent // 100
    await state.update_data(dp_amount=dp_amount)
    
    await state.set_state(InvestForm.installment_rate)
    await show_installment(callback.message, state)


# ============================================
# РАССРОЧКА: СТАВКА
# ============================================

async def show_installment(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    price = data.get("price", 0)
    dp_amount = data.get("dp_amount", 0)
    
    keyboard = get_installment_rate_keyboard()
    text = (
        f"📊 **Выберите ставку по рассрочке**\n\n"
        f"💰 Цена: {price:,} ฿\n"
        f"💵 ПВ ({data.get('downpayment', 30)}%): {dp_amount:,} ฿\n"
        f"🏦 Остаток: {price - dp_amount:,} ฿\n\n"
        "Выберите ставку:"
    )
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_dp")
async def back_to_downpayment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.downpayment)
    await state.update_data(page=0)
    await show_downpayment(callback.message, state)


@router.callback_query(F.data.startswith("inst_rate_"))
async def process_installment_rate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rate = float(callback.data.replace("inst_rate_", ""))
    await state.update_data(installment_rate=rate)
    await state.set_state(InvestForm.installment_term)
    await state.update_data(page=0)
    await show_installment_term(callback.message, state)


# ============================================
# РАССРОЧКА: СРОК
# ============================================

async def show_installment_term(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    page = data.get("page", 0)
    rate = data.get("installment_rate", 0)
    
    keyboard = get_installment_term_keyboard(page)
    options = list(range(1, 16))
    total_pages = (len(options) + 4) // 5
    
    text = f"📅 **Выберите срок рассрочки**\n\n💸 Ставка: {rate}%\n\n(страница {page+1}/{total_pages})"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_inst_rate")
async def back_to_installment_rate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.installment_rate)
    await show_installment(callback.message, state)


@router.callback_query(F.data.startswith("term_page_"))
async def term_pagination(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)
    
    if "prev" in callback.data:
        page = max(0, page - 1)
    elif "next" in callback.data:
        page = max(0, page + 1)
    
    await state.update_data(page=page)
    await show_installment_term(callback.message, state)


@router.callback_query(F.data.startswith("inst_term_"))
async def process_installment_term(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    term = int(callback.data.replace("inst_term_", ""))
    await state.update_data(installment_term=term)
    
    await state.set_state(InvestForm.uk_commission)
    await show_uk_commission(callback.message, state)


# ============================================
# УПРАВЛЯЮЩАЯ КОМПАНИЯ
# ============================================

async def show_uk_commission(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    rent_type = data.get("rent_type", "short")
    
    keyboard = get_uk_keyboard(rent_type)
    
    if rent_type == "short":
        text = "🏢 **Выберите комиссию УК (посуточная аренда):**"
    else:
        text = "🏢 **Выберите комиссию УК (долгосрочная аренда):**"
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_inst_term")
async def back_to_installment_term_from_uk(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.installment_term)
    await state.update_data(page=0)
    await show_installment_term(callback.message, state)


@router.callback_query(F.data.startswith("uk_"))
async def process_uk_commission(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    uk = int(callback.data.replace("uk_", ""))
    await state.update_data(uk_commission=uk)
    
    await state.set_state(InvestForm.management_class)
    await show_management_class(callback.message, state)


# ============================================
# КЛАСС ЖИЛЬЯ
# ============================================

async def show_management_class(message: Message, state: FSMContext, edit: bool = True):
    keyboard = get_management_class_keyboard()
    text = (
        "🏢 **Выберите класс жилья**\n\n"
        "От этого зависит Maintenance Fee:\n"
        "• Эконом: 40-60 ฿/м²/мес\n"
        "• Средний: 60-80 ฿/м²/мес\n"
        "• Премиум: 80-120 ฿/м²/мес\n"
        "• Люкс: 120-200+ ฿/м²/мес"
    )
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_uk")
async def back_to_uk(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.uk_commission)
    await show_uk_commission(callback.message, state)


@router.callback_query(F.data.startswith("mclass_"))
async def process_management_class(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    mclass = callback.data.replace("mclass_", "")
    await state.update_data(management_class=mclass)
    
    await state.set_state(InvestForm.ownership_type)
    await show_ownership_type(callback.message, state)


# ============================================
# ТИП ПРАВА СОБСТВЕННОСТИ
# ============================================

async def show_ownership_type(message: Message, state: FSMContext, edit: bool = True):
    keyboard = get_ownership_keyboard()
    text = (
        "🏠 **Выберите тип права собственности**\n\n"
        "• **Freehold** — полная собственность\n"
        "  Land Tax: 0.02%\n\n"
        "• **Leasehold** — аренда земли (30+ лет)\n"
        "  Регистрационный сбор: 1.1%\n"
        "  Возможна амортизация права аренды"
    )
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "back_mclass")
async def back_to_mclass(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(InvestForm.management_class)
    await show_management_class(callback.message, state)


@router.callback_query(F.data.startswith("own_"))
async def process_ownership(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    ownership = "freehold" if callback.data == "own_freehold" else "leasehold"
    await state.update_data(ownership=ownership)
    
    await show_result(callback.message, state)


# ============================================
# РЕЗУЛЬТАТ
# ============================================

async def show_result(message: Message, state: FSMContext, edit: bool = True):
    data = await state.get_data()
    
    # Извлекаем данные
    region = data.get("region")
    district = data.get("district")
    prop_type = data.get("property_type")
    rent_type = data.get("rent_type")
    price = data.get("price", 0)
    dp_percent = data.get("downpayment", 30)
    dp_amount = data.get("dp_amount", 0)
    rate = data.get("installment_rate", 0)
    term = data.get("installment_term", 5)
    uk = data.get("uk_commission", 30)
    mclass = data.get("management_class", "Средний")
    ownership = data.get("ownership", "freehold")
    
    # Данные аренды
    rent_data = RENTS[region][district][prop_type]
    rent_high = rent_data["high"]
    rent_low = rent_data["low"]
    occupancy = rent_data["occupancy"]
    sqm = rent_data.get("sqm", "—")
    
    # Расчеты
    gross_income = calc_gross_income(rent_high, rent_low, occupancy)
    
    maint_rate = MAINTENANCE_RATES.get(region, {}).get(mclass, 70)
    sqm_num = get_sqm_number(sqm)
    maintenance = maint_rate * sqm_num * 12
    
    land_tax = price * 0.0002
    uk_fee = gross_income * uk / 100
    pit = calc_pit(gross_income - uk_fee, "standard")
    avg_rent = (rent_high + rent_low) / 2
    vacancy = avg_rent
    repair = 15000
    
    total_expenses = maintenance + land_tax + uk_fee + pit + vacancy + repair
    net_income = gross_income - total_expenses
    real_yield = calc_real_yield(net_income, price)
    roi = calc_roi(net_income, dp_amount)
    
    # Сохраняем для PDF
    data["_gross_income"] = gross_income
    data["_total_expenses"] = total_expenses
    data["_net_income"] = net_income
    data["_real_yield"] = real_yield
    data["_roi"] = roi
    data["_sqm"] = sqm
    data["_uk_fee"] = uk_fee
    data["_maintenance"] = maintenance
    data["_land_tax"] = land_tax
    data["_pit"] = pit
    data["_vacancy"] = vacancy
    data["_repair"] = repair
    await state.update_data(data)
    
    # Расчет рассрочки
    credit_amount = price - dp_amount
    installment_payment = calc_installment(credit_amount, rate, term)
    
    result_text = (
        f"🏝️ **ИНВЕСТИЦИОННЫЙ ОТЧЕТ**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 **Объект**\n"
        f"Регион: {region}\n"
        f"Район: {district}\n"
        f"Тип: {prop_type}\n"
        f"Площадь: {sqm} м²\n"
        f"Цена: {price:,} ฿\n\n"
        f"💸 **Финансирование**\n"
        f"ПВ: {dp_percent}% ({dp_amount:,} ฿)\n"
        f"Рассрочка: {credit_amount:,} ฿ на {term} лет под {rate}%\n"
        f"Ежеквартальный платёж: {installment_payment:,.0f} ฿\n\n"
        f"🏖️ **Аренда ({'посуточная' if rent_type == 'short' else 'долгосрочная'})**\n"
        f"High: {rent_high:,} ฿/мес | Low: {rent_low:,} ฿/мес\n"
        f"Заполняемость: {occupancy}%\n"
        f"Валовый доход: {gross_income:,.0f} ฿/год\n\n"
        f"📊 **Расходы (в год)**\n"
        f"УК ({uk}%): -{uk_fee:,.0f} ฿\n"
        f"Maintenance: -{maintenance:,.0f} ฿\n"
        f"Land Tax: -{land_tax:,.0f} ฿\n"
        f"Налог PIT: -{pit:,.0f} ฿\n"
        f"Простой: -{vacancy:,.0f} ฿\n"
        f"Мелкий ремонт: -{repair:,.0f} ฿\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ **ЧИСТЫЙ ДОХОД: {net_income:,.0f} ฿/год**\n"
        f"📊 **Реальная доходность: {real_yield:.1f}%**\n"
        f"📊 **ROI (от ПВ): {roi:.1f}%**\n"
        f"🏠 **Тип права: {ownership.upper()}**\n"
    )
    
    keyboard = get_result_keyboard()
    
    if edit:
        await message.edit_text(result_text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(result_text, reply_markup=keyboard, parse_mode="Markdown")


# ============================================
# ЭКСПОРТ PDF
# ============================================

@router.callback_query(F.data == "export_pdf")
async def export_pdf(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()
    
    if not data.get("price"):
        await callback.message.answer(
            "❌ Нет данных для экспорта. Сначала выполните расчет."
        )
        return
    
    msg = await callback.message.answer("⏳ Генерация PDF-отчета...")
    
    try:
        filepath = export_to_pdf(data, callback.from_user.id)
        
        await callback.message.answer_document(
            document=FSInputFile(filepath),
            caption="📊 **Инвестиционный отчет успешно создан!**\n\n"
                    "PDF-отчет содержит:\n"
                    "• 📋 Параметры объекта и финансирования\n"
                    "• 📈 Детальный расчет доходности\n"
                    "• 📅 График платежей по рассрочке\n"
                    "• 📊 Графики роста и сравнения доходности\n"
                    "• ✅ Итоговые показатели (ROI, доходность)\n\n"
                    "✅ Отчет готов к печати или отправке клиенту",
            parse_mode="Markdown"
        )
        
        os.remove(filepath)
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка при создании отчета: {str(e)}")


# ============================================
# IGNORE (для пагинации)
# ============================================

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()