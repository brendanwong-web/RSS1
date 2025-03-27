#!/usr/bin/env python3
"""This is just a simple authentication example.

Please see the `OAuth2 example at FastAPI <https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/>`_  or
use the great `Authlib package <https://docs.authlib.org/en/v0.13/client/starlette.html#using-fastapi>`_ to implement a classing real authentication system.
Here we just demonstrate the NiceGUI integration.
"""
from typing import Optional, List
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime

from nicegui import app, ui
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload

client = PocketBase('http://127.0.0.1:8090')
topics = ['logger', 'plastic']

#DB

# in reality users passwords would obviously need to be hashed
unrestricted_page_routes = {'/login', '/register', '/test'}

#MQTT
MQTT_HOST = '172.20.10.10'
MQTT_PORT = 1883
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

class Data:
    weight = 0
    material = ''
    points = ''
    user_id = ''
    
    def __init__(self):
        self.weight = 12123
    def update_weight(self, w, m):
        self.weight = w
        self.material = m
        # print('written weight from class', self.weight)
    def update_points(self, uid):
        self.user_id = uid
        # self.points = int(self.weight) * 2
        # print('written data from class')
        
local_data = {'weight': 1212,}

data = Data()

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        if not app.storage.user.get('authenticated', False):
            if not request.url.path.startswith('/_nicegui') and request.url.path not in unrestricted_page_routes:
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        return await call_next(request)

app.add_middleware(AuthMiddleware)

def update_data(x, t):
    global local_data
    local_data['weight'] = x
    data.update_weight(x, t)
    
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for t in range(len(topics)):
        client.subscribe(topics[t])
        

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "logger": 
        return
    update_data(str(msg.payload.decode()), msg.topic)
    # print(msg.topic+" "+str(msg.payload.decode()))
    
def on_subscribe(client, obj, mid, reason_code_list):
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))
    ui.notify('arssgarsg')

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

@ui.page('/')
def main_page() -> None:
    test = app.storage.user["user_id"]
    filter_dic = {
        "filter": f"user_id ?= \"{test}\"",
    }
    try:
        result = client.collection("transactions").get_list(
        1, 20, filter_dic)
        transactions = []
        for t in range(len(result.items)):
            transaction_new = {
                "material": '',
                "weight": 0,
                "time": ''
            }
            transaction_new['material'] = result.items[t].material
            transaction_new['weight'] = result.items[t].weight
            transaction_new['time'] = result.items[t].time.split(' ')[0]
            transactions.append(transaction_new)
        transactions.reverse()
        print(transactions[0]['material'])
    except:
        print("unkown error ocurred")
        
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to('/login')

    with ui.row().classes("absolute-center"):
        with ui.column().classes('items-center mb-8'):
            ui.label(f'Hello {app.storage.user["username"]}!').classes('text-5xl mb-8')      
            ui.label("Welcome to recycling sorting center")
            ui.link('Start recycling', "/test")
            ui.button(on_click=logout, icon='logout').props('outline round').classes('mt-8')
        with ui.column().classes('items-center mb-8'):   
            with ui.row():  
                ui.label("Total times recycled")
                ui.label(result.total_items)
            with ui.row():
                with ui.column():
                    for i in range(len(transactions)):
                        with ui.row():
                            ui.label(transactions[i].get('material', 0))
                            ui.label(transactions[i].get('weight', 0))
                            ui.label(transactions[i].get('time', 0))

def update_db():
    print('update db')

@ui.page('/submit/{username}')
def submit_data(username: str) -> None:
    global data
    def home():
        ui.navigate.to('/')
    with ui.column().classes('absolute-center items-center mb-8'):
        with ui.row():
            ui.label(f'Submitted data for {username}')
        with ui.row():
            ui.label(f"Material: {data.material}")
        with ui.row():
            ui.label(f"Weight: {data.weight}")
        with ui.row():
            ui.label(f"Points earned: {data.points}")
            # ui.label("Weight: " + str(data.weight))
        with ui.row():
            ui.button(on_click=home, icon='home').props('outline round').classes('mt-8')
    
    # TODO write to db


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    '''def try_login() -> None:  # local function to avoid passing username and password as arguments
        if passwords.get(username.value) == password.value:
            app.storage.user.update({'username': username.value, 'authenticated': True})
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')'''
    async def try_login() -> None:
        authData = client.collection('users').auth_with_password(username.value, password.value)
        app.storage.user.update(
            {
                'username': authData.record.username,
                'email': authData.record.email,
                'authenticated': True,
                'user_id': authData.record.id,
                'created': authData.record.created,
            }
        )
        data.update_points(authData.record.id)
        if not authData.is_valid:
            ui.notify("invalid login details")
        ui.navigate.to(app.storage.user.get('referrer_path', '/'))
        
        
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)
        with ui.row():
            ui.label("Don\'t have an account yet?")
            ui.link('Register', "/register")

@ui.page('/register')
def register() -> None:
    def try_register() -> None:  # local function to avoid passing username and password as arguments
        data = {
            "username": username.value,
            "email": email.value,
            "emailVisibility": True,
            "password": password.value,
            "passwordConfirm": password2.value,
            "name": username.value
            }
        print(data)
        try:
            result = client.collection("users").create(data)
            # print(result)
            ui.notify("Account succesfully created!")
            ui.navigate.to("/")
        except Exception as error:
            ui.notify(error.data['data']['password']['message'])
            #ui.notify(error.data['message'])
            
    if app.storage.user.get('authenticated', False):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_register)
        email = ui.input('Email').on('keydown.enter', try_register)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_register)
        password2 = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_register)
        ui.button('Register', on_click=try_register)
    
@ui.page('/test')
def test():
    def set_transaction():
        data.update_points(app.storage.user.get('user_id'))
        transaction = {
                "material": data.material,
                "weight": data.weight,
                "points": data.points,
                "time": str(datetime.now()),
                "user_id": app.storage.user.get('user_id')
        };
        try:
            print(transaction)
            urlstring = '/submit/' + app.storage.user["username"]
            record = client.collection('transactions').create(transaction);
        except Exception as error:
            print(error.data['data'])
        ui.navigate.to(urlstring)
        ui.notify("data sent")
    def unlock_door():
        mqttc.publish("unlck", "1", qos=1)
    def release_compartment():
        mqttc.publish("gtpc", "open", qos=1)
    def begin_recycling():
        mqttc.publish("gtpc", "plastic", qos=1)
    def home():
        ui.navigate.to('/')
    with ui.column().classes('absolute-center items-center mb-8'):
        with ui.row():  
                ui.label('You are currently recycling')
                ui.label().bind_text_from(data, 'material')
        with ui.row():  
                ui.label("Weight: ").classes('text-2xl')
                ui.label().bind_text_from(data, 'weight').classes('text-2xl font-bold') 
        with ui.row():
            ui.button('Unlock', on_click=unlock_door)
            ui.button('Release', on_click=release_compartment)
            ui.button('Begin', on_click=begin_recycling)
            ui.button('Confirm data', on_click=set_transaction)
        with ui.row(): 
            ui.button(on_click=home, icon='home').props('outline round').classes('mt-8')
        
    
if __name__ in {'__main__', '__mp_main__'}:
    mqttc.loop_start() 
    ui.run(storage_secret='stasrtrt')   
    