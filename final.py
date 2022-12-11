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

ff1.Cache.enable_cache('UN5550/cache')

st.title("An Interactive Dashboard for Data Visualization on F1 Dataset")
st.subheader("------------------------")
st.write("-------")

#### Data upload ####
drivers = pd.read_csv('drivers.csv')
circuits = pd.read_csv('circuits.csv',index_col=0, na_values=r'\N')
constructorResults = pd.read_csv('constructor_results.csv',index_col=0, na_values=r'\N')
constructors = pd.read_csv('constructors.csv',index_col=0, na_values=r'\N')
constructorStandings = pd.read_csv('constructor_standings.csv',index_col=0, na_values=r'\N')
driverStandings = pd.read_csv('driver_standings.csv',index_col=0, na_values=r'\N')
lapTime = pd.read_csv('lap_times.csv')
pitStops = pd.read_csv('pit_stops.csv')
qualifying = pd.read_csv('qualifying.csv',index_col=0, na_values=r'\N')
races = pd.read_csv('races.csv',index_col=0, na_values=r'\N')
results = pd.read_csv('results.csv',index_col=0, na_values=r'\N')
seasons = pd.read_csv('seasons.csv',index_col=0, na_values=r'\N')
status = pd.read_csv('status.csv',index_col=0, na_values=r'\N')


### Data preprocessing ###

circuits = circuits.rename(columns={'name':'circuitName','location':'circuitLocation','country':'circuitCountry','url':'circuitUrl'})
drivers = drivers.rename(columns={'nationality':'driverNationality','url':'driverUrl'})
drivers['driverName'] = drivers['forename']+' '+drivers['surname']
constructors = constructors.rename(columns={'name':'constructorName','nationality':'constructorNationality','url':'constructorUrl'})
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
    tab1, tab2 = st.tabs(['matplt','plotly'])

    
#### Abu Dhabi 2022 EDA ####
    plotting.setup_mpl()

    race = ff1.get_session(2022, 'Abu Dhabi Grand Prix', 'R')
    race.load()

    lec = race.laps.pick_driver('LEC')
    per = race.laps.pick_driver('PER')
    asp = race.load()

    fig, ax = plt.subplots()
    ax.plot(lec['LapNumber'], lec['LapTime'], color='red')
    ax.plot(per['LapNumber'], per['LapTime'], color='blue')
    ax.set_title("LEC vs PER")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    tab1.write(fig)

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
    tab2.plotly_chart(fig)

##### Exclusive EDA of Racers ####

#adapted from https://medium.com/towards-formula-1-analysis/how-to-analyze-formula-1-telemetry-in-2022-a-python-tutorial-309ced4b8992

    year, grand_prix, session = 2022, 'Saudi Arabia', 'Q'
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

    plot_size = [15, 15]
    plot_title = f"{quali.event.year} {quali.event.EventName} - {quali.name} - {driver_1} VS {driver_2}"
    plot_ratios = [1, 3, 2, 1, 1, 2, 1]
    plot_filename = plot_title.replace(" ", "") + ".png"


# Make plot a bit bigger
    plt.rcParams['figure.figsize'] = plot_size

# Create subplots with different sizes
    fig, ax = plt.subplots(7, gridspec_kw={'height_ratios': plot_ratios})

# Set the plot title
    ax[0].title.set_text(plot_title)


# Delta line
    ax[0].plot(ref_tel['Distance'], delta_time)
    ax[0].axhline(0)
    ax[0].set(ylabel=f"Gap to {driver_2} (s)")

# Speed trace
    ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[1].set(ylabel='Speed')
    ax[1].legend(loc="lower right")

# Throttle trace
    ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[2].set(ylabel='Throttle')

# Brake trace
    ax[3].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[3].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[3].set(ylabel='Brake')

# Gear trace
    ax[4].plot(telemetry_driver_1['Distance'], telemetry_driver_1['nGear'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[4].plot(telemetry_driver_2['Distance'], telemetry_driver_2['nGear'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[4].set(ylabel='Gear')

    # RPM trace
    ax[5].plot(telemetry_driver_1['Distance'], telemetry_driver_1['RPM'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[5].plot(telemetry_driver_2['Distance'], telemetry_driver_2['RPM'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[5].set(ylabel='RPM')

    # DRS trace
    ax[6].plot(telemetry_driver_1['Distance'], telemetry_driver_1['DRS'], label=driver_1, color=ff1.plotting.team_color(team_driver_1))
    ax[6].plot(telemetry_driver_2['Distance'], telemetry_driver_2['DRS'], label=driver_2, color=ff1.plotting.team_color(team_driver_2))
    ax[6].set(ylabel='DRS')
    ax[6].set(xlabel='Lap distance (meters)')


    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for a in ax.flat:
        a.label_outer()
        
    # Store figure
    plt.savefig(plot_filename, dpi=600)
    tab1.write(fig)

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








