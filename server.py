# coding: utf-8
import json
import socket
from threading import Thread

import time
from flask import Flask
from flask import request

s = socket.socket()
s.bind(('127.0.0.1', 4344))
s.listen(-1)

c = None


def accept_clients():
    while True:
        global c
        c = s.accept()
        c = c[0]


Thread(target=accept_clients).start()

tasks_to_do = []


def read_requests():
    global c
    while True:
        try:
            if c:
                try:
                    received = c.recv(4096).decode('utf-8')
                    if not received.isspace():
                        try:
                            # print('Received:', received)
                            json_string = json.loads(received)
                            global tasks_to_do
                            tasks_to_do.append(str(json_string['id']) + ',' + json_string['command'])
                        except (ValueError, AttributeError):
                            pass
                except ConnectionResetError:
                    c = None
        except KeyboardInterrupt:
            break

Thread(target=read_requests).start()

app = Flask(__name__)


@app.route('/hello/')
def hello():
    return 'Hello World!'


@app.route('/', methods=['GET', 'POST'])
def req():
    if request.method == 'GET':
        global tasks_to_do

        while len(tasks_to_do) <= 0:
            time.sleep(1)

        return tasks_to_do.pop(0)
    elif request.method == 'POST':
        print('Returned data: ' + str(request.form))

        data = request.form

        message = '{'
        if 'result' in data:
            message += '"result": "' + data['result'] + '",'
        if 'result2' in data:
            message += '"result2": "' + str(data['result2']) + '",'
        if 'error' in data:
            message += '"error": "' + str(data['error']) + '",'
        if 'id' in data:
            message += '"id": "' + str(data['id']) + '"'
        message += '}'

        c.send(message.encode('utf-8'))

    return ''


app.run(None, 4343)
