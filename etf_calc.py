import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="DE ETF Calc", layout="wide")
st.title("🇩🇪 German ETF Tax & Growth (Purchasing Power Edition)")

# 1. INPUTS
st.sidebar.header("Settings")
init_cap = st.sidebar.number_input("Initial Capital (€)", value=100)
monthly_save_init = st.sidebar.number_input("Starting Monthly Saving (€)", value=100)
years = st.sidebar.slider("Years", 1, 40, 30)
rate = st.sidebar.slider("Market Return (%)", 0.0, 15.0, 9.0) / 100
inflation = st.sidebar.slider("Inflation (%)", 0.0, 5.0, 2.0) / 100
dynamics = st.sidebar.slider("Annual Savings Increase (%)", 0.0, 5.0, 2.0) / 100

st.sidebar.header("Tax Settings")
allowance = st.sidebar.number_input("Tax-Free Allowance (€)", value=1000)
equity_etf = st.sidebar.checkbox("Equity ETF (30% Exemption)", value=True)

# 2. LOGIC
months = years * 12
data = []
balance = init_cap
total_invested = init_cap
accumulated_vorab_tax = 0
current_monthly_save = monthly_save_init
basiszins = 0.0253
exemption = 0.7 if equity_etf else 1.0
tax_rate = 0.26375 

for m in range(1, months + 1):
    if m > 1 and m % 12 == 1:
        current_monthly_save = current_monthly_save * (1 + dynamics)
    if m % 12 == 1:
        val_jan_1 = balance
    balance = balance * (1 + rate/12) + current_monthly_save
    total_invested += current_monthly_save
    if m % 12 == 0:
        year = m // 12
        actual_gain = balance - val_jan_1
        basisertrag = val_jan_1 * basiszins * 0.7
        vorab_base = max(0, min(actual_gain, basisertrag))
        taxable_vorab = max(0, (vorab_base * exemption) - allowance)
        yearly_vorab_tax = taxable_vorab * tax_rate
        accumulated_vorab_tax += yearly_vorab_tax
        total_profit = balance - total_invested
        final_taxable = max(0, (total_profit * exemption) - allowance)
        exit_tax = max(0, (final_taxable * tax_rate) - accumulated_vorab_tax)
        net_val = balance - exit_tax - accumulated_vorab_tax
        real_val = net_val / ((1 + inflation) ** year)
        data.append({"Year": year, "Nominal": round(balance, 2), "Real Value": round(real_val, 2), "Invested": total_invested, "Monthly Rate": round(current_monthly_save, 2)})

# 3. WITHDRAWAL CALCULATIONS
df = pd.DataFrame(data)
final_nominal = df.iloc[-1]['Nominal']
final_real = df.iloc[-1]['Real Value']
effective_tax = tax_rate * exemption

# Nominal Withdrawal (What the bank sends you)
monthly_nom_net = (final_nominal * 0.04 / 12) * (1 - effective_tax)

# Real Withdrawal (Purchasing power in today's money)
monthly_real_net = (final_real * 0.04 / 12) * (1 - effective_tax)

# 4. OUTPUT DISPLAY
st.metric("Final Purchasing Power (Real Value)", f"€{final_real:,.2f}")

col1, col2 = st.columns(2)
with col1:
    st.success(f"💶 **Nominal Payout:** In {years} years, you can withdraw **€{monthly_nom_net:,.2f} net** per month.")
with col2:
    st.info(f"🛒 **Purchasing Power:** That payout will feel like **€{monthly_real_net:,.2f}** in today's money.")

st.warning(f"⚠️ To have the same lifestyle as €3,000 today, your 'Purchasing Power' result above should be €3,000.")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Year"], y=df["Invested"], name="Total Deposits", fill='tozeroy', line=dict(color='lightgrey')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Nominal"], name="Nominal Balance", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Real Value"], name="Real Value (Today's €)", line=dict(dash='dash', color='orange')))
st.plotly_chart(fig, use_container_width=True)
