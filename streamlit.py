import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

cities = ['London', 'Paris', 'New York', 'Tokyo', 'Sydney', 'Moscow', 'Beijing','Cairo', 'Rio de Janeiro', 'Mumbai','Mexico City', 'Dubai', 'Los Angeles', 'Singapore']
st.title("Погодное приложение от Нарэ")
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
            if temperature_limits[0] <= temperature <= temperature_limits[1]:
                st.success(f"Температура в {city}: {temperature}°C — Не аномальная, "f"{description}, Скорость  ветра{wind_speed} м/с")
            else:
                st.warning(f"Температура в {city}: {temperature}°C — Аномальная, "f"{description}, Скорость ветра: {wind_speed} м/с")
            plt.figure(figsize=(12, 6))
            plt.plot(season['timestamp'], season['temperature'], marker='o', label='Температура', color='blue')
            mean = data[data['season'] == season['season'].mode()[0]]['temperature'].mean()
            std = data[data['season'] == season['season'].mode()[0]]['temperature'].std()
            plt.fill_between(season['timestamp'],mean - 2 * std,mean + 2 * std, color='green', alpha=0.3, label='Доверительный интервал')
            plt.title(f'Временной ряд температуры в {city}')
            plt.xlabel("Дата")
            plt.ylabel("Температура (°C)")
            plt.xticks(rotation=45)
            plt.legend()
            st.pyplot(plt)
            season_avgs = data.groupby('season')['temperature'].mean().reset_index()
            plt.figure(figsize=(8, 8))
            plt.pie(season_avgs['temperature'], labels=season_avgs['season'], autopct='%1.1f%%', colors=sns.color_palette('Set2'))
            plt.title(f'Средняя температура по сезонам для {city}')
            st.pyplot(plt)
        else:
            st.error('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')
