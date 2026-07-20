# utils/pdf_exporter.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config import EXPORT_DIR, TEMP_DIR, LOGO_PATH
from data.rents import RENTS
from data.costs import MAINTENANCE_RATES
from utils.calculations import *
from utils.charts import (
    create_price_growth_chart,
    create_rent_vs_expenses_chart,
    create_roi_comparison_chart
)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def export_to_pdf(data: dict, user_id: int) -> str:
    ensure_dir(EXPORT_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"investment_report_{user_id}_{timestamp}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )
    
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a3c6e'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5b8a'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubHeader',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#3a6da0'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='Label',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='BigNumber',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#1a3c6e'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    elements = []
    
    # ========== СТРАНИЦА 1: ТИТУЛЬНАЯ ==========
    elements.append(Spacer(1, 20*mm))
    
    if os.path.exists(LOGO_PATH):
        try:
            img = Image(LOGO_PATH, width=60*mm, height=20*mm)
            img.hAlign = 'CENTER'
            elements.append(img)
        except:
            pass
    
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("ИНВЕСТИЦИОННЫЙ ОТЧЕТ", styles['CustomTitle']))
    elements.append(Paragraph(f"<b>{data.get('region', '')} / {data.get('district', '')}</b>", styles['BigNumber']))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(data.get('property_type', ''), styles['SubHeader']))
    elements.append(Spacer(1, 15*mm))
    
    # Ключевые цифры
    stats_data = [
        ["💰 Цена объекта", f"{data.get('price', 0):,.0f} ฿"],
        ["📈 Чистый доход/год", f"{data.get('_net_income', 0):,.0f} ฿"],
        ["📊 Реальная доходность", f"{data.get('_real_yield', 0):.1f}%"],
        ["📊 ROI (от ПВ)", f"{data.get('_roi', 0):.1f}%"],
    ]
    
    stats_table = Table(stats_data, colWidths=[80*mm, 70*mm])
    stats_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#444444')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a3c6e')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(stats_table)
    
    elements.append(Spacer(1, 20*mm))
    elements.append(Paragraph(f"Дата: {datetime.now().strftime('%d %B %Y')}", styles['Label']))
    
    # ========== СТРАНИЦА 2: ПАРАМЕТРЫ ==========
    elements.append(PageBreak())
    elements.append(Paragraph("1. ПАРАМЕТРЫ ОБЪЕКТА", styles['SectionHeader']))
    
    params_data = [
        ["Регион", data.get('region', '')],
        ["Район", data.get('district', '')],
        ["Тип объекта", data.get('property_type', '')],
        ["Площадь", data.get('sqm', '—')],
        ["Тип права", data.get('ownership', 'freehold').upper()],
        ["Класс жилья", data.get('management_class', 'Средний')],
        ["Тип аренды", "Посуточная" if data.get('rent_type') == 'short' else "Долгосрочная"],
    ]
    
    params_table = Table(params_data, colWidths=[60*mm, 80*mm])
    params_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#444444')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a3c6e')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(params_table)
    
    # Финансы
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("ФИНАНСИРОВАНИЕ", styles['SubHeader']))
    
    finance_data = [
        ["Цена объекта", f"{data.get('price', 0):,.0f} ฿"],
        ["Первый взнос", f"{data.get('downpayment', 30)}% ({data.get('dp_amount', 0):,.0f} ฿)"],
        ["В рассрочку", f"{data.get('price', 0) - data.get('dp_amount', 0):,.0f} ฿"],
        ["Ставка", f"{data.get('installment_rate', 0)}%"],
        ["Срок", f"{data.get('installment_term', 5)} лет"],
        ["Комиссия УК", f"{data.get('uk_commission', 30)}%"],
    ]
    
    finance_table = Table(finance_data, colWidths=[60*mm, 80*mm])
    finance_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#444444')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a3c6e')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(finance_table)
    
    # ========== СТРАНИЦА 3: РАСЧЕТ ==========
    elements.append(PageBreak())
    elements.append(Paragraph("2. ДЕТАЛЬНЫЙ РАСЧЕТ", styles['SectionHeader']))
    
    gross_income = data.get('_gross_income', 0)
    total_expenses = data.get('_total_expenses', 0)
    net_income = data.get('_net_income', 0)
    
    calc_data = [
        ["ДОХОДЫ", "", ""],
        ["Валовый арендный доход", f"{gross_income:,.0f} ฿", "High + Low с заполняемостью"],
        ["", "", ""],
        ["РАСХОДЫ", "", ""],
        ["Комиссия УК", f"{data.get('_uk_fee', 0):,.0f} ฿", f"{data.get('uk_commission', 30)}% от валового дохода"],
        ["Maintenance Fee", f"{data.get('_maintenance', 0):,.0f} ฿", "Ежемесячно"],
        ["Land & Building Tax", f"{data.get('_land_tax', 0):,.0f} ฿", "0.02% от цены"],
        ["Налог PIT", f"{data.get('_pit', 0):,.0f} ฿", "Стандартный вычет 30%"],
        ["Простой (1 мес)", f"{data.get('_vacancy', 0):,.0f} ฿", "Средняя аренда"],
        ["Мелкий ремонт", f"{data.get('_repair', 15000):,.0f} ฿", "Ежегодно"],
        ["", "", ""],
        ["ИТОГО РАСХОДОВ", f"{total_expenses:,.0f} ฿", ""],
        ["", "", ""],
        ["ЧИСТЫЙ ДОХОД (год)", f"{net_income:,.0f} ฿", ""],
    ]
    
    calc_table = Table(calc_data, colWidths=[60*mm, 40*mm, 50*mm])
    calc_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (1, 4), (1, 10), colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (1, 12), (1, 12), colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (1, 14), (1, 14), colors.HexColor('#28a745')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#eeeeee')),
        ('FONT', (0, 14), (-1, 14), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 14), (-1, 14), 12),
    ]))
    elements.append(calc_table)
    
    # ========== СТРАНИЦА 4: ГРАФИК РАССРОЧКИ ==========
    elements.append(PageBreak())
    elements.append(Paragraph("3. ГРАФИК ПЛАТЕЖЕЙ ПО РАССРОЧКЕ", styles['SectionHeader']))
    
    price = data.get('price', 0)
    dp_amount = data.get('dp_amount', 0)
    rate = data.get('installment_rate', 0)
    term = data.get('installment_term', 5)
    
    credit_amount = price - dp_amount
    q_payment = calc_installment(credit_amount, rate, term)
    
    summary_data = [
        ["Сумма рассрочки", f"{credit_amount:,.0f} ฿"],
        ["Ежеквартальный платёж", f"{q_payment:,.2f} ฿"],
        ["Общая переплата", f"{(q_payment * term * 4 - credit_amount):,.2f} ฿"],
    ]
    
    summary_table = Table(summary_data, colWidths=[70*mm, 70*mm])
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#444444')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a3c6e')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(summary_table)
    
    elements.append(Spacer(1, 10*mm))
    
    # График платежей
    schedule_data = [["Квартал", "Платёж (฿)", "Проценты (฿)", "Долг (฿)", "Остаток (฿)"]]
    
    balance = credit_amount
    q_rate = rate / 100 / 4 if rate > 0 else 0
    total_quarters = term * 4
    display_quarters = min(total_quarters, 12)
    
    for q in range(1, display_quarters + 1):
        interest = balance * q_rate if rate > 0 else 0
        principal = q_payment - interest
        balance -= principal
        if balance < 0:
            balance = 0
        schedule_data.append([
            str(q),
            f"{q_payment:,.0f}",
            f"{interest:,.0f}",
            f"{principal:,.0f}",
            f"{balance:,.0f}"
        ])
    
    schedule_table = Table(schedule_data, colWidths=[25*mm, 30*mm, 30*mm, 30*mm, 30*mm])
    schedule_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3c6e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.WHITE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#dddddd')),
    ]))
    elements.append(schedule_table)
    
    if total_quarters > display_quarters:
        elements.append(Paragraph(
            f"<i>... и ещё {total_quarters - display_quarters} кварталов</i>",
            styles['Label']
        ))
    
    # ========== СТРАНИЦА 5: ГРАФИКИ ==========
    elements.append(PageBreak())
    elements.append(Paragraph("4. ВИЗУАЛИЗАЦИЯ", styles['SectionHeader']))
    
    ensure_dir(TEMP_DIR)
    temp_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        chart1_path = os.path.join(TEMP_DIR, f"chart_growth_{temp_timestamp}.png")
        create_price_growth_chart(data, chart1_path)
        img1 = Image(chart1_path, width=160*mm, height=90*mm)
        img1.hAlign = 'CENTER'
        elements.append(img1)
        elements.append(Spacer(1, 5*mm))
        os.remove(chart1_path)
        
        chart2_path = os.path.join(TEMP_DIR, f"chart_rent_{temp_timestamp}.png")
        create_rent_vs_expenses_chart(data, chart2_path)
        img2 = Image(chart2_path, width=160*mm, height=90*mm)
        img2.hAlign = 'CENTER'
        elements.append(img2)
        elements.append(Spacer(1, 5*mm))
        os.remove(chart2_path)
        
        chart3_path = os.path.join(TEMP_DIR, f"chart_roi_{temp_timestamp}.png")
        create_roi_comparison_chart(data, chart3_path)
        img3 = Image(chart3_path, width=160*mm, height=90*mm)
        img3.hAlign = 'CENTER'
        elements.append(img3)
        os.remove(chart3_path)
        
        os.rmdir(TEMP_DIR)
    except Exception as e:
        elements.append(Paragraph(
            f"<i>Графики: {str(e)}</i>",
            styles['Label']
        ))
    
    # ========== СТРАНИЦА 6: ИТОГИ ==========
    elements.append(PageBreak())
    elements.append(Paragraph("5. ИТОГОВЫЕ ПОКАЗАТЕЛИ", styles['SectionHeader']))
    
    result_data = [
        ["Показатель", "Значение"],
        ["Валовый доход", f"{gross_income:,.0f} ฿"],
        ["Чистый доход (год)", f"{net_income:,.0f} ฿"],
        ["Реальная доходность", f"{data.get('_real_yield', 0):.1f}%"],
        ["ROI (от ПВ)", f"{data.get('_roi', 0):.1f}%"],
        ["Срок окупаемости", f"{price / net_income:.1f} лет" if net_income > 0 else "∞"],
    ]
    
    result_table = Table(result_data, colWidths=[70*mm, 70*mm])
    result_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3c6e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.WHITE),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#28a745') if net_income > 0 else colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (1, 3), (1, 3), colors.HexColor('#28a745') if data.get('_real_yield', 0) > 0 else colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (1, 4), (1, 4), colors.HexColor('#28a745') if data.get('_roi', 0) > 0 else colors.HexColor('#dc3545')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
    ]))
    elements.append(result_table)
    
    doc.build(elements)
    return filepath