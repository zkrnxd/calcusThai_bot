# utils/keyboards.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.rents import RENTS

def get_regions_keyboard(page=0):
    regions = list(RENTS.keys())
    items_per_page = 2
    total_pages = (len(regions) + items_per_page - 1) // items_per_page
    
    start = page * items_per_page
    end = min(start + items_per_page, len(regions))
    
    builder = InlineKeyboardBuilder()
    for region in regions[start:end]:
        builder.button(text=f"📍 {region}", callback_data=f"region_{region}")
    builder.adjust(2)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data="region_page_prev"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data="region_page_next"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def get_districts_keyboard(region, page=0):
    districts = list(RENTS[region].keys())
    items_per_page = 3
    total_pages = (len(districts) + items_per_page - 1) // items_per_page
    
    start = page * items_per_page
    end = min(start + items_per_page, len(districts))
    
    builder = InlineKeyboardBuilder()
    for district in districts[start:end]:
        builder.button(text=f"🏘️ {district}", callback_data=f"district_{district}")
    builder.adjust(1)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data="district_page_prev"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data="district_page_next"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(
        InlineKeyboardButton("🔙 Назад", callback_data="back_region"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    )
    return builder.as_markup()

def get_property_types_keyboard(region, district, page=0):
    types = list(RENTS[region][district].keys())
    items_per_page = 3
    total_pages = (len(types) + items_per_page - 1) // items_per_page
    
    start = page * items_per_page
    end = min(start + items_per_page, len(types))
    
    builder = InlineKeyboardBuilder()
    for prop_type in types[start:end]:
        builder.button(text=f"🏠 {prop_type}", callback_data=f"ptype_{prop_type}")
    builder.adjust(1)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data="ptype_page_prev"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data="ptype_page_next"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(
        InlineKeyboardButton("🔙 Назад", callback_data="back_district"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    )
    return builder.as_markup()

def get_downpayment_keyboard(page=0):
    options = list(range(20, 105, 5))
    items_per_page = 5
    total_pages = (len(options) + items_per_page - 1) // items_per_page
    
    start = page * items_per_page
    end = min(start + items_per_page, len(options))
    
    builder = InlineKeyboardBuilder()
    for opt in options[start:end]:
        builder.button(text=f"{opt}%", callback_data=f"dp_{opt}")
    builder.adjust(5)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data="dp_page_prev"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data="dp_page_next"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_price"))
    return builder.as_markup()

def get_installment_rate_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="0% (беспроцентная)", callback_data="inst_rate_0")
    
    rates = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    for rate in rates:
        builder.button(text=f"{rate}%", callback_data=f"inst_rate_{rate}")
    builder.adjust(3)
    
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_dp"))
    return builder.as_markup()

def get_installment_term_keyboard(page=0):
    options = list(range(1, 16))
    items_per_page = 5
    total_pages = (len(options) + items_per_page - 1) // items_per_page
    
    start = page * items_per_page
    end = min(start + items_per_page, len(options))
    
    builder = InlineKeyboardBuilder()
    for opt in options[start:end]:
        label = f"{opt} лет" if opt > 1 else "1 год"
        builder.button(text=label, callback_data=f"inst_term_{opt}")
    builder.adjust(5)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️", callback_data="term_page_prev"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️", callback_data="term_page_next"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_inst_rate"))
    return builder.as_markup()

def get_uk_keyboard(rent_type):
    if rent_type == "short":
        options = [20, 25, 30, 35, 40]
    else:
        options = [8, 10, 12]
    
    builder = InlineKeyboardBuilder()
    for opt in options:
        builder.button(text=f"{opt}%", callback_data=f"uk_{opt}")
    builder.adjust(5 if rent_type == "short" else 3)
    
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_inst_term"))
    return builder.as_markup()

def get_management_class_keyboard():
    classes = ["Эконом", "Средний", "Премиум", "Люкс"]
    builder = InlineKeyboardBuilder()
    for cls in classes:
        builder.button(text=f"🏢 {cls}", callback_data=f"mclass_{cls}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_uk"))
    return builder.as_markup()

def get_ownership_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Freehold", callback_data="own_freehold")
    builder.button(text="📄 Leasehold", callback_data="own_leasehold")
    builder.adjust(2)
    builder.row(InlineKeyboardButton("🔙 Назад", callback_data="back_mclass"))
    return builder.as_markup()

def get_result_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔄 Новый расчет", callback_data="new_calc")],
        [InlineKeyboardButton("📄 Скачать PDF-отчет", callback_data="export_pdf")],
    ])

def get_back_keyboard(callback_data):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔙 Назад", callback_data=callback_data)]
    ])