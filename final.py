import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px

st.write('hello world')

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

st.dataframe(results)

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

st.dataframe(results)

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

newResults = pd.merge(results,races,left_on='raceId',right_index=True,how='left')
newResults = pd.merge(newResults,circuits,left_on='circuitId',right_index=True,how='left')
newResults = pd.merge(newResults,constructors,left_on='constructorId',right_index=True,how='left')
newResults = pd.merge(newResults,drivers,left_on='driverId',right_index=True,how='left')
newResults = newResults.rename(columns={'driverId_x' : 'driverId'})


newPitStops = pd.merge(pitStops,races,on='raceId',how='inner')
newPitStops = pd.merge(newPitStops,circuits,on='circuitId',how='inner')
newPitStops = pd.merge(newPitStops,newResults[['raceId','driverId','driverName','constructorId','constructorName']],on=['raceId','driverId'])

fig = px.box(newPitStops[newPitStops['seconds']<50].groupby(by=['raceId','name','date','constructorName']).mean().reset_index().sort_values(by='seconds',ascending=True),
                 x='constructorName',
                 y='seconds',
                 color='constructorName',
                 color_discrete_map=constructor_color_map,
                )
fig.update_layout(
    title_text='Pit Stop Durations by Constructor from 2011 to date',
)
st.plotly_chart(fig)
