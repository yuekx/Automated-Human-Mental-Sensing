import pymysql
import pandas as pd
import json
import chat

def ConnectSensor(sensor): # "screen" or "battery"
    conn=pymysql.connect(host = '' # TODO: fill in host
    ,user = '' # TODO: fill in user
    ,passwd = '' # TODO: fill in passwd
    ,port = 3306
    ,db = 'test'
    )

    cursor = conn.cursor()
    query = "select * from "+sensor+" where device_id='eec39399-9e25-4384-a9eb-0f38724181c3';"
    cursor.execute(query)
    results = cursor.fetchall()
    if sensor=="screen":
        columns = ['_id','timestamp','device_id','screen_status'] 
    elif sensor=="battery":
        columns = ['_id','timestamp','device_id','battery_status','battery_level','battery_scale','battery_voltage','battery_temperature','battery_adaptor','battery_health','battery_technology']
    df = pd.DataFrame(results, columns=columns)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def SelectTime(df,TimeSpan): #"morning" or "afternoon" or "evening" or "night" or "daytime" or "whole day"
    df=df[(df['timestamp']>='2023-11-30') & (df['timestamp']<='2023-12-09')]
    df = df.copy()
    df['date'] = df['timestamp'].dt.date

    df.set_index('timestamp',inplace=True)
    if(TimeSpan=="morning"):
        selected_data = df.between_time('6:00','11:59')
    elif(TimeSpan=="afternoon"):
        selected_data = df.between_time('12:00','17:59')
    elif(TimeSpan=="evening"):
        selected_data = df.between_time('18:00','23:59')
    elif(TimeSpan=='night'):
        df_1=df[(df.index>='2023-11-30') & (df.index<='2023-12-08')]
        df_2=df[(df.index>='2023-12-01') & (df.index<='2023-12-09')]
        night_part1 = df_1.between_time('18:00', '23:59')
        night_part2 = df_2.between_time('00:00', '05:59')
        night_part2 = night_part2.copy()
        night_part2['date'] -= pd.Timedelta(days=1)
        selected_data = night_part1.combine_first(night_part2)
    elif(TimeSpan=="daytime"):
        selected_data = df.between_time('6:00','17:59')
    elif(TimeSpan=="whole day"):
        selected_data=df
    selected_data.reset_index(inplace=True)
    return selected_data

def CalcuMetrics(df,metrics,sensor):
    if(sensor=="screen"):
        if(metrics=="frequency"): # count of screen unlocked
            result = df[df['screen_status']==3].groupby('date').size().reset_index(name='frequency')
            ans = str(result['frequency'].mean())+" times"
        elif(metrics=="average_duration"): # duration of screen usage per unlocked
            unlocked_data = df[df['screen_status']==3]
            locked_data = df[df['screen_status']==2]
            df = pd.merge(unlocked_data,locked_data,how='outer').sort_values(by='timestamp')
            df['duration'] = df['timestamp'].diff()
            df['duration'] = df['duration'].where((df['screen_status'].shift(1)==3) & (df['screen_status']==2))
            result = df.groupby('date')['duration'].mean().reset_index(name='average_duration')
            ans = str(result['average_duration'].mean())
        elif(metrics=="total_duration"): # total time of screen usage
            unlocked_data = df[df['screen_status']==3]
            locked_data = df[df['screen_status']==2]
            df = pd.merge(unlocked_data,locked_data,how='outer').sort_values(by='timestamp')
            df['duration'] = df['timestamp'].diff()
            df['duration'] = df['duration'].where((df['screen_status'].shift(1)==3) & (df['screen_status']==2))
            result = df.groupby('date')['duration'].sum().reset_index(name='total_duration')
            ans = str(result['total_duration'].mean())
    elif(sensor=="battery"):
        if(metrics=="decrement"): # decrement of battery level
            df['decrement'] = df['battery_level'].diff()
            df['decrement'] = df['decrement'].where(df['decrement'] < 0)
            result = df.groupby('date')['decrement'].sum().reset_index(name='total_decrement')
            ans = str(-result['total_decrement'].mean())
        elif(metrics=="frequency"): # count of battery chages
            df['battery_adaptor'] = df['battery_adaptor'].where((df['battery_adaptor'].shift(1)!=1) & (df['battery_adaptor']==1))
            result = df.groupby('date')['battery_adaptor'].sum().reset_index(name='charge_frequency')
            ans = str(result['charge_frequency'].mean())+" charges"
    return ans

if __name__=='__main__':
    user_request = input()
    feature = chat.Chat(user_request)
    df = ConnectSensor(feature["sensor"])
    selected_data = SelectTime(df,feature["time span"])
    result = CalcuMetrics(selected_data,feature["metrics"],feature["sensor"])
    print("On average, the "+feature["metrics"]+" of "+feature["sensor"]+" is "+str(result)+" in the "+feature["time span"])