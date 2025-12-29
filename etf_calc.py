import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="DE ETF Calc", layout="wide")
st.title("🇩🇪 German ETF Tax & Growth")

# 1. INPUTS
st.sidebar.header("Settings")
init_cap = st.sidebar.number_input("Initial Capital (€)", value=100)
monthly_save = st.sidebar.number_input("Monthly Saving (€)", value=100)
years = st.sidebar.slider("Years", 1, 40, 30)
rate = st.sidebar.slider("Return (%)", 0.0, 12.0, 7.0) / 100
inflation = st.sidebar.slider("Inflation (%)", 0.0, 5.0, 2.0) / 100
allowance = st.sidebar.number_input("Tax-Free Allowance (€)", value=1000)
equity_etf = st.sidebar.checkbox("Equity ETF (30% Exemption)", value=True)

# 2. LOGIC
months = years * 12
data = []
balance = init_cap
total_invested = init_cap
accumulated_vorab_tax = 0
basiszins = 0.0253
exemption = 0.7 if equity_etf else 1.0
tax_rate = 0.26375 

for m in range(1, months + 1):
    if m % 12 == 1:
        val_jan_1 = balance
    
    # Calculation lines (Ensure exactly 4 spaces before these)
    balance = balance * (1 + rate/12) + monthly_save
    total_invested += monthly_save
    
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
        data.append({"Year": year, "Nominal": round(balance, 2), "After Tax": round(net_val, 2), "Real Value": round(real_val, 2), "Invested": total_invested})

# 3. OUTPUT
df = pd.DataFrame(data)
st.metric("Future Purchasing Power (Real €)", f"€{df.iloc[-1]['Real Value']:,.2f}")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Year"], y=df["Invested"], name="Total Deposits", fill='tozeroy', line=dict(color='lightgrey')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Nominal"], name="Total (Before Tax)", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Real Value"], name="Real Value (Inflation Adj)", line=dict(dash='dash', color='orange')))
st.plotly_chart(fig, use_container_width=True)
