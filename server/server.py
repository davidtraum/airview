from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse,parse_qs
import sqlite3

DEFAULT_CONFIG = {
    'ip': 'localhost',
    'port': 2020,
    'database': 'airview.db',
    'max_result_size': 1000
}

if(not os.path.exists('config.json')):
    with open('config.json', 'w') as file:
        file.write(json.dumps(DEFAULT_CONFIG, indent=4))
        file.flush()
        print("Created default config.")

CONFIG = dict()
with open('config.json') as file:
    CONFIG = json.loads(file.read())

conn = sqlite3.connect(CONFIG['database'])
cursor = conn.cursor()
try:
    cursor.execute('CREATE TABLE stations (ssid text, mac text, lat real, lon real)')
    conn.commit()
except sqlite3.OperationalError:
    pass

def addData(data):
    for sta in data['data']:
        print(sta)
        try:
            results = cursor.execute("SELECT * FROM stations WHERE mac='" + sta['mac'] + "'")
            if(results.rowcount>0):
                cursor.execute("UPDATE stations SET lat = " + str(sta['lat']) + ", lon = " + str(sta['lon']) + " WHERE mac=" + sta['mac'])
            else:
                cursor.execute("INSERT INTO stations VALUES ('" + sta['ssid'] + "', '" + sta['mac'] + "', " + str(sta['lat']) + ", " + str(sta['lon']) + ")")
        except Exception as e:
            print(e)
    conn.commit()


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self.send_response(200) 
        self.send_header('Content-type', 'text/html') 
        self.end_headers() 
        self.wfile.write(b'sucess')
        addData(json.loads(post_data.decode('utf-8')))

    def do_GET(self):
        parsed = urlparse(self.path) 
        query = parse_qs(parsed.query)
        self.send_response(200) 
        self.send_header('Content-type', 'text/html') 
        self.end_headers() 
        if(parsed.path == '/aws/add'):
            data = json.loads(query['data'][0])
            print("Adding " + data['ssid'])
            results = cursor.execute("SELECT * FROM stations WHERE mac='" + data['mac'] + "'")
            print(results.rowcount)
            if(results.rowcount>0):
                cursor.execute("UPDATE stations SET lat = " + str(data['lat']) + ", lon = " + str(data['lon']) + " WHERE mac=" + data['mac'])
            else:
                cursor.execute("INSERT INTO stations VALUES ('" + data['ssid'] + "', '" + data['mac'] + "', " + str(data['lat']) + ", " + str(data['lon']) + ")")
            conn.commit()
            self.wfile.write(b"sucess")
        elif(parsed.path == '/aws/upload'):
            pass
        elif(parsed.path == '/aws/get'):
            data = json.loads(query['data'][0])
            print("Loading " + str(data))
            returnData = {
                'data': list()
            }
            if('area' in data):
                print("Serving area: " + str(data['area']))
                rows = cursor.execute('SELECT * FROM stations WHERE lat BETWEEN ' + 
                str(data['area']['lat']['min']) + 
                ' and ' + str(data['area']['lat']['max']) + 
                ' AND lon BETWEEN ' + str(data['area']['lon']['min']) + 
                ' and ' + str(data['area']['lon']['max']))
                count = 0
                for result in rows:
                    obj = {}
                    obj['ssid'] = result[0]
                    obj['mac'] = result[1]
                    obj['lat'] = result[2]
                    obj['lon'] = result[3]
                    returnData['data'].append(obj)
                    count+=1
                    if(count > CONFIG['max_result_size']):
                        break
            self.wfile.write(json.dumps(returnData, indent=2).encode('utf-8'))

server = HTTPServer((CONFIG['ip'], int(CONFIG['port'])), Handler) 
server.serve_forever() 