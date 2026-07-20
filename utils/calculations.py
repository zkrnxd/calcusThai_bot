# utils/calculations.py

from data.costs import PIT_BRACKETS
from data.growth import GROWTH_RATES

def calc_gross_income(rent_high, rent_low, occupancy):
    high_income = rent_high * 6
    low_income = rent_low * 6
    return (high_income + low_income) * (occupancy / 100)

def calc_pit(income, method="standard", actual_expenses=0):
    if method == "standard":
        taxable = income * 0.7
    else:
        taxable = max(0, income - actual_expenses)
    
    if taxable <= 150000:
        return 0
    
    tax = 0
    for low, high, rate in PIT_BRACKETS:
        if taxable > low:
            amount = min(taxable, high) - low
            if amount > 0:
                tax += amount * rate
    return tax

def calc_future_price(price, region, years):
    total_growth = GROWTH_RATES.get(region, {}).get("total", 0.08)
    return price * (1 + total_growth) ** years

def calc_installment(amount, rate, years):
    if rate == 0:
        return amount / (years * 4)
    q_rate = rate / 100 / 4
    n = years * 4
    if q_rate == 0:
        return amount / n
    return amount * (q_rate * (1 + q_rate) ** n) / ((1 + q_rate) ** n - 1)

def calc_cash_flow(gross_income, expenses):
    return gross_income - expenses

def calc_roi(net_profit, initial_investment):
    if initial_investment == 0:
        return 0
    return (net_profit / initial_investment) * 100

def calc_real_yield(net_income, price):
    if price == 0:
        return 0
    return (net_income / price) * 100

def get_sqm_number(sqm_str):
    try:
        if "-" in str(sqm_str):
            return int(str(sqm_str).split("-")[0])
        return int(sqm_str)
    except:
        return 35