import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import duckdb
import datetime
import matplotlib.pyplot as plt


@st.cache_data(ttl=3600)
def load_data(current_date):
    # Generate a unique cache key based on user_id and current_date
    cache_key = f"{current_date}"
    TOKENDB=st.secrets["TOKENDB"]
    con = duckdb.connect(f'md:aggregated?motherduck_token={TOKENDB}')
    df = con.sql("SELECT * FROM V2aggregated_table").df()
    return df

def main():
    st.set_page_config( layout="wide") 
    st.title("Dashboard")

    current_date = datetime.date.today()
    df = load_data(current_date)
    print(df.shape)

    # Sidebar for filters
    st.sidebar.header('Filters')

    columns = df.columns.tolist()
    blacklist = st.sidebar.multiselect("Columns to exclude from filtering", columns)
    filtered_columns = [col for col in columns if col not in blacklist]
    df['property.location.postalCode'] = df['property.location.postalCode'].astype('string')
    if filtered_columns:  # Check if any columns are selected for filtering
        for col in filtered_columns:
            # Example: Slider for numerical filtering
            if df[col].dtype == 'float64' or df[col].dtype == 'int64':

                min_value = df[col].min(skipna=True)  # Skip NaN values
                max_value = df[col].max(skipna=True)  # Skip NaN values
                if min_value != max_value:
                    selected_min = st.sidebar.slider(f"Select minimum {col}", min_value, max_value, min_value)
                    selected_max = st.sidebar.slider(f"Select maximum {col}", min_value, max_value, max_value)
                else:
                    selected_max = selected_min = st.sidebar.multiselect(f"Select {col}", [max_value])
                if min_value != selected_min or max_value != selected_max:
                    df = df[(df[col] >= selected_min) & (df[col] <= selected_max)]
            else:
                # Example: Text filtering
                filter_text = st.sidebar.multiselect(f"Enter value for {col} filter", df[col].unique())

                if filter_text:
                    print(filter_text)
                    print(col)
                    df = df[df[col].isin(filter_text)]
                    print(df.shape)
    else:       
        st.warning("No columns selected for filtering.")  # Display a warning if no columns are selected for filtering
        # Return the original DataFrame without any filtering


    print(df.shape)
    grouped = df.groupby(['extractDate']).agg({'sum_price': 'sum', 'num_properties': 'sum'})
    grouped['avg'] = grouped['sum_price'] / grouped['num_properties']

    fig1 = px.line(
        grouped.reset_index(),  # Reset the index to use 'extractDate' and 'sorting_column' as separate columns
        x='extractDate',
        y='num_properties',
        labels={'sum_price': 'Main Value','num_properties':'Number of properties'},
        title='Number of properties Over Time'        
    )
    fig2 = px.line(
        grouped.reset_index(),  # Reset the index to use 'extractDate' and 'sorting_column' as separate columns
        x='extractDate',
        y='avg',
        labels={'sum_price': 'Main Value','avg_price':'Average price of properties'},
        title='AVG Main Value Over Time'        
    )


    # Group data by 'extractDate' and calculate the average price
    

    # Create Streamlit app
    st.title('Average Property Price Over Time')


    col1, col2, col3 = st.columns([1, 1, 1])
    col4, col5, col6 = st.columns([1, 1, 1])


    with col1:
        st.header("Number of housing offers")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.header("Average asking price of housing offers")
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        st.header("Placeholder")
        st.plotly_chart(fig1, use_container_width=True)
    with col4:
        st.header("Placeholder")
        st.plotly_chart(fig2, use_container_width=True)
    with col5:
        st.header("Placeholder")
        st.plotly_chart(fig2, use_container_width=True)
    with col6:
        st.header("Placeholder")
        st.plotly_chart(fig2, use_container_width=True)
        
if __name__ == '__main__':
    main()
