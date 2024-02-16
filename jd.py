import pandas as pd
import streamlit as st
import os


DATA_DIR = "data"



# Define a password for authentication
PASSWORD = "password123"

# Define Streamlit's SessionState class
class SessionState:
    def __init__(self):
        self.logged_in = False

# Create an instance of SessionState
session_state = SessionState()

def login():
    st.title("Login")
    password = st.text_input("Password", type="password")
    if password == PASSWORD:
        session_state.logged_in = True
        st.success("Logged in successfully.")
    else:
        st.error("Invalid password. Please try again.")




def upload_file():
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, header=1)
        data = data.drop(columns=['STOCKS VALUE ', 'Unnamed: 10', 'MINIMUM SALES ', \
                                  'Unnamed: 16'])
        data = data.set_axis(data.iloc[0], axis=1)
        new = ['OIL STATION', 'Tank PMS', 'Tank AGO', 'GIT PMS', 'GIT AGO', 'STOCK LEVEL PMS', 'STOCK LEVEL AGO',
               'ULLAGE PMS', 'ULLAGE AGO', 'DEAD STOCKS PMS', 'DEAD STOCKS AGO','AV. CONSUMPTION PMS','AV. CONSUMPTION AGO',\
                'MAX SALES PMS', 'MAX SALES AGO',
               'LITERS PMS', 'LITERS AGO']
        data.columns = new
        data = data.drop(index=[0, 1])
        data=data[:-1]
        data = data.fillna(0)

        # Create the data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        # Save the data as a CSV file
        filename = os.path.join(DATA_DIR, "uploaded_data.csv")
        data.to_csv(filename, index=False)

        st.sidebar.success("Data uploaded and saved")

        pass
        return data
        

def load_saved_data():
    filename = os.path.join(DATA_DIR, "uploaded_data.csv")
    if os.path.exists(filename):
        data = pd.read_csv(filename)
        return data
    else:
        return None
    
        

def calculate_day(data, selected_category, selected_station, goods_in_transit, git_dict):
    if data is None:
        st.warning('Please upload a file first.')
        return None

    if 'OIL STATION' not in data.columns:
        st.warning("Selected sheet does not contain 'OIL STATION' column.")
        return None

    filtered_data = data[['OIL STATION']].copy()

    stock_level_column = f"STOCK LEVEL {selected_category}"
    dead_stocks_column = f"DEAD STOCKS {selected_category}"
    max_sales_column = f"MAX SALES {selected_category}"
    ullage_column = f"ULLAGE {selected_category}"
    tank_column = f"Tank {selected_category}"
    avg_consumption = f"AV. CONSUMPTION {selected_category}"

    zero_mask = data[max_sales_column] == 0
    data.loc[zero_mask, max_sales_column] = 1

    filtered_data['Current Stock'] = data[stock_level_column]

    # Update GIT value in the dictionary
    git_dict[selected_station] = goods_in_transit

    # Adjust current stock based on goods in transit
    for station in git_dict.keys():
        filtered_data.loc[filtered_data['OIL STATION'] == station, 'Current Stock'] += git_dict[station]

    filtered_data['Days Left(max sales)'] = ((filtered_data['Current Stock'] - data[dead_stocks_column]) / data[max_sales_column]).apply(
        lambda x: max(0, round(x)))

    filtered_data['Days Left(avg)'] = ((filtered_data['Current Stock'] - data[dead_stocks_column]) / data[avg_consumption]).apply(
        lambda x: max(0, int(round(x))) if x != float('inf') else 0)

    filtered_data['Demand'] = data[max_sales_column] * filtered_data['Days Left(max sales)']

    demand_exceeds_ullage_mask = filtered_data['Demand'] > data[ullage_column]
    filtered_data['Days Left(max sales)'] = filtered_data['Days Left(max sales)'].apply(lambda x: max(0, round(x)))
    filtered_data['Demand'] = data[max_sales_column] * filtered_data['Days Left(max sales)']

    # Calculate the "Qty Needed to be full" column
    filtered_data['Qty Needed to be full'] = data[tank_column] - filtered_data['Current Stock']
    # Calculate the "sellable Qty"
    filtered_data['Sellable Qty'] = filtered_data['Current Stock'] - data[dead_stocks_column]
    # Add Goods in Transit (GIT) column
    filtered_data['GIT'] = filtered_data['OIL STATION'].map(git_dict)

    filtered_data = filtered_data.sort_values(by='Days Left(max sales)', ascending=True)

    st.subheader(f"STOCK MONITORING TABLE - {selected_category}")
    st.table(filtered_data.reset_index(drop=True))  # Remove index column

    pass

    return filtered_data

def convert_df(filtered_data, git_dict):
    # Update GIT column with values from the dictionary
    filtered_data['GIT'] = filtered_data['OIL STATION'].map(git_dict)
    pass
    return filtered_data.to_csv(index=True).encode('utf-8')

def main():
    st.sidebar.title("Column Selection")
    data = upload_file()

    if data is None:
        # Load saved data if it exists
        data = load_saved_data()

    if data is not None:
        category = st.sidebar.radio("Select category", ["AGO", "PMS"])

        # Add input fields for station and goods in transit
        selected_station = st.sidebar.selectbox("Select Station", data["OIL STATION"])
        goods_in_transit = 0  # Set default value to 0

        if selected_station:
            goods_in_transit = st.sidebar.number_input("Goods in Transit", min_value=0, value=0)

        # Create or load the GIT dictionary
        git_dict = st.session_state.get('git_dict', {})
        if not git_dict:
            stations = data["OIL STATION"].tolist()
            git_dict = {station: 0 for station in stations}
            st.session_state['git_dict'] = git_dict

        if st.sidebar.checkbox("Show Table"):
            filtered_data = calculate_day(data, category, selected_station, goods_in_transit, git_dict)

            # Check if Goods in Transit is more than Qty Needed to be full
            if selected_station:
                qty_needed_to_be_full = filtered_data.loc[
                    filtered_data['OIL STATION'] == selected_station, 'Qty Needed to be full'].values[0]
                if goods_in_transit > qty_needed_to_be_full:
                    st.error("Goods in Transit cannot be more than Qty Needed to be full")

            csv = convert_df(filtered_data, git_dict)
            st.download_button("Press to Download", csv, "file.csv", "text/csv", key='download-csv')

if __name__ == '__main__':
    main()
