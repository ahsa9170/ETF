import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="DE ETF Calc", layout="wide")
st.title("🇩🇪 German ETF Tax & Growth")

# 1. INPUTS
st.sidebar.header("Investment Settings")
init_cap = st.sidebar.number_input("Initial Capital (€)", value=100)
monthly_save_init = st.sidebar.number_input("Starting Monthly Saving (€)", value=100)
years = st.sidebar.slider("Years of Saving", 1, 40, 30)
rate = st.sidebar.slider("Market Return (%)", 0.0, 15.0, 9.0) / 100
inflation = st.sidebar.slider("Annual Inflation (%)", 0.0, 5.0, 2.0) / 100

st.sidebar.header("Dynamics")
# Restored: Increases your monthly contribution every year to keep pace with your career/inflation
dynamics = st.sidebar.slider("Annual Savings Increase (%)", 0.0, 10.0, 2.0) / 100

st.sidebar.header("Tax Settings")
allowance = st.sidebar.number_input("Tax-Free Allowance (€)", value=1000)
equity_etf = st.sidebar.checkbox("Equity ETF (30% Exemption)", value=True)

# 2. CALCULATION LOGIC
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
    # Apply Annual Dynamics (Increase savings amount every 12 months)
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
        
        # Taxes if sold today
        total_profit = balance - total_invested
        final_taxable = max(0, (total_profit * exemption) - allowance)
        exit_tax = max(0, (final_taxable * tax_rate) - accumulated_vorab_tax)
        
        net_val = balance - exit_tax - accumulated_vorab_tax
        real_val = net_val / ((1 + inflation) ** year)
        
        data.append({
            "Year": year, 
            "Nominal": round(balance, 2), 
            "Real Value": round(real_val, 2), 
            "Invested": total_invested,
            "Monthly Rate": round(current_monthly_save, 2)
        })

# 3. WITHDRAWAL LOGIC
df = pd.DataFrame(data)
final_nominal = df.iloc[-1]['Nominal']
final_real = df.iloc[-1]['Real Value']
effective_tax = tax_rate * exemption

# Based on 4% Safe Withdrawal Rate (SWR)
# Nominal = The actual Euros sent to you in the future
monthly_nom_net = (final_nominal * 0.04 / 12) * (1 - effective_tax)
# Real = What that money buys in today's terms
monthly_real_net = (final_real * 0.04 / 12) * (1 - effective_tax)

# 4. OUTPUTS
st.metric("Final Balance (Today's Purchasing Power)", f"€{final_real:,.2f}")

col1, col2 = st.columns(2)
with col1:
    st.success(f"💶 **Nominal Monthly Payout:** €{monthly_nom_net:,.2f}")
    st.caption(f"The actual amount you receive in Year {years}")
with col2:
    st.info(f"🛒 **Purchasing Power:** €{monthly_real_net:,.2f}")
    st.caption("What this payout 'feels like' in today's money")

st.divider()

# Charts
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Year"], y=df["Invested"], name="Total Deposits", fill='tozeroy', line=dict(color='lightgrey')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Nominal"], name="Nominal Balance (Market Value)", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Real Value"], name="Real Value (Today's €)", line=dict(dash='dash', color='orange')))
fig.update_layout(legend=dict(orientation="h", y=1.1), margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

st.write(f"ℹ️ By year {years}, your monthly contribution will have grown to **€{df.iloc[-1]['Monthly Rate']:.2f}** due to the {dynamics*100:.1f}% annual increase.")
