from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user


import base64
import imghdr
import random
from datetime import datetime, timedelta
import datetime as dt

from . import DateToolKit as dtk
from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt
from . import ScreenGoRoute
from . import function_pool
from . import id_generator

if dbORM == None:
    User, Notes = None, None
else:
    User, Notes = dbORM.get_all("UserAPRO"), None


today = dt.datetime.now().date()


admin_actions = Blueprint('admin_actions', __name__)
aa = admin_actions

@aa.route("/admin-dashboard")
def enterAdminDBOARD():

    if function_pool.isAdmin(current_user.id) == True:
        return ScreenGoRoute.go_to("1", request=request, admin_pass=id_generator.generateTID())
    else:
        flash("You are restricted from accessing this.", category=['EOC', 'Access denied'])
        return ScreenGoRoute.go_to("1", request=request)

@aa.route("/admin-dashboard/<string:screen_id>")
def enterAdminDBOARDSceen(screen_id):

    if function_pool.isAdmin(current_user.id) == True:
        return ScreenGoRoute.go_to(screen_id, request=request, admin_pass=id_generator.generateTID())
    else:
        flash("You are restricted from accessing this.", category=['EOC', 'Access denied'])
        return ScreenGoRoute.go_to("1", request=request)

@aa.route("/add-broadcast", methods=['POST'])
def AddBroadCast():
    if function_pool.isAdmin(current_user.id) == True:

        _ = {
            "sender_id": "None", 
            "recipient_id": "None", 
            "title": request.form['title'].replace("'", "").replace('"', ""), 
            "content": request.form['content'].replace("'", "").replace('"', ""), 
            "type": "official", 
            "data": request.form['data'], 
            "datestamp": f"{function_pool.getDateTime()[0]}", 
            "timestamp": f"{function_pool.getDateTime()[1]}", 
            "status": "delivered", 
            "broadcast": "true"
        }
        dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_)))
        flash(f"Successfully broadcasted message '{request.form['title']}'.", category=['SUC', 'Message Broadcasted'])

        return ScreenGoRoute.go_to("9", request=request, admin_pass=id_generator.generateTID())
    else:
        flash("You are restricted from accessing this.", category=['EOC', 'Access denied'])
        return ScreenGoRoute.go_to("9", request=request)

@aa.route('/open-broadcast/<string:notification_id>')
def showBroadcast(notification_id):
    try:
        the_notification = dbORM.get_all("NotificationAPRO")[f'{dbORM.find_one("NotificationAPRO", "id", notification_id)}']
        dbORM.update_entry(
            "NotificationAPRO", 
            f"{dbORM.find_one('NotificationAPRO', 'id', notification_id)}", 
            encrypt.encrypter(str(
                {
                    "status": "read"
                }
            )), 
            dnd=False
        )
        return ScreenGoRoute.go_to("8", request=request, the_notification=the_notification)
    except Exception as e:
        flash(f"Error occured while retriving message. Try again later.{e} ", category=['EOC', 'Message load unsuccessful'])

        return ScreenGoRoute.go_to("8", request=request)

@aa.route("/delete-broadcast/<string:notification_id>")
def deleteBroadcast(notification_id):
    if function_pool.isAdmin(current_user.id) == True:
        dbORM.delete_entry("NotificationAPRO", dbORM.find_one("NotificationAPRO", "id", notification_id))

        flash(f"Deleted Broadcast!", category=['SUC', 'Deleted successfully'])

        return ScreenGoRoute.go_to("9", request=request, admin_pass=id_generator.generateTID())
    else:
        flash("You are restricted from accessing this.", category=['EOC', 'Access denied'])
        return ScreenGoRoute.go_to("1", request=request)




























# if function_pool.isAdmin(current_user.id) == True:
#     return ScreenGoRoute.go_to("1", request=request, admin_pass=id_generator.generateTID())
# else:
#     flash("You are restricted from accessing this.", category=['EOC', 'Access denied'])
#     return ScreenGoRoute.go_to("1", request=request)