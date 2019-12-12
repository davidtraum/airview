import sys
import os
import json
import time

class Station:

    def __init__(self, pName, pMac):
        self.name = pName 
        self.mac = pMac
        self.lat = 0 
        self.lon = 0 
        self.coordinates = 0 

    def addCoordinate(self, lat, lon):
        if(self.lat == 0):
            self.lat = lat 
            self.lon = lon 
        else:
            self.lat += lat 
            self.lon += lon 
            self.lat /= 2 
            self.lon /= 2 
        self.coordinates += 1 

data = dict() 
datasetCount = 0 
columns = None
with open(sys.argv[1]) as file:
    for line in file:
        line = line[:-2] 
        if(columns == None):
            columns = line.split(", ")
            print(columns)
        else:
            args = line.split(",") 
            ssid = args[columns.index('ESSID')] 
            if(len(ssid)>0):
                datasetCount+=1 
                if(not ssid in data):
                    data[ssid] = Station(ssid, args[columns.index('BSSID')]) 
                data[ssid].addCoordinate(float(args[columns.index('Latitude')]), float(args[columns.index('Longitude')]))

print("Origin Datasets: " + str(datasetCount)) 
print("Parsed Accesspoints: " + str(len(data))) 

def printData():
    index = 0 
    for each in data:
        print(str(index) + ") " + each + ": " + str(data[each].lat) + " / " + str(data[each].lon)) 
        index+=1

def printStation(pStation):
    print("=== " + str(pStation.name) + " ===") 
    print("Latitude: " + str(pStation.lat)) 
    print("Longitude: " + str(pStation.lon)) 
    print("Times seen: " + str(pStation.coordinates)) 
    
def getJSON():
    obj = {} 
    
    about = {} 
    about['timestamp'] = int(time.time()*1000)
    about['creator'] = os.getlogin()
    about['station_count'] = len(data)
    about['origin_datasets'] = datasetCount
    obj['about'] = about
    
    jdata = [] 
    for sta in data:
        details = {} 
        details['ssid'] = data[sta].name
        details['lat'] = data[sta].lat
        details['lon'] = data[sta].lon
        details['times_seen'] = data[sta].coordinates
        details['mac'] = data[sta].mac
        jdata.append(details)
        
    obj['data'] = jdata
    
    return json.dumps(obj, indent=4)

def exportToFile(filename):
    with open(filename, 'w') as file:
        file.write(getJSON())
        file.flush()

def printIndex(pIndex):
    index = 0 
    for each in data:
        if(index == pIndex):
            printStation(data[each])
            return
        index+=1

def getStation(ident):
    try:
        index = int(ident)
        count=0
        for sta in data:
            if count == index:
                return data[sta]
            count+=1
    except Exception:
        try:
            return data[ident]
        except Exception:
            pass
try:
    while True:
        line = input(">> ") 
        args = line.split(" ")
        print(args)
        print(args[0])
        if(args[0]=='show'):
            printData()
        elif(args[0]=='exit'):
            break
        elif(args[0]=='detail'):
            try:
                index = int(args[1])
                printIndex(index)
            except Exception:
                printStation(data[args[1]])
        elif(args[0]=='maps'):
            sta = getStation(args[1])
            print(sta.lat, ' ', sta.lon)
            os.system('chromium ' + 'https://maps.google.com/?q=' + str(sta.lat) + ',' + str(sta.lon))
        elif(args[0]=='overview'):
            urlstring = 'https://www.google.com/maps/dir/'
            for sta in data:
                urlstring += str(data[sta].lat)
                urlstring += ','
                urlstring += str(data[sta].lon)
                urlstring += '/'
            urlstring += '/'
            os.system('chromium "' + urlstring + '"')
        elif(args[0]=='export'):
            exportToFile(args[1]) 
            
except KeyboardInterrupt:
    print("Exit") 
