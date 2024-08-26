from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_from_directory, session, jsonify
from flask_login import login_required, current_user


import base64
import imghdr
import datetime as dt
from datetime import datetime, timedelta

from . import DateToolKit as dtk
# from .db import db
# from .db import dbORM
# from . import encrypt
from . import function_pool
from . import ScreenGoRoute

from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt

# from . import app

if dbORM == None:
    User, Notes = None, None
else:
    User, Notes = dbORM.get_all("UserAPRO"), None


today = dt.datetime.now().date()


views = Blueprint('views', __name__)

def get_mime_type(data):
    decoded_data = base64.b64decode(data)
    image_type = imghdr.what(None, h=decoded_data)
    return f'image/{image_type}' if image_type else ''

def getDBItem(model, column, value):
    
    try:
        i = dbORM.get_all(model)[f'{dbORM.find_one(model, column, value)}']
    except Exception as e:
        i = {}

    return i



@views.route("/")
def welcome():
    
    return render_template("landing.html")

@views.route("/dashboard")
@login_required
def dashboard():
    def calculateTimeDifference(dpt, ct):
        return [int(x) for x in ("[" + str(datetime.strptime(dpt, "%H:%M") - datetime.strptime(ct, "%H:%M:%S")).replace(":", ", ").replace("-1 day, ", "") + "]").strip("[]").split(", ")]
    
    if dbORM.get_all("UserAPRO")[current_user.id]['waitlist'] != "launched":
        return render_template("WaitLobby.html", CUser=dbORM.get_all("UserAPRO")[current_user.id], TimeDifference=calculateTimeDifference, CurrentTime=function_pool.getDateTime()[1])
    else:
        return ScreenGoRoute.go_to("1", request=request)

@views.route("/dashboard/<string:screen_number>")
@login_required
def dashboardPages(screen_number):
    def calculateTimeDifference(dpt, ct):
        return [int(x) for x in ("[" + str(datetime.strptime(dpt, "%H:%M") - datetime.strptime(ct, "%H:%M:%S")).replace(":", ", ").replace("-1 day, ", "") + "]").strip("[]").split(", ")]
    
    if dbORM.get_all("UserAPRO")[current_user.id]['waitlist'] != "launched":
        return render_template("WaitLobby.html", CUser=dbORM.get_all("UserAPRO")[current_user.id], TimeDifference=calculateTimeDifference, CurrentTime=function_pool.getDateTime()[1])
    else:
        return ScreenGoRoute.go_to(screen_number, request=request)

@views.route('/render-image', methods=['POST'])
def renderImage():
    return render_template("ViewImage.html", assignment_id=request.form['assignment_id'], data_raw=request.form['base64_encoding'])