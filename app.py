import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import xlsxwriter
st.set_option('deprecation.showPyplotGlobalUse', False)




month_mapping = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

# Define a list of month names
month_names = list(month_mapping.keys())


def upload_file():
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["xls"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, parse_dates=['Date'], header=9)
        data = data.drop(columns=['Account', 'Volume', 'Balance '], axis=0)
        data = data.rename(columns={'Unnamed: 9': 'Account', 'Unnamed: 14': 'Volume', 'Unnamed: 16': 'Balance'})

        data = process_data(data)
        return data


def process_data(data):
    # Keep only the required columns
    columns_to_keep = ['Date', 'Trans #', 'Description', 'Account', 'Volume']
    data = data[columns_to_keep]

    # Rename columns
    data = data.rename(columns={'Trans #': 'Trans', 'Account': 'Account'})
    data = data.dropna()
    data['Date'] = pd.to_datetime(data['Date'])

    # Convert Account column to strings
    data['Account'] = data['Account'].astype(str)

    # Split Account column into Gantry and OMC columns
    data['Gantry'] = data['Account'].apply(lambda x: ('TAKORADI' if 'TAKORADI' in x else x.split('-')[-1].strip()))
    data['OMC'] = data['Account'].apply(lambda x: x.replace(' at TAKORADI BLUE OCEAN INVESTMENT LIMITED', '').strip().split(' at ')[0].strip().replace('at BOST', ''))

    # Filter rows where Description contains "Sale"
    data = data[data['Description'].str.contains('Sale', case=False)]

    return data





def display_OMC(data, selected_month, selected_window):
    if data is None:
        st.warning('Please upload a file first.')
        return

    if 'OMC' not in data.columns:
        st.warning("Selected sheet does not contain 'OMC' column.")
        return

    st.subheader("OIL MARKETING COMPANIES")

    OMC = data['OMC'].unique()
    selected_omc = st.selectbox("Select an OMC", OMC)
    filtered_data = data[data['OMC'] == selected_omc]

    filtered_data = filtered_data[filtered_data['Date'].dt.month == selected_month]

    volume_sum = filtered_data['Volume'].sum()
    st.write(f"Total sales made to {selected_omc} in {selected_month}: {volume_sum:,}")

    if selected_window == "Window 1":
        filtered_data = filtered_data[filtered_data['Date'].dt.day <= 15]
    elif selected_window == "Window 2":
        filtered_data = filtered_data[filtered_data['Date'].dt.day > 15]

    volume_sum = filtered_data['Volume'].sum()
    st.write(f"Total sales made to {selected_omc} in {selected_month}, {selected_window}: {volume_sum:,}")


def display_gantry(data, selected_month, selected_window):
    if data is None:
        st.warning('Please upload a file first.')
        return

    if 'Gantry' not in data.columns:
        st.warning("Selected sheet does not contain 'Gantry' column.")
        return

    st.subheader("GANTRY")

    gantries = data['Gantry'].unique()
    selected_gantry = st.selectbox("Select a Gantry", gantries)
    filtered_data = data[data['Gantry'] == selected_gantry]

    filtered_data = filtered_data[filtered_data['Date'].dt.month == selected_month]

    volume_sum = filtered_data['Volume'].sum()
    st.write(f"Total sales made in {selected_gantry} in {selected_month}: {volume_sum:,}")

    if selected_window == "Window 1":
        filtered_data = filtered_data[filtered_data['Date'].dt.day <= 15]
    elif selected_window == "Window 2":
        filtered_data = filtered_data[filtered_data['Date'].dt.day > 15]

    volume_sum = filtered_data['Volume'].sum()
    st.write(f"Total sales made in {selected_gantry} in {selected_month}, {selected_window}: {volume_sum:,}")

    st.subheader(f"Sales by OMC in {selected_gantry} for {selected_month}, {selected_window}:")
    sales_by_omc = filtered_data.groupby('OMC')['Volume'].sum()
    st.write(sales_by_omc)
    st.bar_chart(sales_by_omc)




def display_summary(data, selected_month, selected_window):
    if data is None:
        st.warning('Please upload a file first.')
        return

    if 'Gantry' not in data.columns:
        st.warning("Selected sheet does not contain 'Gantry' column.")
        return

    gantries = data['Gantry'].unique()
    omcs = data['OMC'].unique()

    summary_data = pd.DataFrame(index=omcs, columns=gantries)

    for gantry in gantries:
        filtered_data = data[(data['Gantry'] == gantry) & (data['Date'].dt.month == selected_month)]

        if selected_window == "Window 1":
            filtered_data = filtered_data[filtered_data['Date'].dt.day <= 15]
        elif selected_window == "Window 2":
            filtered_data = filtered_data[filtered_data['Date'].dt.day > 15]

        sales_by_omc = filtered_data.groupby('OMC')['Volume'].sum()

        # Fill missing values with zeros
        sales_by_omc = sales_by_omc.reindex(omcs, fill_value=0)

        summary_data[gantry] = sales_by_omc.values

    st.subheader(f"Summary Dataset for {selected_month}, {selected_window}:")


    # Calculate row and column totals
    summary_data['Total'] = summary_data.sum(axis=1)
    summary_data.loc['Total'] = summary_data.sum()

    # Filter out rows with a total of 0
    summary_data = summary_data[summary_data['Total'] != 0]

    # Save the summary_data DataFrame as an Excel file
    def convert_df(summary_data):
        return summary_data.to_csv(index=True).encode('utf-8')


    csv = convert_df(summary_data)
    st.download_button(
    "Press to Download",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv')



def visualize_sales(data, selected_month, selected_window):
    if data is None:
        st.warning('Please upload a file first.')
        return

    st.subheader("Sales Visualization")
    selected_category = st.selectbox("Select a category", ["OMC", "Gantry"])

    if selected_category == "OMC":
        if selected_window == "Window 1":
            filtered_data = data[(data['Date'].dt.month == selected_month) & (data['Date'].dt.day <= 15)]
        elif selected_window== "Window 2":
            filtered_data = data[(data['Date'].dt.month == selected_month) & (data['Date'].dt.day > 15)]

        sales_by_omc = filtered_data.groupby('OMC')['Volume'].sum()
        sales_by_omc.plot(kind='bar')
        plt.xlabel('OMC')
        plt.ylabel('Total Sales')
        plt.title('Total Sales by OMC')
        st.pyplot()

    elif selected_category == "Gantry":
        if selected_window == "Window 1":
            filtered_data = data[(data['Date'].dt.month == selected_month) & (data['Date'].dt.day <= 15)]
        elif selected_window == "Window 2":
            filtered_data = data[(data['Date'].dt.month == selected_month) & (data['Date'].dt.day > 15)]

        sales_by_gantry = filtered_data.groupby('Gantry')['Volume'].sum()
        sales_by_gantry.plot(kind='bar')
        plt.xlabel('Gantry')
        plt.ylabel('Total Sales')
        plt.title('Total Sales by Gantry')
        st.pyplot()







def main():
    st.title("Sales Analysis")

    data = upload_file()

    if data is not None:
        st.success("File uploaded successfully.")

        st.sidebar.header("Menu")
        
        menu_options = ["Welcome","Gantry", "OMC", "Visualization", 'Summary']
        selected_menu = st.sidebar.selectbox("Select an option", menu_options)

        # Get the unique months from the data
        months = data['Date'].dt.month.unique()

        

        selected_month_name = st.sidebar.selectbox("Select a month", month_names)

        # Get the numerical value of the selected month name
        selected_month = month_mapping[selected_month_name]

        window_options = ["Window 1", "Window 2"]
        selected_window = st.sidebar.selectbox("Select a window", window_options)

        if selected_menu == "Welcome":
            st.write("Welcome to Gidi's Reconciliation Web App. This web app was developed to help\
                      calculate the sales made to OMCs at various Gantry in Ghana.")
         
        elif selected_menu == "Gantry":
            display_gantry(data, selected_month, selected_window)
        elif selected_menu == "OMC":
            display_OMC(data, selected_month, selected_window)
        elif selected_menu == "Visualization":
            visualize_sales(data, selected_month, selected_window)
        elif selected_menu == "Upload":
            upload_file()
        elif selected_menu == 'Summary':
            display_summary(data, selected_month, selected_window)

if __name__ == '__main__':
    main()