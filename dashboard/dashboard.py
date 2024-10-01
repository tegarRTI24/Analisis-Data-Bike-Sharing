import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt

sns.set(style='dark')

# Definisi fungsi untuk memproses data
def get_total_count_by_hour_df(hour_df):
  hour_count_df =  hour_df.groupby(by="hours").agg({"count_cr": ["sum"]})
  return hour_count_df

def count_by_day_df(day_df):
    day_df_count_2011 = day_df.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_df_count_2011

def total_registered_df(day_df):
   reg_df =  day_df.groupby(by="dteday").agg({
      "registered": "sum"
    })
   reg_df = reg_df.reset_index()
   reg_df.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
   return reg_df

def total_casual_df(day_df):
   cas_df =  day_df.groupby(by="dteday").agg({
      "casual": ["sum"]
    })
   cas_df = cas_df.reset_index()
   cas_df.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
   return cas_df

def sum_order (hour_df):
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def macem_season (day_df): 
    season_df = day_df.groupby(by="season").count_cr.sum().reset_index() 
    return season_df

# Membaca file CSV
days_df = pd.read_csv("dashboard/day_clean.csv")
hours_df = pd.read_csv("dashboard/hour_clean.csv")

# Preprocessing tanggal
datetime_columns = ["dteday"]
days_df.sort_values(by="dteday", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="dteday", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

min_date_hour = hours_df["dteday"].min()
max_date_hour = hours_df["dteday"].max()

# Sidebar
with st.sidebar:
    st.image("https://storage.googleapis.com/gweb-uniblog-publish-prod/original_images/image1_hH9B4gs.jpg")
    
    # Rentang tanggal
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
    
    # Menampilkan metrik di sidebar
    st.metric("Total Sharing Bike", value="3,289,950")
    st.metric("Total Registered", value="2,672,662")
    st.metric("Total Casual", value="620,017")

main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

hour_count_df = get_total_count_by_hour_df(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_hour)

# Header
st.header('Bike Sharing 🚴')

# Visualisasi performa penjualan
st.subheader("Performa penjualan perusahaan dalam beberapa tahun terakhir")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    days_df["dteday"],
    days_df["count_cr"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Korelasi antara variabel numerik
st.subheader("Pertanyaan 1: Apa faktor-faktor utama yang mempengaruhi jumlah peminjaman sepeda harian?")
numeric_cols = ['temp', 'atemp', 'humidity', 'wind_speed', 'holiday', 'count_cr']
correlation = days_df[numeric_cols].corr()
st.write(correlation)

plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title("Korelasi antara Variabel Numerik dan Jumlah Peminjaman Sepeda")
st.pyplot(plt)

# Pola penggunaan sepeda sepanjang hari
st.subheader("Pertanyaan 2: Bagaimana pola penggunaan sepeda berubah sepanjang hari?")
hourly_counts = hours_df.groupby('hours')['count_cr'].sum().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x='hours', y='count_cr', data=hourly_counts, marker='o')
plt.title('Jumlah Peminjaman Sepeda Sepanjang Hari')
plt.xlabel('Jam')
plt.ylabel('Jumlah Peminjaman')
plt.xticks(range(24))
plt.grid()
st.pyplot(plt)

# Jumlah peminjaman sepeda berdasarkan musim
st.subheader("Pertanyaan 3: Apakah musim tertentu mempengaruhi permintaan peminjaman sepeda?")
season_counts = days_df.groupby('season', observed=False)['count_cr'].sum().reset_index()

plt.figure(figsize=(8, 5))
sns.barplot(x='season', y='count_cr', data=season_counts, palette='viridis', hue='season', dodge=False)
plt.title('Jumlah Peminjaman Sepeda Berdasarkan Musim')
plt.xlabel('Musim')
plt.ylabel('Jumlah Peminjaman')
plt.xticks(rotation=45)
plt.legend(title="Musim")
plt.tight_layout()
st.pyplot(plt)

# Jumlah peminjaman sepeda berdasarkan cuaca
st.subheader("Pertanyaan 4: Bagaimana cuaca mempengaruhi jumlah peminjaman sepeda?")
weather_counts = days_df.groupby('weather_situation', observed=False)['count_cr'].sum().reset_index()
weather_counts = weather_counts.sort_values(by='count_cr', ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(x='weather_situation', y='count_cr', data=weather_counts)
plt.title("Jumlah Peminjaman Sepeda Berdasarkan Cuaca")
plt.xlabel("Kategori Cuaca")
plt.ylabel("Jumlah Peminjaman")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

# Tren Peminjaman Sepeda per Bulan
st.subheader("Pertanyaan 5: Apakah ada tren peningkatan atau penurunan penggunaan sepeda dari waktu ke waktu?")
monthly_counts = days_df.groupby(days_df['dteday'].dt.to_period('M'))['count_cr'].sum().reset_index()
monthly_counts['dteday'] = monthly_counts['dteday'].dt.to_timestamp()

plt.figure(figsize=(12, 6))
sns.lineplot(x='dteday', y='count_cr', data=monthly_counts, marker='o')
plt.title("Tren Peminjaman Sepeda per Bulan")
plt.xlabel("Tanggal")
plt.ylabel("Jumlah Peminjaman")
plt.xticks(rotation=45)
plt.grid()
st.pyplot(plt)

# Fungsi untuk mendapatkan RFM
def calculate_rfm(df):
    # Menggunakan tanggal peminjaman terakhir
    snapshot_date = df['dteday'].max() + dt.timedelta(days=1)  # Tanggal peminjaman terakhir + 1
    # Menghitung RFM secara agregat
    rfm = df.agg({
        'dteday': lambda x: (snapshot_date - x.max()).days,
        'count_cr': 'sum',  # Menghitung total peminjaman
    }).rename(index={'dteday': 'Recency', 'count_cr': 'Monetary'})

    # Menghitung frekuensi
    frequency = df['count_cr'].count()  # Menghitung total peminjaman
    rfm['Frequency'] = frequency
    return rfm

# Fungsi manual grouping
def manual_grouping(value, bins, labels):
    for i in range(len(bins) - 1):
        if bins[i] < value <= bins[i + 1]:
            return labels[i]
    return labels[-1]

# Fungsi binning
def binning(data, bins, labels, col_name):
    data[col_name + '_binned'] = pd.cut(data[col_name], bins=bins, labels=labels, include_lowest=True)
    return data

# Load data
days_df = pd.read_csv("dashboard/day_clean.csv")
days_df['dteday'] = pd.to_datetime(days_df['dteday'])

# Mengelompokkan data
casual_bins = [0, 1000, 5000, 10000, 20000]
registered_bins = [0, 1000, 5000, 10000, 20000]
data = days_df[['casual', 'registered', 'count_cr']].copy()

# Manual grouping
data['casual_group'] = data['casual'].apply(manual_grouping, args=(casual_bins, ["Very Low", "Low", "Medium", "High"]))
data['registered_group'] = data['registered'].apply(manual_grouping, args=(registered_bins, ["Very Low", "Low", "Medium", "High"]))

# Binning
data = binning(data, casual_bins, ["Very Low", "Low", "Medium", "High"], 'casual')
data = binning(data, registered_bins, ["Very Low", "Low", "Medium", "High"], 'registered')

# Filter dataframe berdasarkan rentang tanggal
filtered_days_df = days_df[(days_df["dteday"] >= pd.to_datetime(start_date)) & (days_df["dteday"] <= pd.to_datetime(end_date))]

# RFM Calculation
rfm_result = calculate_rfm(filtered_days_df)

# Hasil RFM
st.header("RFM Analysis")
st.write("Recency: ", rfm_result['Recency'])
st.write("Frequency: ", rfm_result['Frequency'])
st.write("Monetary: ", rfm_result['Monetary'])

# Manual Grouping Visualisasi
st.header("Manual Grouping of Bike Rentals")
binned_data_manual = data.groupby(['casual_group', 'registered_group']).agg({'count_cr': 'sum'}).reset_index()
st.write(binned_data_manual)

# Scatter plot manual grouping
plt.figure(figsize=(12, 8))
sns.scatterplot(x='casual', y='registered', hue='casual_group', style='registered_group', data=data, palette='Set1')
plt.title('Manual Grouping of Bike Rentals')
plt.xlabel('Casual Rentals')
plt.ylabel('Registered Rentals')
plt.legend(title='Casual and Registered Groups')
st.pyplot(plt)

# Binning Clustering Visualisasi
st.header("Binning Clustering of Bike Rentals")
binned_data = data.groupby(['casual_binned', 'registered_binned'], observed=True).agg({'count_cr': 'sum'}).reset_index()
st.write(binned_data)

# Scatter plot binning
plt.figure(figsize=(12, 8))
sns.scatterplot(x='casual', y='registered', hue='casual_binned', style='registered_binned', data=data, palette='Set1')
plt.title('Binning Clustering of Bike Rentals')
plt.xlabel('Casual Rentals')
plt.ylabel('Registered Rentals')
plt.legend(title='Casual and Registered Bins')
st.pyplot(plt)

st.write("Created by: Ramadhan Tegar Imansyah")