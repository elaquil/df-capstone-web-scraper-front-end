import json
import random
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import requests

st. set_page_config(layout="wide")  
# Load data
@st.cache_data
def load_data():
    url = "https://buw5pcb475.execute-api.us-east-1.amazonaws.com/production/phones"
    response = requests.get(url)
    data = response.json()["phones"]

    df = pd.DataFrame(data)
    currentTime = pd.Timestamp.now()
    return [df, currentTime]

def invalidate_cache_and_reload():
    load_data.clear()
    load_data()

data = load_data()[0]
currentTime = load_data()[1]

# Sidebar
st.sidebar.header('Phone Selection')
selectedManufacturer = st.sidebar.selectbox('Manufacturer', data['manufacturer'].unique())
trimmed_data = data[data['manufacturer'] == selectedManufacturer]
selectedModel = st.sidebar.selectbox('Model', trimmed_data['phone_model'].unique())
trimmed_data = trimmed_data[trimmed_data['phone_model'] == selectedModel]
selectedColour = st.sidebar.radio('Colour', sorted(trimmed_data['phone_colour'].unique()))
trimmed_data = trimmed_data[trimmed_data['phone_colour'] == selectedColour]
selectedCapacity = st.sidebar.radio('Capacity', sorted(trimmed_data['capacity'].unique()))
trimmed_data = trimmed_data[trimmed_data['capacity'] == selectedCapacity]
selectedCarrier = st.sidebar.radio('Carrier', np.flip(trimmed_data['network'].unique()))
trimmed_data = trimmed_data[trimmed_data['network'] == selectedCarrier]
selectedGrade = st.sidebar.radio('Grade', sorted(trimmed_data['grade'].unique()))

#Main
selectedPhone = data[(data['manufacturer'] == selectedManufacturer) & (data['phone_model'] == selectedModel) & (data['phone_colour'] == selectedColour) & (data['capacity'] == selectedCapacity) & (data['network'] == selectedCarrier) & (data['grade'] == selectedGrade)]
selectedPhone = selectedPhone.iloc[0]

#change all values inside of list for price, trade-in_for_voucher, trade-in_for_cash to float
selectedPhone['price'] = [float(x) for x in selectedPhone['price']]
selectedPhone['trade-in_for_voucher'] = [float(x) for x in selectedPhone['trade-in_for_voucher']]
selectedPhone['trade-in_for_cash'] = [float(x) for x in selectedPhone['trade-in_for_cash']]

st.title(''+selectedPhone.manufacturer+' '+selectedPhone.phone_model)
maincol1, maincol2 = st.columns(2)

maincol1.columns((1, 8, 1))[1].image(selectedPhone.image_url, use_column_width='auto')
isVoucherBetter = float(selectedPhone['trade-in_for_voucher'][-1]) > float(selectedPhone['trade-in_for_cash'][-1])+20

hasHistoricalData = len(selectedPhone.price) > 1

if hasHistoricalData:
    priceFluctuation = f'▲ {selectedPhone.price[-1] - selectedPhone.price[-2]}' if selectedPhone.price[-1] > selectedPhone.price[-2] else f'▼ {selectedPhone.price[-2] - selectedPhone.price[-1]}' if selectedPhone.price[-1] < selectedPhone.price[-2] else '- 0.00'
    voucherFluctuation = f'▲ {selectedPhone["trade-in_for_voucher"][-1] - selectedPhone["trade-in_for_voucher"][-2]}' if selectedPhone["trade-in_for_voucher"][-1] > selectedPhone["trade-in_for_voucher"][-2] else f'▼ {selectedPhone["trade-in_for_voucher"][-2] - selectedPhone["trade-in_for_voucher"][-1]}' if selectedPhone["trade-in_for_voucher"][-1] < selectedPhone["trade-in_for_voucher"][-2] else '- 0.00'
    cashFluctuation = f'▲ {selectedPhone["trade-in_for_cash"][-1] - selectedPhone["trade-in_for_cash"][-2]}' if selectedPhone["trade-in_for_cash"][-1] > selectedPhone["trade-in_for_cash"][-2] else f'▼ {selectedPhone["trade-in_for_cash"][-2] - selectedPhone["trade-in_for_cash"][-1]}' if selectedPhone["trade-in_for_cash"][-1] < selectedPhone["trade-in_for_cash"][-2] else '- 0.00'

priceStyle = "font-size: 3rem; font-weight: bold; margin: -1.75rem 0rem; padding: 0;"
priceStyle2 = "font-size: 2.5rem; font-weight: 600; margin: -1.75rem 0rem; padding: 0;"
priceSubStyle = "font-size: 1rem; font-weight: normal; margin: 0; padding: 0;"
bestPriceStyle = "color: green;"
valueUpStyle = "color: green; font-weight: bold; margin: -1.25rem 0rem; padding: 0;"
valueDownStyle = "color: red; font-weight: bold; margin: -1.25rem 0rem; padding: 0;"
valueNeutralStyle = "color: grey; font-weight: bold; margin: -1.25rem 0rem; padding: 0;"

maincol2.markdown(f"<p style='{priceStyle}'>£{str(selectedPhone['price'][-1])} <span style='{priceSubStyle}'>Buying Price</p></p>", unsafe_allow_html=True)
if hasHistoricalData: maincol2.markdown(f"<p style='{(valueUpStyle if priceFluctuation[0] == '▲' else valueDownStyle if priceFluctuation[0] == '▼' else valueNeutralStyle)}'>{priceFluctuation}</p>", unsafe_allow_html=True)
maincol2.markdown(f"<p style='{priceStyle2 + (bestPriceStyle if isVoucherBetter else '')}'>£{str(selectedPhone['trade-in_for_voucher'][-1])} <span style='{priceSubStyle}'>Trade in for Voucher</p></p>", unsafe_allow_html=True)
if hasHistoricalData: maincol2.markdown(f"<p style='{(valueUpStyle if voucherFluctuation[0] == '▲' else valueDownStyle if voucherFluctuation[0] == '▼' else valueNeutralStyle)}'>{voucherFluctuation}</p>", unsafe_allow_html=True)
maincol2.markdown(f"<p style='{priceStyle2 + (bestPriceStyle if not isVoucherBetter else '')}'>£{str(selectedPhone['trade-in_for_cash'][-1])} <span style='{priceSubStyle}'>Trade in for Cash</p></p>", unsafe_allow_html=True)
if hasHistoricalData: maincol2.markdown(f"<p style='{(valueUpStyle if cashFluctuation[0] == '▲' else valueDownStyle if cashFluctuation[0] == '▼' else valueNeutralStyle)}'>{cashFluctuation}</p>", unsafe_allow_html=True)


conditionEmoji = '🇦' if selectedPhone["grade"] == "A" else '🇧' if selectedPhone["grade"] == "B" else '🇨'
maincol2.markdown(f"<h3>🌈 Colour: <span style='color: {selectedPhone['main_colour'] if selectedPhone['phone_colour'] != 'Rose Gold' else 'pink'};'>{selectedPhone['phone_colour']}</span></h3>", unsafe_allow_html=True)
maincol2.subheader(f'💾 Capacity: {selectedPhone["capacity"]}')
maincol2.subheader(f'🪛 Condition: {conditionEmoji}')
maincol2.subheader(f'📶 Network: {selectedPhone["network"]}')

st.button('🔃', on_click=invalidate_cache_and_reload)
st.caption(f'Last updated: {currentTime.floor("s")}')

if hasHistoricalData:
    st.subheader('Price History')
    chart = st.empty()
    graphControlscol1, graphControlscol2 = st.columns(2)
    priceType = graphControlscol1.radio('Price Type', ['Buying Price', 'Trade in for Voucher', 'Trade in for Cash'])
    extraphones = graphControlscol2.multiselect('Compare with other phones', data['phoneid'].unique())
    price_data = selectedPhone['price'] if priceType == 'Buying Price' else selectedPhone['trade-in_for_voucher'] if priceType == 'Trade in for Voucher' else selectedPhone['trade-in_for_cash']
    time_data = pd.to_datetime(selectedPhone['time'], format='%Y-%m-%d-%H-%M-%S').date
    historical_data_df = pd.DataFrame({'Date': time_data, 
                        f'{selectedPhone["phone_model"]}, {selectedPhone["main_colour"]}, {selectedPhone["capacity"]}, {selectedPhone["grade"]}, {selectedPhone["network"]}': price_data, })
    if extraphones:
        extraPhonesDf = pd.DataFrame()
        for phone in extraphones:
            phoneData = data[data['phoneid'] == phone].iloc[0]
            phoneData['price'] = [float(x) for x in phoneData['price']]
            phoneData['trade-in_for_voucher'] = [float(x) for x in phoneData['trade-in_for_voucher']]
            phoneData['trade-in_for_cash'] = [float(x) for x in phoneData['trade-in_for_cash']]
            price_data = phoneData['price'] if priceType == 'Buying Price' else phoneData['trade-in_for_voucher'] if priceType == 'Trade in for Voucher' else phoneData['trade-in_for_cash']
            time_data = pd.to_datetime(phoneData['time'], format='%Y-%m-%d-%H-%M-%S').date
            temp = pd.DataFrame({f'{phoneData["phone_model"]}, {phoneData["main_colour"]}, {phoneData["capacity"]}, {phoneData["grade"]}, {phoneData["network"]}': price_data, 
                                    'Date': time_data})
            historical_data_df = historical_data_df.merge(temp, on='Date', how='outer')
    chart.line_chart(historical_data_df, x='Date',)
    with st.expander('Raw Price History Data'):
        st.write(historical_data_df)
    with st.expander('Debug data'):
        st.write(selectedPhone)