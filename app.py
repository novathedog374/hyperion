import streamlit as st
import pandas as pd
import yfinance as yf

# Load S&P 500 companies list from Wikipedia
@st.cache_data
def load_sp500_companies():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_df = tables[0]
    return sp500_df[['Symbol', 'Security', 'GICS Sector']]

# Function to get PE ratio of a company
@st.cache_data
def get_pe_ratio(ticker):
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('trailingPE', None)
    except:
        return None

# Main app
sp500_df = load_sp500_companies()

st.title("Rupiosity - Hyperion")

# User inputs
selected_stocks = st.multiselect("Select S&P 500 Companies you've invested in:", sp500_df['Symbol'])

investment_details = {}
if selected_stocks:
    st.write("### Enter investment year and quarter for each stock:")
    for stock in selected_stocks:
        col1, col2 = st.columns(2)
        year = col1.selectbox(f"Year for {stock}", list(range(2000, 2026)), key=f"year_{stock}")
        quarter = col2.selectbox(f"Quarter for {stock}", ['Q1', 'Q2', 'Q3', 'Q4'], key=f"quarter_{stock}")
        investment_details[stock] = {'year': year, 'quarter': quarter}

    if st.button("Submit"):
        selected_sectors = sp500_df[sp500_df['Symbol'].isin(selected_stocks)]['GICS Sector'].unique()

        sector_companies = sp500_df[sp500_df['GICS Sector'].isin(selected_sectors)].copy()
        sector_companies['PE Ratio'] = sector_companies['Symbol'].apply(get_pe_ratio)
        sector_companies.dropna(inplace=True)

        selected_pes = [get_pe_ratio(stock) for stock in selected_stocks if get_pe_ratio(stock)]
        avg_selected_pe = sum(selected_pes) / len(selected_pes) if selected_pes else None

        if avg_selected_pe:
            sector_companies['PE Difference'] = abs(sector_companies['PE Ratio'] - avg_selected_pe)
            recommendations = sector_companies[~sector_companies['Symbol'].isin(selected_stocks)].sort_values('PE Difference').head(5)

            st.write("### Recommended Stocks Similar to Your Past Winners:")
            st.dataframe(recommendations[['Symbol', 'Security', 'PE Ratio', 'GICS Sector']])
else:
    st.write("Please select at least one stock you've invested in.")