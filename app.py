from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from test import main

app = Flask(__name__)
CORS(app)

@app.get("/")
def index():
    return "Hello World"

sched = BackgroundScheduler(daemon=True)
sched.add_job(main,'interval', seconds=20)
sched.start()