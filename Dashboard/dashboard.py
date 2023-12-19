import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk format currency
def format_currency(value, currency, locale):
    formatted_value = f"{currency} {value:,.2f}"
    return formatted_value

# Membaca CSV ke dalam DataFrame
all_df = pd.read_csv("all_data.csv")

# Menghitung total revenue pertahun
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])
all_df['tahun'] = all_df['order_purchase_timestamp'].dt.year
revenue_pertahun = all_df.groupby('tahun')['price'].sum().reset_index()  # Reset index untuk mendapatkan DataFrame baru

# Menghitung persentase kenaikan atau penurunan
revenue_pertahun['persentase_kenaikan'] = revenue_pertahun['price'].pct_change() * 100

 # Menampilkan hasil menggunakan Streamlit
st.header("Dashboar MUM")
st.subheader("Total Revenue Pertahun:")
# st.write(revenue_pertahun)

# st.subheader("Persentase Kenaikan atau Penurunan:")
# st.write(revenue_pertahun['persentase_kenaikan'])

# Visualisasi dengan multi barplot
fig, ax = plt.subplots(figsize=(10, 6))

revenue_pertahun.plot(kind='bar', x='tahun', y='price', ax=ax, color=['blue', 'orange'])
ax.set_ylabel('Total Revenue')
ax.set_xlabel('Tahun')
ax.set_title('Total Revenue Pertahun')
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha='right', rotation_mode='anchor')

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)


#menambahkan header pada dashboard
st.header('Collection Dashboard :sparkles:')


min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    #membuat logo 
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    #mengambil start_date & end_state dari date_input
    start_date, end_date = st.date_input(
        label='Rentang waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

#create_daily_orders_df() digunakan untuk menyimpan dayli_report_df
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df

daily_orders_df = create_daily_orders_df(main_df)

#menampilkan informasi total order dan revenue dalam bentuk metric()
#yang ditampilkan menggunakan layout columns()
#informasi tentang order harian ditampilkan dalam bentuk visualisasi data

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)


fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90cAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

# Menambahkan label dan judul agar lebih jelas
ax.set_xlabel("Tanggal Order")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("Tren Pesanan bulanan")

st.pyplot(fig)


#menampilkan 5 produk paling laris dan paling sedikit terjual melalui visualisasi data
def create_sum_order_items_df(df):
    # Mengganti 'order_id' dengan 'order_item_id' pada pengelompokan
    sum_order_items_df = df.groupby("product_category_name").order_item_id.sum().sort_values(ascending=False).reset_index()

    return sum_order_items_df

sum_order_items_df = create_sum_order_items_df(main_df)

st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Menggunakan kolom 'product_category_name' sebagai sumbu x
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of sales", fontsize=30)
ax[0].set_title("Best performing product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# Memperbaiki kolom yang digunakan untuk plotting
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst performing product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Ambil informasi waktu pengiriman
delivery_info = all_df[['customer_state', 'order_delivered_customer_date', 'order_delivered_carrier_date']]

# Konversi kolom waktu pengiriman ke format datetime
delivery_info['order_delivered_customer_date'] = pd.to_datetime(delivery_info['order_delivered_customer_date'])
delivery_info['order_delivered_carrier_date'] = pd.to_datetime(delivery_info['order_delivered_carrier_date'])

# Hitung durasi pengiriman untuk setiap pesanan per bulan
delivery_info['delivery_duration_month'] = (delivery_info['order_delivered_customer_date'] - delivery_info['order_delivered_carrier_date']).dt.days

# Extract the month and year from the delivery date
delivery_info['delivery_month'] = delivery_info['order_delivered_customer_date'].dt.month
delivery_info['delivery_year'] = delivery_info['order_delivered_customer_date'].dt.year

# Pilih dua kota tercepat dan dua kota terlama
fastest_cities = delivery_info.groupby('customer_state')['delivery_duration_month'].mean().nsmallest(2).index
slowest_cities = delivery_info.groupby('customer_state')['delivery_duration_month'].mean().nlargest(2).index

# Filter data untuk kota tercepat dan terlama
subset = delivery_info[delivery_info['customer_state'].isin(fastest_cities.union(slowest_cities))]

# Buat bar plot
fig, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x='customer_state', y='delivery_duration_month', hue='delivery_year', data=subset, palette='viridis')
plt.xlabel('customer_state', fontsize=18)
plt.ylabel('Average Delivery Duration (days)', fontsize=18)
plt.title('Average Delivery Duration for Fastest and Slowest Cities', fontsize=25)
plt.xticks(rotation=45, ha='right', fontsize=15)
plt.yticks(fontsize=15)
plt.tight_layout()

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)



def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Move this line outside of the function
rfm_df = create_rfm_df(main_df)

# Menampilkan nilai avg ketiga parameter (recency, frequency, monetary) menggunakan widget (metric)
st.subheader('Best & Worst Based on RFM Parameters')

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average recency", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale="es_CO")
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Frequency", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)
