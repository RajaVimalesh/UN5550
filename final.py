from tkinter import Image
import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils
from fastf1 import plotting
import matplotlib.pyplot as plt

ff1.Cache.enable_cache('E:/MTU/DATASETS/cache')

st.title("An Interactive Dashboard for Data Visualization on F1 Dataset")
st.subheader("------------------------")
st.write("-------")

#### Data upload ####
drivers = pd.read_csv('E:/MTU/DATASETS/drivers.csv')
circuits = pd.read_csv('E:/MTU/DATASETS/circuits.csv',index_col=0, na_values=r'\N')
constructorResults = pd.read_csv('E:/MTU/DATASETS/constructor_results.csv',index_col=0, na_values=r'\N')
constructors = pd.read_csv('E:/MTU/DATASETS/constructors.csv',index_col=0, na_values=r'\N')
constructorStandings = pd.read_csv('E:/MTU/DATASETS/constructor_standings.csv',index_col=0, na_values=r'\N')
driverStandings = pd.read_csv('E:/MTU/DATASETS/driver_standings.csv',index_col=0, na_values=r'\N')
lapTime = pd.read_csv('E:/MTU/DATASETS/lap_times.csv')
pitStops = pd.read_csv('E:/MTU/DATASETS/pit_stops.csv')
qualifying = pd.read_csv('E:/MTU/DATASETS/qualifying.csv',index_col=0, na_values=r'\N')
races = pd.read_csv('E:/MTU/DATASETS/races.csv',index_col=0, na_values=r'\N')
results = pd.read_csv('E:/MTU/DATASETS/results.csv',index_col=0, na_values=r'\N')
seasons = pd.read_csv('E:/MTU/DATASETS/seasons.csv',index_col=0, na_values=r'\N')
status = pd.read_csv('E:/MTU/DATASETS/status.csv',index_col=0, na_values=r'\N')


### Data preprocessing ###

circuits = circuits.rename(columns={'name':'circuitName','location':'circuitLocation','country':'circuitCountry','url':'circuitUrl'})
drivers = drivers.rename(columns={'nationality':'driverNationality','url':'driverUrl'})
drivers['driverName'] = drivers['forename']+' '+drivers['surname']
constructors = constructors.rename(columns={'name':'constructorName','nationality':'constructorNationality','url':'constructorUrl'})
# races.index = races.index.set_names(['raceId','year','round','circuitId','raceName','date','time','raceUrl','a','b'])
#races = races[[]].reset_index()[['raceId','year','round','circuitId','raceName','date','time','raceUrl']]
#races.set_index('raceId',inplace=True)
races['date'] = races['date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))
pitStops = pitStops.rename(columns={'time':'pitTime'})
pitStops['seconds'] = pitStops['milliseconds'].apply(lambda x: x/1000)
results['seconds'] = results['milliseconds'].apply(lambda x: x/1000)

#st.dataframe(results)

### Define constructor color codes ###

constructor_color_map = {
    'Toro Rosso':'#0000FF',
    'Mercedes':'#6CD3BF',
    'Red Bull':'#1E5BC6',
    'Ferrari':'#ED1C24',
    'Williams':'#37BEDD',
    'Force India':'#FF80C7',
    'Virgin':'#c82e37',
    'Renault':'#FFD800',
    'McLaren':'#F58020',
    'Sauber':'#006EFF',
    'Lotus':'#FFB800',
    'HRT':'#b2945e',
    'Caterham':'#0b361f',
    'Lotus F1':'#FFB800',
    'Marussia':'#6E0000',
    'Manor Marussia':'#6E0000',
    'Haas F1 Team':'#B6BABD',
    'Racing Point':'#F596C8',
    'Aston Martin':'#2D826D',
    'Alfa Romeo':'#B12039',
    'AlphaTauri':'#4E7C9B',
    'Alpine F1 Team':'#2293D1'
}

#-----sidebar
page = st.sidebar.selectbox(
    'Select Options', ["Historical Data EDA","Pitstop Analysis", "Abu Dhabi 2022 EDA" ])
st.sidebar.markdown("""---""")
st.sidebar.image("F1.png", use_column_width=True)

if page == "Abu Dhabi 2022 EDA" :

    tab1, tab2, tab3 = st.tabs(["Qualifying Analysis", "Extra Params","Lap Times During Race" ])

#adapted from https://medium.com/towards-formula-1-analysis/how-to-analyze-formula-1-telemetry-in-2022-a-python-tutorial-309ced4b8992

    year, grand_prix, session = 2022, 'Abu Dhabi', 'Q'
    quali = ff1.get_session(year, grand_prix, session)
    quali.load() 
    driver_1, driver_2 = 'PER', 'LEC'

    # Laps can now be accessed through the .laps object coming from the session
    laps_driver_1 = quali.laps.pick_driver(driver_1)
    laps_driver_2 = quali.laps.pick_driver(driver_2)

    # Select the fastest lap
    fastest_driver_1 = laps_driver_1.pick_fastest()
    fastest_driver_2 = laps_driver_2.pick_fastest()

    # Retrieve the telemetry and add the distance column
    telemetry_driver_1 = fastest_driver_1.get_telemetry().add_distance()
    telemetry_driver_2 = fastest_driver_2.get_telemetry().add_distance()

    # Make sure whe know the team name for coloring
    team_driver_1 = fastest_driver_1['Team']
    team_driver_2 = fastest_driver_2['Team']

    # Extract the delta time
    delta_time, ref_tel, compare_tel = utils.delta_time(fastest_driver_1, fastest_driver_2)

    fig_delta = go.Figure()

    fig_delta.add_trace(go.Scatter(
        x=ref_tel['Distance'],
        y=delta_time,
        name='PER',
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))
        
    fig_delta.update_layout(template='simple_white',
        yaxis_title = 'Time Delta to Lec',
        xaxis_title = 'Laps Distance in Meters',
        title='Time Delta Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )
    fig_delta.add_hline(y=0, opacity=1, line_width=2, line_color='Red')
    fig_delta.add_hrect(
            y0=0, y1=0.3, line_width=0, 
            fillcolor="red", opacity=0.2)
    
    tab1.plotly_chart(fig_delta)

    fig_speed = go.Figure()

    fig_speed.add_trace(go.Scatter(
        x=telemetry_driver_1['Distance'],
        y=telemetry_driver_1['Speed'],
        name=driver_1,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_speed.add_trace(go.Scatter(
        x=telemetry_driver_2['Distance'],
        y=telemetry_driver_2['Speed'],
        name=driver_2,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_speed.update_layout(template='simple_white',
        yaxis_title = 'Speed Trace',
        xaxis_title = 'Laps Distance in Meters',
        title='Speed Trace Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )

    tab1.plotly_chart(fig_speed)

    fig_trottle = go.Figure()

    fig_trottle.add_trace(go.Scatter(
        x=telemetry_driver_1['Distance'],
        y=telemetry_driver_1['Throttle'],
        name=driver_1,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_trottle.add_trace(go.Scatter(
        x=telemetry_driver_2['Distance'],
        y=telemetry_driver_2['Throttle'],
        name=driver_2,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_trottle.update_layout(template='simple_white',
        yaxis_title = 'Speed Trace',
        xaxis_title = 'Laps Distance in Meters',
        title='Trottle Trace Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )

    tab1.plotly_chart(fig_trottle)

    fig_brake = go.Figure()

    fig_brake.add_trace(go.Scatter(
        x=telemetry_driver_1['Distance'],
        y=telemetry_driver_1['Brake'],
        name=driver_1,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_brake.add_trace(go.Scatter(
        x=telemetry_driver_2['Distance'],
        y=telemetry_driver_2['Brake'],
        name=driver_2,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_brake.update_layout(template='simple_white',
        yaxis_title = 'Speed Trace',
        xaxis_title = 'Laps Distance in Meters',
        title='Brake Trace Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )

    tab1.plotly_chart(fig_brake)

    fig_rpm = go.Figure()

    fig_rpm.add_trace(go.Scatter(
        x=telemetry_driver_1['Distance'],
        y=telemetry_driver_1['RPM'],
        name=driver_1,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_rpm.add_trace(go.Scatter(
        x=telemetry_driver_2['Distance'],
        y=telemetry_driver_2['RPM'],
        name=driver_2,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_rpm.update_layout(template='simple_white',
        yaxis_title = 'RPM Trace',
        xaxis_title = 'Laps Distance in Meters',
        title='RPM Trace Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )

    tab2.plotly_chart(fig_rpm)

    fig_gear = go.Figure()

    fig_gear.add_trace(go.Scatter(
        x=telemetry_driver_1['Distance'],
        y=telemetry_driver_1['nGear'],
        name=driver_1,
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_gear.add_trace(go.Scatter(
        x=telemetry_driver_2['Distance'],
        y=telemetry_driver_2['nGear'],
        name=driver_2,
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig_gear.update_layout(template='simple_white',
        yaxis_title = 'Gear Trace',
        xaxis_title = 'Laps Distance in Meters',
        title='Gear Trace Between LEC and PER in ABU DHABI 2022 Qualifiying',
        hovermode='x unified'
    )

    tab2.plotly_chart(fig_gear)

    plotting.setup_mpl()

    race = ff1.get_session(2022, 'Abu Dhabi Grand Prix', 'R')
    race.load()

    lec = race.laps.pick_driver('LEC')
    per = race.laps.pick_driver('PER')
    asp = race.load()

    fig_, ax = plt.subplots()
    ax.plot(lec['LapNumber'], lec['LapTime'], color='red')
    ax.plot(per['LapNumber'], per['LapTime'], color='blue')
    ax.set_title("LEC vs PER")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    tab3.write(fig_)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=per['LapNumber'],
        y=per['LapTime'],
        name='PER',
        mode='lines',
        marker=dict(size=[0, 0, 30, 0, 0, 0],
                color=[0, 0, 10, 0, 0, 0])
    ))

    fig.add_trace(go.Scatter(
        x=lec['LapNumber'],
        y=lec['LapTime'],
        name='LEC',
        mode='lines',
        marker=dict(size=[0, 0, 0, 30, 0, 0],
                color=[0, 0, 0, 10, 0, 0])
    ))

    for i, data in enumerate(fig['data']):
        fig.update_traces(marker_color=data['line']['color'],
                        selector=dict(name=data['name']))
        
    fig.update_layout(template='simple_white',
        yaxis_title = 'Lap Time',
        xaxis_title = 'Laps',
        title='Laptimes Between LEC and PER in ABU DHABI 2022',
        hovermode="x"
    )

    tab3.plotly_chart(fig)

elif page == "Pitstop Analysis":

    newResults = pd.merge(results,races,left_on='raceId',right_index=True,how='left')
    newResults = pd.merge(newResults,circuits,left_on='circuitId',right_index=True,how='left')
    newResults = pd.merge(newResults,constructors,left_on='constructorId',right_index=True,how='left')
    newResults = pd.merge(newResults,drivers,left_on='driverId',right_index=True,how='left')
    newResults = newResults.rename(columns={'driverId_x' : 'driverId'})


    newPitStops = pd.merge(pitStops,races,on='raceId',how='inner')
    newPitStops = pd.merge(newPitStops,circuits,on='circuitId',how='inner')
    newPitStops = pd.merge(newPitStops,newResults[['raceId','driverId','driverName','constructorId','constructorName']],on=['raceId','driverId'])


    #### Start of pitstop duration by constructor scatter plot ####
    fig = px.scatter(newPitStops[newPitStops['seconds']<50],
                    x='date',
                    y='seconds',
                    color='constructorName',
                    color_discrete_map=constructor_color_map,
                    )
    fig.update_layout(
        title_text='Pit Stop Durations over Time by Constructor',
    )

    st.plotly_chart(fig)

#### Start of pitstop duration by constructor ###
    
    fig = px.box(newPitStops[newPitStops['seconds']<50].groupby(by=['raceId','name','date','constructorName']).mean().reset_index().sort_values(by='seconds',ascending=True),
                 x='constructorName',
                 y='seconds',
                 color='constructorName',
                 color_discrete_map=constructor_color_map,
                )
    fig.update_layout(
        title_text='Pit Stop Durations by Constructor',
    )
    st.plotly_chart(fig)

    #### End of pitstop duration by constructor ####

else:
    #### Start of Most number of wins ####
    results = results[results['position'] != '\\N']
    results[['position']] = results[['position']].apply(pd.to_numeric)
    results_1 = results[results['position']==1]
    wins_driverID = results_1.groupby('driverId').size().reset_index()
    wins_driverID.columns = ['driverId','total_wins']
    top_wins_driver = wins_driverID.sort_values(by=['total_wins'],ascending = False).head(10)
    driver_names = pd.merge(drivers,top_wins_driver, on = 'driverId', how = 'inner')
    data_types_dict = {'forename': str, 'surname':str}
    driver_names = driver_names.astype(data_types_dict)
    driver_names['name'] = driver_names['forename'] +' '+ driver_names['surname']
    driver_names = driver_names[['name','total_wins']].sort_values(by=['total_wins'],ascending = False)

    fig = px.bar(driver_names, x = 'name', y = 'total_wins')
    fig.update_layout(
        title_text='Most Number of Wins - Drivers',
    )
    st.plotly_chart(fig)
    #### End of Most number of wins ####

    #### Start of Drivers with max points ####

    race_driver = pd.merge(results,races, on = 'raceId', how = 'inner')
    points = race_driver[['driverId','points']].groupby('driverId').sum().sort_values(by=['points'], ascending = False).reset_index()
    driver_names_points_result = pd.merge(drivers,points, on = 'driverId', how = 'inner')
    data_types_dict = {'forename': str, 'surname':str}
    driver_names_points_result = driver_names_points_result.astype(data_types_dict)
    driver_names_points_result['name'] = driver_names_points_result['forename'] +' '+ driver_names_points_result['surname']
    driver_names_points_result = driver_names_points_result[['name','points']].sort_values(by=['points'],ascending = False).head(10)
    fig_points_results = px.bar(driver_names_points_result, x = 'name', y = 'points')
    fig_points_results.update_layout(
        title_text='Drivers with Maximum Points',
    )
    st.plotly_chart(fig_points_results)

#### End of Drivers with max points ####

#### Start of Countries with Most F1 Drivers ####
    dfg = drivers.groupby(['driverNationality']).size().to_frame().sort_values([0], ascending = False).head(10).reset_index()
    dfg = drivers.groupby(['driverNationality'])['driverId'].count().head(10).reset_index()
    dfg.columns = ['driverNationality','count']
    dfg = dfg.sort_values(by = 'count', ascending=False)
    fig = px.bar(dfg, x = 'driverNationality', y = 'count', title='Countries With Most F1 Drivers')
    st.plotly_chart(fig)
#### End of Countries with Most F1 Drivers ####








