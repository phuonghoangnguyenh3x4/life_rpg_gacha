import json
from dotenv import load_dotenv
import os
from NotionPy import NotionPy
from Game import Game
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
STORE_DB_ID = os.getenv("STORE_DB_ID")
PLAYER_DB_ID = os.getenv("PLAYER_DB_ID")

notionPy = NotionPy(NOTION_API_KEY)
game = Game(notionPy, STORE_DB_ID, PLAYER_DB_ID)

player = None
app = Flask(__name__)
CORS(app)

@app.route('/draw1card', methods=["POST"])
def draw1card():
    global player
    random_collectables = game.get_n_random_collectables(1)
    game.buy_collectables(player, random_collectables)
    return jsonify(random_collectables[0])

@app.route('/get-collectables')
def get_collectables():
    global player
    players = game.get_players()
    username = request.args.get('username')
    player = notionPy.search_by_title(players, username)[0] 
    return jsonify(game.get_player_collection(player))

if __name__ == "__main__": 
    app.run()