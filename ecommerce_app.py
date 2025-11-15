import streamlit as st
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import io

# SQL Server connection
conn_str = (
    "Driver={SQL Server};"
    "Server=SABAHOME\\SQLEXPRESS;"
    "Database=Ecommerce;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Load data from correct schema
@st.cache_data
def load_data():
    query = "SELECT * FROM Ecommerce.ImportExport_Countries"
    return pd.read_sql(query, conn)

# Insert new record
def insert_record(row):
    placeholders = ', '.join(['?'] * len(row))
    query = f"INSERT INTO Ecommerce.ImportExport_Countries VALUES ({placeholders})"
    cursor.execute(query, tuple(row))
    conn.commit()

# Delete record by index
def delete_record(index):
    df = load_data()
    if index < len(df):
        pk_query = f"DELETE FROM Ecommerce.ImportExport_Countries WHERE ID = ?"
        pk_value = df.loc[index, "ID"]
        cursor.execute(pk_query, pk_value)
        conn.commit()

# App layout
st.set_page_config(page_title="ImportExport Dashboard", layout="wide")
st.title("📦 ImportExport Countries Dashboard (Multilingual 🇺🇸 / 🇱🇰)")

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Records")
years = sorted(df["Year"].dropna().unique()) if "Year" in df.columns else []
products = sorted(df["Product"].dropna().unique()) if "Product" in df.columns else []
countries = sorted(df["Country_ID"].dropna().unique()) if "Country_ID" in df.columns else []
directions = sorted(df["Import_Export"].dropna().unique()) if "Import_Export" in df.columns else []
languages = sorted(df["Language"].dropna().unique()) if "Language" in df.columns else []

selected_year = st.sidebar.selectbox("Year", ["All"] + [str(y) for y in years])
selected_country = st.sidebar.selectbox("Country ID", ["All"] + list(map(str, countries)))
selected_product = st.sidebar.selectbox("Product", ["All"] + products)
selected_direction = st.sidebar.selectbox("Import/Export", ["All"] + directions)
selected_language = st.sidebar.selectbox("Language", ["All"] + languages)

filtered_df = df.copy()
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["Year"] == int(selected_year)]
if selected_country != "All":
    filtered_df = filtered_df[filtered_df["Country_ID"] == int(selected_country)]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["Product"] == selected_product]
if selected_direction != "All":
    filtered_df = filtered_df[filtered_df["Import_Export"] == selected_direction]
if selected_language != "All":
    filtered_df = filtered_df[filtered_df["Language"] == selected_language]

# Editable grid
st.subheader("📝 Edit Records")
edited_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

# Add new record
st.subheader("➕ Add New Record")
with st.form("add_record"):
    new_row = [st.text_input(col) for col in df.columns if col != "ID"]
    if st.form_submit_button("Add"):
        insert_record(new_row)
        st.success("Record added!")

# Delete record
st.subheader("🗑️ Delete Record")
delete_index = st.number_input("Enter row index to delete", min_value=0, max_value=len(df)-1, step=1)
if st.button("Delete"):
    delete_record(delete_index)
    st.success(f"Deleted row {delete_index}")

# Export filtered data
st.sidebar.header("📥 Export Filtered Data")
export_format = st.sidebar.selectbox("Format", ["CSV", "Excel"])
if st.sidebar.button("Download"):
    if export_format == "CSV":
        st.sidebar.download_button("Download CSV", filtered_df.to_csv(index=False), file_name="filtered_import_export.csv")
    else:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            filtered_df.to_excel(writer, index=False, sheet_name="Filtered")
        st.sidebar.download_button("Download Excel", buffer.getvalue(), file_name="filtered_import_export.xlsx")

# Visualizations
st.subheader("📊 Visual Insights")

# Bar Chart: Total transaction value by year
if "Year" in filtered_df.columns and "Total_Transaction_Value_USD" in filtered_df.columns:
    st.markdown("**💰 Total Transaction Value by Year**")
    bar_data = filtered_df.groupby("Year")["Total_Transaction_Value_USD"].sum()
    fig1, ax1 = plt.subplots()
    bar_data.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel("USD")
    st.pyplot(fig1)

# Pie Chart: Product category distribution
if "Product" in filtered_df.columns:
    st.markdown("**📦 Product Category Distribution**")
    pie_data = filtered_df["Product"].value_counts()
    fig2, ax2 = plt.subplots()
    pie_data.plot(kind='pie', autopct='%1.1f%%', ax=ax2)
    ax2.set_ylabel("")
    st.pyplot(fig2)

# Line Chart: Market growth percent over time
if "Year" in filtered_df.columns and "Market_Growth_Percent" in filtered_df.columns:
    st.markdown("**📈 Market Growth Over Time**")
    line_data = filtered_df.groupby("Year")["Market_Growth_Percent"].mean()
    fig3, ax3 = plt.subplots()
    line_data.plot(kind='line', marker='o', ax=ax3, color='green')
    ax3.set_ylabel("Growth (%)")
    st.pyplot(fig3)

# HS Code Summary Table
if "HS_Code" in filtered_df.columns:
    st.markdown("**📋 HS Code Usage Summary**")
    hs_summary = filtered_df["HS_Code"].value_counts().reset_index()
    hs_summary.columns = ["HS Code", "Frequency"]
    st.dataframe(hs_summary, use_container_width=True)