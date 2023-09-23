import plotly.express as px
import streamlit as st
import duckdb
import datetime
# Define a function to load the DataFrame from DuckDB
@st.cache_data(ttl=3600)

def load_data(current_date):
    # Generate a unique cache key based on user_id and current_date
    cache_key = f"{current_date}"

    # Define the path to the Excel file
    TOKENDB=st.secrets["TOKENDB"]
    con = duckdb.connect(f'md:aggregated?motherduck_token={TOKENDB}')
    df = con.sql("SELECT * FROM aggregated_table").df()
    return df

# Get the current date
current_date = datetime.date.today()

# Load the DataFrame using the caching function with a custom cache key
df = load_data(current_date)

# Create a Streamlit sidebar for filters
st.sidebar.header('Filters')

# Filter by property type (multi-choice)
property_type_filters = st.sidebar.multiselect('Property Types', df['property.type'].unique(), df['property.type'].unique())

# Filter by bedroom count (multi-choice)
bedroom_count_filters = st.sidebar.multiselect('Bedroom Counts', df['property.bedroomCount'].unique(), df['property.bedroomCount'].unique()[1:5])

# Filter by postal code (multi-choice)
postal_code_filters = st.sidebar.multiselect('Postal Codes', df['property.location.postalCode'].unique(), 1170)

# Filter by date (checkbox)
filter_dates_from_june_24 = st.sidebar.checkbox('Filter Dates from June 24th', value=True)

# Create a custom sorting column based on the selected filters' priority
df['sorting_column'] = df['property.type']
if len(bedroom_count_filters) > 1:
    df['sorting_column'] = df['property.bedroomCount']
if len(postal_code_filters) > 1:
    df['sorting_column'] = df['property.location.postalCode']

# Apply filters to the cached DataFrame
filtered_df = df[
    df['property.type'].isin(property_type_filters) &
    df['property.bedroomCount'].isin(bedroom_count_filters) &
    df['property.location.postalCode'].isin(postal_code_filters) &
    (df['extractDate'] >= '2023-06-24' if filter_dates_from_june_24 else True)
]

# Create an interactive line chart using Plotly Express, and use the custom sorting column for line splitting
st.header('Interactive Chart per Extract Date')

grouped = filtered_df.groupby(['extractDate', 'sorting_column']).agg({'sum_value': 'sum', 'count_id': 'sum'})
grouped['avg'] = grouped['sum_value'] / grouped['count_id']

fig = px.line(
    grouped.reset_index(),  # Reset the index to use 'extractDate' and 'sorting_column' as separate columns
    x='extractDate',
    y='avg',
    color='sorting_column',  # Split lines based on the sorting column
    labels={'sum_value': 'Main Value'},
    title='Main Value Over Time',
)

st.plotly_chart(fig)
