import json
import random
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

st. set_page_config(layout="wide")  
# Load data
@st.cache_data
def load_data():
    # fetch JSON from API URL
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
selectedColour = st.sidebar.radio('Colour', trimmed_data['phone_colour'].unique())
trimmed_data = trimmed_data[trimmed_data['phone_colour'] == selectedColour]
selectedCapacity = st.sidebar.radio('Capacity', trimmed_data['capacity'].unique())
trimmed_data = trimmed_data[trimmed_data['capacity'] == selectedCapacity]
selectedCarrier = st.sidebar.radio('Carrier', trimmed_data['network'].unique())
trimmed_data = trimmed_data[trimmed_data['network'] == selectedCarrier]
selectedGrade = st.sidebar.radio('Grade', sorted(trimmed_data['grade'].unique()))

#Main
selectedPhone = data[(data['manufacturer'] == selectedManufacturer) & (data['phone_model'] == selectedModel) & (data['phone_colour'] == selectedColour) & (data['capacity'] == selectedCapacity) & (data['network'] == selectedCarrier) & (data['grade'] == selectedGrade)]
selectedPhone = selectedPhone.iloc[0]
st.title(''+selectedPhone.manufacturer+' '+selectedPhone.phone_model)
maincol1, maincol2 = st.columns(2)

maincol1.columns((1, 8, 1))[1].image(selectedPhone.image_url, use_column_width='auto')
isVoucherBetter = float(selectedPhone['trade-in_for_voucher'][-1]) > float(selectedPhone['trade-in_for_cash'][-1])+20


priceStyle = "font-size: 3rem; font-weight: bold; margin: -1.75rem 0rem; padding: 0;"
priceStyle2 = "font-size: 2.5rem; font-weight: 600; margin: -1.75rem 0rem; padding: 0;"
priceSubStyle = "font-size: 1rem; font-weight: normal; margin: 0; padding: 0;"
bestPriceStyle = "color: green;"
maincol2.markdown(f"<p style='{priceStyle}'>£{str(selectedPhone['price'][-1])} <span style='{priceSubStyle}'>Buying Price</p></p>", unsafe_allow_html=True)
maincol2.markdown(f"<p style='{priceStyle2 + (bestPriceStyle if isVoucherBetter else '')}'>£{str(selectedPhone['trade-in_for_voucher'][-1])} <span style='{priceSubStyle}'>Trade in for Voucher</p></p>", unsafe_allow_html=True)
maincol2.markdown(f"<p style='{priceStyle2 + (bestPriceStyle if not isVoucherBetter else '')}'>£{str(selectedPhone['trade-in_for_cash'][-1])} <span style='{priceSubStyle}'>Trade in for Cash</p></p>", unsafe_allow_html=True)


conditionEmoji = '🇦' if selectedPhone["grade"] == "A" else '🇧' if selectedPhone["grade"] == "B" else '🇨'
maincol2.markdown(f"<h3>🌈 Colour: <span style='color: {selectedPhone['main_colour'] if selectedPhone['phone_colour'] != 'Rose Gold' else 'pink'};'>{selectedPhone['phone_colour']}</span></h3>", unsafe_allow_html=True)
maincol2.subheader(f'💾 Capacity: {selectedPhone["capacity"]}')
maincol2.subheader(f'🪛 Condition: {conditionEmoji}')
maincol2.subheader(f'📶 Network: {selectedPhone["network"]}')

st.button('🔃', on_click=invalidate_cache_and_reload)
st.caption(f'Last updated: {currentTime.floor("S")}')
