import json
import time
import html
import pandas as pd
from flask import Flask, render_template, request, redirect,url_for
import os
import sys
from datetime import datetime, timedelta
import json
from pretty_html_table import build_table
from process_parser import *

app = Flask(__name__)
def today():
    date = datetime.now()
    return date.strftime("%Y-%m-%d")

MINIMAL_COLUMNS_PROCS = [
    'process_name',
    'active',
    'START',
    'RESTART',
    'STOP'
]

@app.route("/")
def index():
    data = find_procs_to_monitor_and_enrich()
    body = ''
    for header, proc_data in data.items():
        avg = proc_data['score'].mean()
        if avg == 1: color = 'green_dark'
        elif avg > 0: color = 'green_light'
        elif avg == 0: color = 'grey_light'
        elif avg == -1: color = 'red_dark'
        else: color = 'red_light'
        body+= f'<h3>{header} - Health: {avg} </h3>{html.unescape(build_table(proc_data[MINIMAL_COLUMNS_PROCS], color))}'
    return render_template('index.html', body=body)

@app.route("/more_info/<process_name>")
def more_info(process_name):
    data = find_procs_to_monitor_and_enrich(group=False)
    avg = data['score'].mean()
    if avg == 1:
        color = 'green_dark'
    elif avg > 0:
        color = 'green_light'
    elif avg == 0:
        color = 'grey_light'
    elif avg == -1:
        color = 'red_dark'
    else:
        color = 'red_light'
    print(data)
    target = data[data['process_name_'] == process_name ]
    header = html.unescape(build_table(target, color))

    # fetch last 10 lines of output
    # fetch last 10 lines of input
    # last updated logs time
    return render_template('more_info.html', header=header, process_name=process_name)


@app.route("/start/<process_name>", methods=['GET'])
def start(process_name):
    time.sleep(2)
    start_job(process_name)
    return index()

@app.route("/stop/<process_name>", methods=['GET'])
def stop(process_name):
    time.sleep(2)
    stop_job(process_name)
    return index()

@app.route("/restart/<process_name>", methods=['GET'])
def restart(process_name):
    time.sleep(2)
    restart_job(process_name)
    return index()
def launch():
    app.run(host='0.0.0.0', port=8001)

if __name__ == "__main__":
    launch()