
from flask import Flask, render_template, request, send_file, app
from datetime import datetime
import socket
import threading
import sys
import json
import os
import csv
import time
# connection vars
#RPi IP address
#host = '127.0.0.1'
host = '172.20.10.5'
#host='0.0.0.0'
port = 5003
global client
client = None
nicknames = []
global butt1
butt1 = 'SensorOFF'
headings = ["Time-","LDR Reading", "Temperature", "Temperature(C)"]
data =[]

# initialise server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)



# FlaskWebServer interface
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    # global button_status
    if request.method == 'POST':
        if request.form.get('SensorON') == 'SensorON':
            butt1 = 'SensorON'
            # Tell client to initiate transmission of data
            client.send(butt1.encode())
            print(butt1)
        
        elif  request.form.get('Status') == 'Status':
            # pass # do something else
            print("Status")
        elif  request.form.get('Check Log') == 'Check Log':
            # pass # do something else
            print("Log : ")
            return render_template("Sensor_Inf.html", headings=headings, data=data)

        elif request.form.get('Download Log') == 'DownloadLog':
            with open('Log.csv', 'w', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                
                writer.writerow(headings)
                
                for row in data:
                    writer.writerow(row)
            print("downloading")
            path = os.getcwd()+"/Log.csv"
            return send_file(path, as_attachment=True)
        
        elif  request.form.get('SensorOFF') == 'SensorOff':
            butt1 = 'SensorOFF'
            print("Exiting...")
            client.send(butt1.encode()) 
            print(butt1)

        elif  request.form.get('Exit()') == 'Exit()':
            # pass # do something else
            print("Exit()")
        else:
            return render_template("Sensor_Inf.html")
    elif request.method == 'GET':
        # do nothing
        pass
    return render_template("Sensor_Inf.html", butt1)

# Client handler - handles msgs rcvd from client
def handler(client):
    global data
    global stat
    while True:
            message = client.recv(2048).decode()
            if message != 'SENDACK' and data != 'ON':
                data.append(message)
            elif data == 'ON':
                stat = 'ON'
            print(message)
                


        

# listening function, connects to client and begins client thread
def receive():
    
    while(True):
        global client
        client, address = server.accept() # connect
        print("Starting connection with {}".format(str(address)))
        #global butt1
        client.send(butt1.encode('ascii'))
        

        # TO DO:: fix client thread
        client_thread = threading.Thread(target=handler, args=(client,)) # main thread for receving info from client
        client_thread.start()
    


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.1', port=80, debug=True, use_reloader=False)).start()
    receive()