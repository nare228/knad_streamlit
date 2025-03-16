import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

cities = ['London', 'Paris', 'New York', 'Tokyo', 'Sydney', 'Moscow', 'Beijing','Cairo', 'Rio de Janeiro', 'Mumbai','Mexico City', 'Dubai', 'Los Angeles', 'Singapore']
st.title("Streamlit Нарэ")
city = st.selectbox("Выберите город", cities)
with st.form('api'):
    api = st.text_input('Введите API-ключ')
    submit = st.form_submit_button('Отправить')
st.text("Загрузите Csv")
download = st.file_uploader("Выберите файл", type=['csv'])
data = None
if download is not None:
    data = pd.read_csv(download)
    st.dataframe(data)
if data is not None and api:
    if st.button('Показать погоду'):
        request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}&units=metric")
        if request.status_code == 200:
            request = request.json()
            temperature = request['main']['temp']
            wind_speed = request['wind']['speed']
            description = request['weather'][0]['description']
            season = data[data['city'] == city]
            average = data[data['season'] == season['season'].mode()[0]]['temperature'].mean()
            seasonal_std = data[data['season'] == season['season'].mode()[0]]['temperature'].std()
            temperature_limits = (average - 2 * seasonal_std, average + 2 * seasonal_std)
            season['anomaly'] = ~season['temperature'].between(temperature_limits[0], temperature_limits[1])
            plt.figure(figsize=(12, 6))
            plt.plot(season['timestamp'], season['temperature'], marker='o', label='Температура', color='blue')
            plt.scatter(season[season['anomaly']]['timestamp'],season[season['anomaly']]['temperature'], color='red', marker='o', label='Аномальные значения')
            plt.axhline(y=temperature_limits[0], color='green', linestyle='--', label='Нижний предел')
            plt.axhline(y=temperature_limits[1], color='orange', linestyle='--', label='Верхний предел')
            plt.title(f'Временной ряд температуры в {city} с аномалиями')
            plt.xlabel("Дата")
            plt.ylabel("Температура (°C)")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()  # Обеспечивает лучшее размещение графика
            st.pyplot(plt)
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=data, x='season', y='temperature', estimator='mean', marker='o', palette='Set2')
            plt.title(f'Cредняя температура по сезонам для {city}')
            plt.xlabel('Сезон')
            plt.ylabel('Средняя температура (°C)')
            plt.grid()
            st.pyplot(plt)
        else:
            st.error('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')
