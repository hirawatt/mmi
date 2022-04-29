import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta, date

import plotly.graph_objects as go

# Custom imports
import nsepyData as nd

#nseData = nd.get_index_data("INDIAVIX")
#st.write(nseData.head())
nifty50 = pd.read_csv('data/nifty50.csv', index_col='Date', parse_dates=['Date'])


# FII Derivative Stats
#oi_data_link = "https://www1.nseindia.com/content/fo/fii_stats_27-Apr-2022.xls"
#fii_data = pd.read_excel(oi_data_link)
#st.write(fii_data)

# FII Data
def get_fii_activity(data_dates):
    oi_data_link = "https://www1.nseindia.com/content/fo/fii_stats_{}-{}-{}.xls"
    #data = pd.read_csv('data/nifty50.csv', index_col='Date', parse_dates=['Date'])
    for i in data_dates.index:
        filename = 'data/fii/fii_stats_{}-{}-{}.csv'.format(i.strftime("%d"), i.strftime("%b"), i.year)
        #st.write(i, filename)
        if os.path.isfile(filename) == False:
            #st.write(oi_data_link.format(i.strftime("%d"), i.strftime("%b"), i.year))
            fii_data = pd.read_excel(oi_data_link.format(i.strftime("%d"), i.strftime("%b"), i.year))
            fii_data.to_csv(filename)
        else:
            pass

# Market Activity Data
def get_market_activity(data_dates):
    ma_link = "https://archives.nseindia.com/archives/equities/mkt/MA{}{}{}.csv"
    for i in data_dates.index:
        filename = 'data/mactivity/MA{}{}{}.csv'.format(i.strftime("%d"), i.strftime("%m"), i.strftime("%y"))
        st.write(i, filename)
        if os.path.isfile(filename) == False:
            st.write(ma_link.format(i.strftime("%d"), i.strftime("%m"), i.strftime("%y")))
            ma_data = pd.read_csv(ma_link.format(i.strftime("%d"), i.strftime("%m"), i.strftime("%y")), skiprows=8)
            ma_data.to_csv(filename)
        else:
            pass

#get_market_activity(nifty50)

# Market Activity Data Processing
#@st.cache(suppress_st_warning=True)
def market_activity(data_dates):
    ma_adv_list = []
    ma_dec_list = []
    for i in data_dates.index:
        filename = 'data/mactivity/MA{}{}{}.csv'.format(i.strftime("%d"), i.strftime("%m"), i.strftime("%y"))
        ma_data = pd.read_csv(filename)
        #st.write(filename, ma_data)
        ma_adv = ma_data['PREVIOUS CLOSE'].loc[ma_data['INDEX'] == 'ADVANCES']
        ma_dec = ma_data['PREVIOUS CLOSE'].loc[ma_data['INDEX'] == 'DECLINES']
        #ma_adv = ma_data.loc[ma_data['INDEX'] == 'ADVANCES']
        #ma_dec = ma_data.loc[ma_data['INDEX'] == 'DECLINES']
        ma_adv_list.append(ma_adv.values[0])
        ma_dec_list.append(ma_dec.values[0])
    ma_df = pd.DataFrame({'ADVANCES': ma_adv_list,
        'DECLINES': ma_dec_list
    }, index=data_dates.index)
    st.write(ma_df)
    return ma_df

market_activity(nifty50)
ma_data = pd.read_csv('data/mactivity/MA030122.csv')
ma_adv = ma_data['PREVIOUS CLOSE'].loc[ma_data['INDEX'] == 'ADVANCES']
ma_dec = ma_data['PREVIOUS CLOSE'].loc[ma_data['INDEX'] == 'DECLINES']
ma_adv_list = []
ma_dec_list = []
ma_adv_list.append(ma_adv.values[0])
#st.write(ma_adv_list)

@st.cache()
def fii_activity(data_dates):
    fii_oi_list = []
    for i in data_dates.index:
        filename = 'data/fii/fii_stats_{}-{}-{}.csv'.format(i.strftime("%d"), i.strftime("%b"), i.year)
        fii_oi = pd.read_csv(filename)
        fii_oi_list.append([fii_oi.iat[2, 3], fii_oi.iat[2, 5]]) # 3rd row, 4th column -> Index Futures -> Amt. in Crores -> [BUY, SELL]
    fii_activity_data = pd.DataFrame(columns=['BUY', 'SELL'], data= fii_oi_list, index=data_dates.index)
    convert_dict = {'BUY': float,
                    'SELL': float
    }
    fii_activity_data = fii_activity_data.astype(convert_dict)
    fii_activity_data['FII Activity'] = fii_activity_data.BUY - fii_activity_data.SELL 
    fii_activity_data.to_csv('data/fii_activity.csv')

# Data Analysis and Visualization
def methodology(df):
    #st.write(df.iloc[:, -1])
    df['Rolling Mean'] = df.iloc[:, -1].rolling(45).mean()
    df['Compare'] = df.iloc[:, -2] - df.iloc[:, -1]
    df['Rolling StdDev'] = df.iloc[:, -3].rolling(45).std()
    # Normalizing Data between 0 to 100
    df['Normalized'] = 100 * ((df['Rolling StdDev'] - df['Rolling StdDev'].min()) / (df['Rolling StdDev'].max() - df['Rolling StdDev'].min()))
    #st.write(df['Normalized'].tail())
    return df['Normalized']

# Run this function to get data
#get_fii_activity(nifty50)

# Run this function to parse the data
#fii_activity(nifty50)

# FII Activity
fii_activity = pd.read_csv('data/fii_activity.csv', index_col='Date', parse_dates=['Date'])
#st.line_chart(fii_activity)
mmi_fii = methodology(fii_activity)
#st.line_chart(mmi_fii.tail())

# Volatility and Skew
indiavix = pd.read_csv('data/indiavix.csv', index_col='Date', parse_dates=['Date'])
indiavix['Rolling'] = indiavix['Close'].rolling(45).mean()
#st.write(indiavix['Rolling'].tail())
mmi_volatility = methodology(indiavix)
#st.write(mmi_volatility.tail())

# Momentum
# 30D & 90D EMA of Nifty 50
nifty50['30D EMA'] = nifty50['Close'].ewm(span=30, adjust=False).mean()
nifty50['90D EMA'] = nifty50['Close'].ewm(span=90, adjust=False).mean()
nifty50['Momentum'] = (nifty50['90D EMA'] - nifty50['30D EMA']) / nifty50['90D EMA']
#st.write('MMI Momentum', nifty50['Momentum'])
#st.line_chart(nifty50.iloc[:, [3, -3, -2]])
mmi_momentum = methodology(nifty50)
#st.line_chart(mmi_momentum.tail())

# Market Breadth -> Modifies Arms Index
#adratio = pd.read_html('https://www1.nseindia.com/products/content/equities/equities/historical_advdeclines.htm')
#adratio = pd.read_html('https://www1.nseindia.com/products/content/equities/equities/eq_advdecmar2022.htm')[0]
#st.write(adratio)

# Price Strength


# Demand for Gold

# MMI Calculation
mmi = 1/3*(mmi_fii + mmi_momentum)
st.write('MMI Data', mmi.tail())

# Vizualization
# Gauge Charts -> https://plotly.com/python/reference/indicator/
fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    delta = {'reference': mmi[-2]},
    value = mmi[-1],
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Risk-o-Meter"},
    gauge = {'axis': {'range': [None, 100],
                    'tickmode': 'array',
                    'ticktext': ['Extreme Fear', 'Fear', '', 'Greed', 'Extreme Greed'],
                    'tickvals': [0, 30, 50, 70, 100]},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen", 'name': 'Fear'},
                {'range': [30, 50], 'color': "rgb(255,200,0)", 'name': 'Risk'},
                {'range': [50, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "red"}]}))

st.plotly_chart(fig, use_container_width=True)

st.write(mmi_fii.tail(), mmi_momentum.tail(), mmi_volatility.tail())

def get_dates():
    # Holiday List From NSE
    holidayTable = pd.read_csv('data/holiday2022.csv')
    holiday = holidayTable['Date'].tolist()
    holidayDataframe = pd.to_datetime(holiday, format='%d-%b-%Y')
    #st.write("2022 Holiday List", holidayDataframe)

    # Create dates dataframe with frequency
    #timedelta(days=45)
    today = datetime.now()
    bDates = pd.date_range(end=today.date(), periods = 45, freq ='B') # B = business days
    bDate = bDates.date
    #st.write(bDates, bDate)

if __name__ == '__main__':
    # Start Here
    a = 10