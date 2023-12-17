"""
Class: CS230--Section XXX
Name: Your name here
Description: (Give a brief description for Exercise name--See
below)
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import streamlit as st
import pandas as pd
import calendar
#Python | Calendar module. (n.d.). GeeksforGeeks. https://www.geeksforgeeks.org/python-calendar-module/
import pydeck as pdk
import plotly.express as px

data = pd.read_csv("bostoncrime2023_7000_sample.csv")
def most_common_day(data, selected_district="All Districts"):
    if selected_district == "All Districts":
        filtered_data = data
    else:
        data.dropna(subset=['DISTRICT'])
        # Pandas DataFrame.dropna() method. (2023, March 31). GeeksforGeeks. https://www.geeksforgeeks.org/python-pandas-dataframe-dropna/
        filtered_data = data[data['DISTRICT'] == selected_district]
    crime_counts_per_day = filtered_data['DAY_OF_WEEK'].value_counts().sort_index()
    return filtered_data, crime_counts_per_day
def reported_percentage_by_month(data, selected_month, selected_district="All Districts"):
    if selected_district == "All Districts":
        filtered_data = data
    else:
        data.dropna(subset=['DISTRICT'])
        filtered_data = data[data['DISTRICT'] == selected_district]
    selected_data = filtered_data[filtered_data['Month'] == selected_month]
    reported_percentage = round((len(selected_data) / len(filtered_data)) * 100)
    return reported_percentage
def most_common_crime_type(selected_district):
    if selected_district == "All Districts":
        filtered_data = data
    else:
        data.dropna(subset=['DISTRICT'])
        filtered_data = data[data['DISTRICT'] == selected_district]
    filter_conditions = (filtered_data['OFFENSE_DESCRIPTION'] != 'INVESTIGATE PERSON') & \
                        (filtered_data['OFFENSE_DESCRIPTION'] != 'SICK ASSIST') & \
                        (filtered_data['OFFENSE_DESCRIPTION'] != 'INVESTIGATE PROPERTY')
    filtered_data = filtered_data[filter_conditions]
    crime_counts_per_type = filtered_data['OFFENSE_DESCRIPTION'].value_counts().sort_index()
    return crime_counts_per_type
st.sidebar.title(":blue[Customization]")
districts_without_nan = data.dropna(subset=['DISTRICT'])
district_options = ['All Districts'] + list(districts_without_nan['DISTRICT'].unique())
selected_district = st.sidebar.selectbox("Select District:", district_options, index=0)
st.sidebar.title("Guess the Most Common Day of Crime")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
data['DAY_OF_WEEK'] = pd.Categorical(data['DAY_OF_WEEK'], categories=day_order, ordered=True)
#Pandas.unique. (n.d.). pandas. https://pandas.pydata.org/docs/reference/api/pandas.unique.html
filtered_data, crime_counts_per_day = most_common_day(data, selected_district)
selected_day_guess = st.sidebar.selectbox("Which day of the week do you think has the most crimes?",
                                          crime_counts_per_day.index)
selected_day_percentage = (crime_counts_per_day[selected_day_guess] / crime_counts_per_day.sum()) * 100
if selected_day_guess == crime_counts_per_day.idxmax():
#Pandas.DataFrame.idxmax.(n.d.).pandas.https: // pandas.pydata.org / pandas - docs / stable / reference / api / pandas.DataFrame.idxmax.html
    st.sidebar.success(
        #St.success. (2023). Streamlit documentation. https://docs.streamlit.io/library/api-reference/status/st.success
        f"Yes, you are correct!\n\n{selected_day_percentage:.2f}% of crimes were committed on {selected_day_guess}.")
else:
    st.sidebar.write(f"{selected_day_percentage:.2f}% of crimes were committed on {selected_day_guess}.")
st.sidebar.title("Guess the Percentage of Crimes Reported")
data['Month'] = pd.to_datetime(data['OCCURRED_ON_DATE']).dt.month_name()
#Pandas.to_datetime. (2023). pandas. https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
selected_month_name = st.sidebar.selectbox("Select a month:", list(calendar.month_name)[1:])
actual_percentage = reported_percentage_by_month(data, selected_month_name, selected_district)
user_guess_percentage = st.sidebar.slider(f"Guess what percentage of crimes are committed in {selected_month_name}",
                                          min_value=0, max_value=100)
if user_guess_percentage == actual_percentage:
    st.sidebar.success(
        f"Yes, you guessed correctly!\n\n{actual_percentage:.2f}% of crimes are actually reported in {selected_month_name}.")
else:
    st.sidebar.write(
        f"Your guess is incorrect!\n\n{actual_percentage:.2f}% of crimes are actually reported in {selected_month_name}.")
st.sidebar.title("Guess Most Common Type of Crime")
crime_counts_per_type = most_common_crime_type(selected_district)
selected_crime_type = st.sidebar.selectbox("Guess the most common type of crime:", crime_counts_per_type.index)
correct_crime_type = crime_counts_per_type.idxmax()
if selected_crime_type == correct_crime_type:
    st.sidebar.success(
        f"Yes, you are correct!\n\n{selected_crime_type} is the most common type of crime in the {selected_district} district.")
else:
    st.sidebar.write(
        f"No, the most common type of crime in the {selected_district} district is :green[{correct_crime_type}].")
intro, bar_graph, pie_chart = st.tabs(["Introduction", "Bar Graph", "Pie Chart"])
# St.pydeck_chart. (2023). Streamlit Inc. https://docs.streamlit.io/library/api-reference/charts/st.pydeck_chart
with intro:
    st.header("Boston Crime")
    st.write("Welcome to the Boston Crimes Analysis App. Explore crime data and make predictions!")
    st.image("Pic for Intro.jpg")
    filtered_df = filtered_data.dropna(subset=["lat"])
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            longitude=-71.0589,
            latitude=42.3601,
            #Boston, MA, USA. (2020, December 26). LatLong. https://www.latlong.net/place/boston-ma-usa-18552.html
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=filtered_df,
                get_position='[lon, lat]',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=filtered_df,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
                pickable=True,
            ),
        ],
    ))
with bar_graph:
    graphs = st.selectbox("Select the graph: ", ('Crime counts by day', 'Most common type of crime'))
    if graphs == 'Crime counts by day':
        st.title("Crimes per Day")
        st.bar_chart(crime_counts_per_day)
        st.caption(
            f"Bar graph showing the number of crimes committed each day of the week in the {selected_district} district.")
    else:
        st.title('Most common type of crime')
        crime_counts_per_type = most_common_crime_type(selected_district)
        st.bar_chart(crime_counts_per_type)
        st.markdown(f"**Most Common Type:** :green[{crime_counts_per_type.idxmax()}]")
with pie_chart:
    crimes_per_month = data['Month'].value_counts().sort_index().reset_index()
    crimes_per_month.columns = ['Month', 'count']
    st.write(crimes_per_month)
    fig = px.pie(
        data_frame=crimes_per_month,
        names='Month',
        values='count',
        title="Distribution of Crimes per Month",
        labels={'Month': 'Month', 'count': 'Crime Count'}
    )
    st.plotly_chart(fig)
    #Pie Charts in Python. (2023). Plotly. https://plotly.com/python/pie-charts/