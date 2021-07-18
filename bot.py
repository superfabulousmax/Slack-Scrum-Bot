
import slack_sdk
from slack_sdk.errors import SlackApiError
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from slackeventsapi import SlackEventAdapter
import datetime

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack_sdk.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
verification_token = os.environ['VERIFICATION_TOKEN']

@app.route('/test', methods=['POST'])
def test():
    if request.form['token'] == verification_token:     
        payload = {'text': 'successful!'}
        return jsonify(payload)
    payload = {'text': 'unsuccessful!'}
    return jsonify(payload)

@app.route('/teamorder', methods=['POST'])
def teamorder():
    if request.form['token'] == verification_token:
        text = '\n'.join(teamnames())
        payload = {'text': text}
        return jsonify(payload)
    return None

@app.route('/addteamorder', methods=['POST'])
def addteamorder():
    if request.form['token'] == verification_token:
        name = request.form['text']
        if(name == ''):
            text = 'No team name given. Use /addteamorder [name] to add a name.'
            payload = {'text': text}
            return jsonify(payload)
        name = (name[0]+"").upper() + name[1:].lower()
        addname(name)
        text = name + ' added to team order'
        payload = {'text': text}
        return jsonify(payload)
    return None

@app.route('/removeteamorder', methods=['POST'])
def removeteamorder():
    if request.form['token'] == verification_token:
        name = request.form['text']
        if(name == ''):
            text = 'No team name given. Use /removeteamorder [name] to remove the name.'
            payload = {'text': text}
            return jsonify(payload)
        removename(name)
        text = name + ' removed from team order'
        payload = {'text': text}
        return jsonify(payload)
    return None

@app.route('/moveteamorder', methods=['POST'])
def moveteamorder():
    if request.form['token'] == verification_token:
        direction = request.form['text'].lower()
        names = teamnames()
        text = ''
        if(names == []):
            text = 'No team names recorded. Use /addteamorder [name] to add a name.'
            payload = {'text': text}
            return jsonify(payload)
        newnames = []
        if(direction == 'forward'):
            newnames = [names[-1]] + names[:len(names)-1]
        if(direction == 'back'):
            newnames = names[1:] + [names[0]]
        if(newnames == []):
            text = 'Incorrect command. Usage /moveteamorder forward or /teamorder back.'
            payload = {'text': text}
            return jsonify(payload)
        writenames(newnames)
        text = 'moved team order '+ direction + ' by one\n'
        text += '\n'.join(teamnames())
        payload = {'text': text}
        return jsonify(payload)
    return None

def teamnames():
    file = open('./names.txt', 'r')
    lines = file.readlines()
    names = [n.strip() for n in lines]
    filtered_names = []
    for n in names:
        if n != '':
            filtered_names.append(n)
    file.close()
    return filtered_names

def addname(name):
    file = open('./names.txt', 'a')
    file.write("\n" + name)
    file.close()

def removename(target):
    file = open('./names.txt', 'r')
    lines = file.readlines()
    names = [n.strip() for n in lines]
    filtered_names = []
    for n in names:
        if n.lower() != target.lower() and n != '':
            filtered_names.append(n)
    print(filtered_names)
    file.close()
    file = open('./names.txt', 'w')
    for i in range(0, len(filtered_names)):
        name = filtered_names[i]
        if i < len(names) - 1:
            file.write(name + '\n')
        else:
            file.write(name)
    file.close()

def writenames(names):
    file = open('./names.txt', 'w')
    for i in range(0, len(names)):
        name = names[i]
        if i < len(names) - 1:
            file.write(name + '\n')
        else:
            file.write(name)
    file.close()

if __name__ == "__main__":
    app.run()