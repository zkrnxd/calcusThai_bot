# utils/charts.py

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

from data.growth import GROWTH_RATES

def setup_fonts():
    try:
        font_paths = [
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'C:/Windows/Fonts/arial.ttf',
        ]
        for path in font_paths:
            if os.path.exists(path):
                fm.fontManager.addfont(path)
                plt.rcParams['font.family'] = fm.FontProperties(fname=path).get_name()
                return
    except:
        pass
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

setup_fonts()

def create_price_growth_chart(data: dict, save_path: str) -> str:
    region = data.get('region', 'Пхукет')
    price = data.get('price', 5000000)
    years = 10
    
    growth_rate = GROWTH_RATES.get(region, {}).get('total', 0.08)
    
    years_array = list(range(years + 1))
    prices = [price * (1 + growth_rate) ** year for year in years_array]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(years_array, prices, color='#1a3c6e', linewidth=3, marker='o', markersize=8)
    ax.fill_between(years_array, 0, prices, alpha=0.15, color='#1a3c6e')
    
    for i, (year, price_val) in enumerate(zip(years_array, prices)):
        if i % 2 == 0:
            ax.annotate(f'{price_val:,.0f} ฿', xy=(year, price_val),
                       xytext=(0, 10), textcoords='offset points',
                       ha='center', fontsize=9, fontweight='bold', color='#1a3c6e')
    
    ax.axhline(y=price, color='red', linestyle='--', alpha=0.5,
               label=f'Текущая цена: {price:,.0f} ฿')
    
    ax.set_xlabel('Год владения', fontsize=12, fontweight='bold')
    ax.set_ylabel('Стоимость (฿)', fontsize=12, fontweight='bold')
    ax.set_title(f'Прогноз роста цены — {region}', fontsize=14, fontweight='bold', color='#1a3c6e')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k' if x >= 1000 else str(int(x))))
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(0, max(prices) * 1.15)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path

def create_rent_vs_expenses_chart(data: dict, save_path: str) -> str:
    gross_income = data.get('_gross_income', 0)
    total_expenses = data.get('_total_expenses', 0)
    net_income = data.get('_net_income', 0)
    
    categories = ['Валовый доход', 'Расходы', 'Чистый доход']
    values = [gross_income, total_expenses, net_income]
    colors = ['#28a745', '#dc3545', '#1a3c6e']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val:,.0f} ฿', xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5), textcoords='offset points',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_title('Структура доходов и расходов (год)', fontsize=14, fontweight='bold', color='#1a3c6e')
    ax.set_ylabel('Сумма (฿)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k' if x >= 1000 else str(int(x))))
    
    if gross_income > 0:
        net_percent = (net_income / gross_income) * 100
        ax.annotate(f'Маржа: {net_percent:.1f}%', xy=(2, net_income),
                   xytext=(0, -30), textcoords='offset points',
                   ha='center', fontsize=12, fontweight='bold', color='#1a3c6e')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path

def create_roi_comparison_chart(data: dict, save_path: str) -> str:
    roi = data.get('_roi', 0)
    
    categories = ['Недвижимость', 'Депозит 3%', 'Депозит 5%', 'Инфляция']
    values = [roi, 3.0, 5.0, 2.0]
    colors = ['#1a3c6e', '#ffc107', '#ff9800', '#dc3545']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                   xytext=(0, 5), textcoords='offset points',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
    ax.set_title('Сравнение доходности с альтернативами', fontsize=14, fontweight='bold', color='#1a3c6e')
    ax.set_ylabel('Доходность (%)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_axisbelow(True)
    
    bars[0].set_color('#1a3c6e')
    bars[0].set_alpha(1.0)
    bars[0].set_edgecolor('#0d2647')
    bars[0].set_linewidth(3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return save_path