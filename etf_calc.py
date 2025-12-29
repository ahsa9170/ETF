import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Basic Page Setup
st.set_page_config(page_title="DE ETF Calc", layout="wide")
st.title("🇩🇪 German ETF Tax & Growth")

# --- SIDEBAR FOR INPUTS ---
with st.sidebar:
    st.header("1. Investment Basics")
    init_cap = st.number_input("Initial Capital (€)", value=100)
    monthly_save = st.number_input("Monthly Saving (€)", value=100)
    years = st.slider("Investment Period (Years)", 1, 40, 30)
    rate = st.slider("Expected Return (%)", 0.0, 12.0, 7.0) / 100
    inflation = st.slider("Annual Inflation (%)", 0.0, 5.0, 2.0) / 100
    
    st.header("2. German Tax Settings")
    allowance = st.number_input("Tax-Free Allowance (€)", value=1000)
    equity_etf = st.checkbox("Equity ETF (30% Exemption)", value=True)
    basiszins = 0.0253  # Official 2025 Basiszins

# --- CALCULATION ENGINE ---
months = years * 12
data = []
balance = init_cap
total_invested = init_cap
accumulated_vorab_tax = 0

# Tax Factors
exemption = 0.7 if equity_etf else 1.0
tax_rate = 0.26375 # 25% + Soli

for m in range(1, months + 1):
    # Capture start of year value for Vorabpauschale
    if m % 12 == 1:
        val_jan_1 = balance
    
    # Monthly Growth Calculation
    balance = balance * (1 + rate/12) + monthly_save
    total_invested += monthly_save
    
    # Annual Processing (Taxes and Inflation)
    if m % 12 == 0:
        year = m // 12
        
        # Vorabpauschale Logic
        actual_gain = balance - val_jan_1
        basisertrag = val_jan_1 * basiszins * 0.7
        vorab_base = max(0, min(actual_gain, basisertrag))
        
        taxable_vorab = max(0, (vorab_base * exemption) - allowance)
        yearly_vorab_tax = taxable_vorab * tax_rate
        accumulated_vorab_tax += yearly_vorab_tax
        
        # Final Exit Tax Calculation
        total_profit = balance - total_invested
        final_taxable = max(0, (total_profit * exemption) - allowance)
        exit_tax = max(0, (final_taxable * tax_rate) - accumulated_vorab_tax)
        
        # Values after tax and inflation
        net_val = balance - exit_tax - accumulated_vorab_tax
        real_val = net_val / ((1 + inflation) ** year)
        
        data.append({
            "Year": year,
            "Nominal": round(balance, 2),
            "After Tax": round(net_val, 2),
            "Real Value": round(real_val, 2),
            "Invested": total_invested
        })

# Create DataFrame
df = pd.DataFrame(data)

# --- VISUALIZATION ---
st.metric("Future Purchasing Power (Real €)", f"€{df.iloc[-1]['Real Value']:,.2f}")

fig = go.Figure()

# Add Area for Principal
fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Invested"], 
    name="Total Deposits", 
    fill='tozeroy', 
    line=dict(color='lightgrey')
))

# Add Line for Nominal Growth
fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Nominal"], 
    name="Total (Before Tax)", 
    line=dict(color='blue')
))

# Add Line for Inflation-Adjusted Value
fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Real Value"], 
    name="Real Value (Inflation Adjusted)", 
    line=dict(dash='dash', color='orange')
))

fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis_title="Years",
    yaxis_title="Euros (€)"
)

st.plotly_chart(fig, use_container_width=True)

# Detailed Data Table
with st.expander("View Yearly Data Table"):
    st.dataframe(df)
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
        
        data.append({
            "Year": year,
            "Nominal": round(balance, 2),
            "After Tax": round(net_val, 2),
            "Real Value": round(real_val, 2),
            "Invested": total_invested
        })

df = pd.DataFrame(data)

# --- DISPLAY ---
st.metric("Future Purchasing Power (Real €)", f"€{df.iloc[-1]['Real Value']:,.2f}")

fig = go.Figure()

# The FIX: Use go.Scatter with fill='tozeroy' instead of add_area
fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Invested"], 
    name="Your Total Deposits", 
    fill='tozeroy', 
    line=dict(color='gray')
))

fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Nominal"], 
    name="Nominal Balance (Market Value)", 
    line=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=df["Year"], 
    y=df["Real Value"], 
    name="Real Value (Today's €)", 
    line=dict(dash='dash', color='orange')
))

fig.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(df)

    # Growth
    balance = balance * (1 + rate/12) + monthly_save
    total_invested += monthly_save
    
    # Yearly Tax Calculation (Vorabpauschale)
    if m % 12 == 0:
        year = m // 12
        # Vorabpauschale Formula: Min(Actual Gain, Jan_1_Value * Basiszins * 0.7)
        actual_gain = balance - val_jan_1
        basisertrag = val_jan_1 * basiszins * 0.7
        vorab_base = max(0, min(actual_gain, basisertrag))
        
        # Apply exemption and allowance
        taxable_vorab = max(0, (vorab_base * exemption) - allowance)
        yearly_vorab_tax = taxable_vorab * tax_rate
        accumulated_vorab_tax += yearly_vorab_tax
        
        # Calculate Final Net and Real Value
        total_profit = balance - total_invested
        # Final tax if sold today (simplified)
        final_taxable = max(0, (total_profit * exemption) - allowance)
        # We subtract already paid Vorabpauschale to avoid double tax
        exit_tax = max(0, (final_taxable * tax_rate) - accumulated_vorab_tax)
        
        net_val = balance - exit_tax - accumulated_vorab_tax
        real_val = net_val / ((1 + inflation) ** year)
        
        data.append({
            "Year": year,
            "Nominal": round(balance, 2),
            "After Tax": round(net_val, 2),
            "Real Value": round(real_val, 2),
            "Invested": total_invested
        })

df = pd.DataFrame(data)

# --- DISPLAY ---
st.metric("Future Purchasing Power (Real €)", f"€{df.iloc[-1]['Real Value']:,.2f}")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Year"], y=df["Nominal"], name="Nominal Balance"))
fig.add_trace(go.Scatter(x=df["Year"], y=df["Real Value"], name="Real (Inflation Adj.)", line=dict(dash='dash')))
fig.add_area(x=df["Year"], y=df["Invested"], name="Your Deposits")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(df)
