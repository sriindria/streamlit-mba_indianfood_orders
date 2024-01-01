import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import plotly.express as px

#navigasi sidebar
with st.sidebar :
    selected = option_menu ('INDIAN FOOD',
    ['Market Basket Analysis',
    'Visualisasi Model'],
    default_index=0)

#halaman Market Basket Analysis Algoritma Apriori
if (selected == 'Market Basket Analysis'):
    header_image = "img/gambar11.jpg"  # Ganti dengan path gambar Anda
    st.image(header_image, width=700)
    st.title('Market Basket Analysis menggunakan Algoritma Apriori')
    
    #load dataset
    df = pd.read_csv("restaurant-1-orders.csv")
    
    df['Order Date'] = pd.to_datetime(df['Order Date'], format="%d/%m/%Y %H:%M")

    df["month"] = df['Order Date'].dt.month
    df["day"] = df['Order Date'].dt.weekday

    df["month"].replace([i for i in range(1, 12 + 1)], ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], inplace=True)
    df["day"].replace([i for i in range(6 + 1)], ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], inplace=True)

    def get_data(month = '', day = ''):
        data= df.copy()
        filtered = data.loc[
            (data["month"].str.contains(month.title())) &
            (data["day"].str.contains(day.title()))
        ]
        return filtered if filtered.shape[0] else "No Result!"
    
    def user_input_features():
        item = st.selectbox("Item", df["Item Name"].unique())
        month = st.select_slider("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        day = st.select_slider("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    
        return month, day, item

    month, day, item = user_input_features()

    data = get_data(month, day)

    def encode_units(x):
        if x <= 0:
            return 0
        elif x >= 1:
            return 1
    
    if type(data) != type ("No Result!"):
        item_count = data[["Order Number", "Item Name", "Quantity"]]
        item_count_pivot = item_count.pivot_table(index='Order Number', columns='Item Name', values='Quantity', aggfunc='sum').fillna(0)
        item_count_pivot = item_count_pivot.applymap(encode_units)

        support = 0.03  # Nilai minimum support
        frq_items = apriori(item_count_pivot, min_support = support, use_colnames = True)   # Menerapkan algoritma Apriori
    
        metric = "lift"
        min_threshold = 1
    
        rules = association_rules(frq_items, metric=metric, min_threshold=min_threshold)[["antecedents", "consequents", "support", "confidence", "lift"]]
        rules.sort_values('confidence', ascending=False, inplace=True)

    def parse_list(x):
        x = list(x)
        if len(x) == 1:
            return x[0]
        elif len(x) > 1:
            return ", ".join(x)
    
    def return_item_df(item_antecedents):
        data = rules[["antecedents", "consequents"]].copy()
        data["antecedents"] = data["antecedents"].apply(lambda x: ", ".join(x))
        data["consequents"] = data["consequents"].apply(lambda x: ", ".join(x))

        matching_rules = data.loc[data["antecedents"] == item_antecedents]

        if matching_rules.empty:
            # Jika tidak ada rekomendasi, pilih item terpopuler secara keseluruhan
            most_frequent_item = df["Item Name"].value_counts().index[0]
            return most_frequent_item
        else:
            return matching_rules.iloc[0, 1]

    if type(data) != type("No Result!"):
        st.markdown("Hasil Rekomendasi:")
        recommendation = return_item_df(item)

        st.success(f"Jika konsumen membeli **{item}**, maka biasanya membeli **{recommendation}** juga.")

if (selected == 'Visualisasi Model'):
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.title('Visualisasi Model Apriori')

    data = pd.read_csv("restaurant-1-orders.csv")
    def encode_units(x):
        if x <= 0:
            return 0
        elif x >= 1:
            return 1
    # Jalankan kembali proses Apriori untuk mendapatkan rules
    item_count = data[["Order Number", "Item Name", "Quantity"]]
    item_count_pivot = item_count.pivot_table(index='Order Number', columns='Item Name', values='Quantity', aggfunc='sum').fillna(0)
    item_count_pivot = item_count_pivot.applymap(encode_units)

    support = 0.03  # Nilai minimum support
    frq_items = apriori(item_count_pivot, min_support=support, use_colnames=True)
    metric = "lift"
    min_threshold = 1
    rules = association_rules(frq_items, metric=metric, min_threshold=min_threshold)[["antecedents", "consequents", "support", "confidence", "lift"]]

    # Ambil data untuk visualisasi
    support = rules["support"]
    confidence = rules["confidence"]
    lift = rules["lift"]
    
    if st.checkbox("3D Scatter Plot of Rules"):
        # Buat plot 3D
        fig = plt.figure(figsize=(28, 18))
        ax = fig.add_subplot(122, projection='3d')

        ax.scatter(support, confidence, lift, c='b', marker='o', s=40, label='Rules')

        ax.set_xlabel('Support')
        ax.set_ylabel('Confidence')
        ax.set_zlabel('Lift')

        ax.set_title('3D Scatter Plot of Rules')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper right')

        # Tampilkan plot
        st.pyplot(fig)
        

    if st.checkbox("Sunburst Chart"):
        rules['rule'] = rules['antecedents'].astype(str) + ' -> ' + rules['consequents'].astype(str)
        # Buat sunburst chart
        fig = px.sunburst(rules, path=['rule'], values='lift', 
                          title='Market Basket Analysis - Sunburst Chart',
                          color='support', color_continuous_scale='YlGnBu')

        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=40),
            )

        # Tampilkan plot
        st.plotly_chart(fig)


    if st.checkbox("Support vs. Confidence"):
        rules['antecedents'] = rules['antecedents'].apply(list)
        rules['consequents'] = rules['consequents'].apply(list)

        # Buat plot
        fig = px.scatter(rules, x="support", y="confidence", size="lift",
                         color="lift", hover_name="consequents",
                        title='Market Basket Analysis - Support vs. Confidence',
                        labels={'support': 'Support', 'confidence': 'Confidence'})
        
        fig.update_layout(
            xaxis_title='Support',
            yaxis_title='Confidence',
            coloraxis_colorbar_title='Lift',
            showlegend=True
            )
        
        # Tampilkan plot
        st.plotly_chart(fig)