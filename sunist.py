#-*- coding:utf-8 -*-
from __future__ import unicode_literals
from redis import Redis
import sys
import re
import json
import ast
from flask import (Flask, render_template, jsonify,
                   url_for, request, session, redirect, flash)

reload(sys)
sys.setdefaultencoding('utf-8')
redis = Redis()

app = Flask(__name__)
app.config.from_object('settings')

# solve jinja2 template and angularjs template conflictS
# app.jinja_env.variable_start_string = '{{ '
# app.jinja_env.variable_end_string = ' }}'

def status():
    keys = redis.keys('xbee:*')
    module = []
    for k in keys:
        m = re.match('xbee:\d+', k)
        if m:
            key = m.group()
            info = redis.hgetall(key)
            info['io'] = ast.literal_eval(info['io'])
            info['D'] = ast.literal_eval(info['D'])
            module.append(info)
    json_status = {"module":module, "counts":len(module)}
    return json_status

@app.route('/add')
def add():
    return 'Add a module'

@app.route('/remove')
def remove():
    return 'Remove a module'

@app.route('/change')
def change():
    return 'Change a module'

@app.route('/')
def index():
    stat = status()
    modules = []
    for m in stat['module']:
        module = {}
        module['name'] = m['name']
        module['address'] = m['address']
        module['io'] = zip(m['D'], m['io'])
        modules.append(module)
    return render_template('index.j2',contents=modules)

@app.route('/control', methods=["POST", "GET"])
def control():
    if request.method == 'POST':
        data = request.json
        addr = data['address']
        cmd = data['D']
        if data['io'] == 'false':
            para = 5
        else:
            para = 4
        msg = (addr, cmd, para)
        redis.publish('xbee:cmd', msg)
    return redirect(url_for('index'))

@app.route('/update')
def update():
    stat = status()
    return jsonify(**stat)

@app.route('/configure')
def configure():
    return 'Configure XBee modules here'

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.j2', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()
