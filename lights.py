#!/usr/bin/python
from pprint import pprint as pp
from requests import get
import json, re, os, time
from influxdb import InfluxDBClient

conf = {
        'url': 'http://<hassio ip >:40850/api/',
        'auth' : '988112a4e198cc1211',
        'ifx' : {'host': '<hassio ip>', 'port': 8086, 'usr_': 'admin', 'pass_': 'PaSsWoRd', 'DB_': 'deconz_data'}
        }

client = InfluxDBClient(host=conf['ifx']['host'], port=conf['ifx']['port'], username=conf['ifx']['usr_'], password=conf['ifx']['pass_'])
client.switch_database(conf['ifx']['DB_'])

def url_ (api):
    url = conf['url']+conf['auth']+'/'+api
    headers = {'content-type': 'application/json'}
    response = get(url, headers=headers)
    return response

api_ = 'lights'
data = json.loads(url_(api_).text)
t = int(time.time())*1000000000


'''
Please identify the model in poshcon and add your model power usage
'''
watts = {
        'Classic A60 W clear - LIGHTIFY' : 8.5,
        'RB 245' : 5.3,
        'BY 265' : 9.0 
        }


for i in data.keys():
    if data[i]['modelid'] in watts.keys() and (data[i]['state']['on'] == True and data[i]['state']['reachable'] == True):
        watts_val = watts[(data[i]['modelid'])]
        data[i]['state'].update({'consumption': watts_val})
        data[i]['state'].update({'on': 1})
        data[i].update({'is_state': 'on'})
    elif data[i]['modelid'] in watts.keys() and (data[i]['state']['on'] == False and data[i]['state']['reachable'] == True): 
        data[i]['state'].update({'consumption': 0.3})
        data[i]['state'].update({'on': 0})
        data[i].update({'is_state': 'off'})
    else:
        data[i]['state'].update({'consumption': 0.0})
        data[i]['state'].update({'on': -1})
        data[i].update({'is_state': 'unknown'})

influx_lights = []
for i in data.keys():
        fields = data[i]['state']
        tags = data[i]
        del tags['state']
        influx_lights.append({ "measurement": api_,
                            "tags": tags,                               
                            "time": t,
                            "fields": fields
                        })
client.write_points(influx_lights)
