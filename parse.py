import json
import sys

AIRODUMP = {
    'ssid': 2,
    'mac': 3,
    'enc': 5,
    'lat': 6,
    'lon': 7,
    'time': 1,
    'skip': 2
}
WIGLE = {
    'ssid': 1,
    'mac': 0,
    'enc': 2,
    'lat': 6,
    'lon': 7,
    'time': 3,
    'skip': 2
}

class Station:

    def __init__(self, ssid, mac, lat, lon, time, enc):
        self.ssid = ssid
        self.mac = mac
        self.lat = lat
        self.lon = lon
        self.time = time
        self.enc = enc

    def addCoordinate(self, lat, lon):
        self.lat += lat
        self.lon += lon
        
        self.lat /= lat
        self.lon /= lon

data = {}

def read(path, reader):
    with open(path, 'r') as file:
        count = 0
        for line in file:
            if(count >= reader['skip']):
                split = line[:-1].split(",")
                if(len(split[reader['ssid']]) > 0):
                    for i in range(len(split)):
                        split[i] = split[i].strip()
                    if(split[reader['mac']] in data):
                        data[split[reader['mac']]].addCoordinate(float(split[reader['lat']]), float(split[reader['lon']]))
                    else:
                        station = Station(split[reader['ssid']], 
                        split[reader['mac']], 
                        float(split[reader['lat']]), 
                        float(split[reader['lon']]), 
                        split[reader['time']],
                        split[reader['enc']])
                        data[split[reader['mac']]] = station
            else:
                print("Skipped line")
            count+=1

def exportToFile(path):
    jo = {
        'data': []
    }

    for sta in data:
        sta = data[sta]
        so = {
            'ssid': sta.ssid,
            'mac': sta.mac,
            'enc': sta.enc,
            'lat': sta.lat,
            'lon': sta.lon,
            'time': sta.time,
        }
        jo['data'].append(so)

    with open(path, 'w') as file:
        file.write(json.dumps(jo, indent=2))
        file.flush()

while True:
    line = input(">> ")
    args = line.split(" ")
    if(args[0] == 'airodump'):
        read(args[1], AIRODUMP)
    elif(args[0] == 'wigle'):
        read(args[1], WIGLE)
    elif(args[0] == 'export'):
        exportToFile(args[1])
    elif(args[0] == 'exit'):
        sys.exit(0)