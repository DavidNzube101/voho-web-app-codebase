from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# from .db import dbORM
from . import DateToolKit as dtk

import base64
import imghdr
# from . import encrypt

from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt

import random
from . import function_pool
import datetime as dt
from . import id_generator
from datetime import datetime

User, Record = dbORM.get_all("UserAPRO"), None
	
								# <!-- <img src="data:{{ getMIME( Task['image_raw'] ) }};base64,{{ Task['image_raw'] }}" style="background: white; aspect-ratio: 1/1; width: 40px; padding: 20px; object-fit: cover;"> -->


def go_to(screen_id, _redirect=False, **kwargs):
	if _redirect == False:
		u = dbORM.get_all("UserAPRO")[f'{current_user.id}']

		def checkImagePassError(image_raw):
			try:
				rr = f"data:{function_pool.getMIME(image_raw)};base64,{image_raw}"
				return "false"
			except:
				return "true"


		all_assignments = []
		Assignment = dbORM.get_all("AssignmentAPRO")
		for x, y in Assignment.items():
			all_assignments.append(y)

		my_assignments = dbORM.find_all("AssignmentAPRO", "reg_number", u['reg_number'])

		# flash("Hey this is a flash", category=["SUC", "Changed Profile Picture"])

		def tryGetKwargs(keyword, exception_text):

			try:
				return kwargs[keyword]
			except:
				return exception_text

		my_assignments = tryGetKwargs('the_assignment', dbORM.find_all("AssignmentAPRO", "reg_number", u['reg_number']))
		active_tab = tryGetKwargs('active_tab', 'All')
		assignment_to_view = tryGetKwargs('TheAssignmentToView', '')
		main_tab = tryGetKwargs('main_tab', 'All')
		assignment_list = tryGetKwargs('assignment_list', None)
		search_result = tryGetKwargs('search_result', None)
		search_input = tryGetKwargs('search_input', '')
		the_notification = tryGetKwargs("the_notification", '')

		assignments = dbORM.get_all("AssignmentAPRO")
		normal_assignment_list = []
		for x, y in assignments.items():
			if y['reg_number'] != u['reg_number']:
				normal_assignment_list.append(y)

		# print(len(assignment_list), len(search_result))

		normal_assignment_list = None if normal_assignment_list == [] else normal_assignment_list[::-1]

		if assignment_list == None and search_result == None:
			normal_assignment_list = normal_assignment_list
		elif assignment_list == None or search_result == None:	
			if assignment_list == None:	
				normal_assignment_list = None
			elif search_result == None:	
				normal_assignment_list = None
		else:
			normal_assignment_list = None if (len(assignment_list) > 0 or len(search_result) > 0) else normal_assignment_list

		print(">>>>>>>>>>>>>>>>>>>>>>", (assignment_list), (search_result))

		try:
			assignment_list = assignment_list[::-1]
		except:
			pass

		try:
			search_result = search_result[::-1]
		except:
			pass

		try:
			Notifications = dbORM.get_all("NotificationAPRO")
			my_notifications = []
			new_notifications = []
			for x, y in Notifications.items():
				if y['broadcast'] == "true":
					my_notifications.append(y)

				elif y['recipient_id'] == u['id']:
					my_notifications.append(y)

				if ((y['recipient_id'] == u['id']) and (y['status'] == 'delivered')) or y['broadcast'] == "true" :
					new_notifications.append(y)
		except KeyError as e:
			my_notifications = dbORM.find_all("NotificationAPRO", "recipient_id", u['id'])
			new_notifications = dbORM.find_all("NotificationAPRO", "status", "delivered")

		users = dbORM.get_all("UserAPRO")
		user_list = []
		for x, y in users.items():
			if y['tier'] != 'god':
				user_list.append(y)

			elif y['reg_number'] != u['reg_number']:
				user_list.append(y)

		return render_template("dashboard.html" if tryGetKwargs('admin_pass', None) == None else "admin-dashboard.html",
			CUser = u,		
			UserList = user_list,
			ImagePassError = checkImagePassError,
			
			AllAssignments = all_assignments[::-1],
			MyAssignments = my_assignments[::-1],
			AssignmentFilterTabs = ['All', 'Public', 'Private', 'Today', 'Done', 'Saved'], #AFT
			ActiveAFT_Tab = active_tab,
			AssignmentToView = assignment_to_view,

			ScreenID = screen_id,
			DashboardTabs = ['All', 'Your Level', f'Today - {u["level"]}L'],
			ActiveDSH_Tab = main_tab,
			FilterAssignmentList = assignment_list,# if (len(normal_assignment_list) == 0 and len(search_result) == 0) else None,

			SearchResults = search_result,# if (len(assignment_list) == 0 and len(normal_assignment_list) == 0) else None,
			SearchInput = search_input,

			NormalAssignmentList = normal_assignment_list,

			UserNotifications = my_notifications[::-1],
			NotificationCount = len(new_notifications),
			TheNotification = the_notification,

			DTK = dtk,
			ApprovedSubjectList = function_pool.return_approved_subjects(),
			LengthFunc = len,
			GetOppositeVisibility = function_pool.GetOppositeVisibility,
			ToJoin = function_pool.toJoin,
			RandomSearchText = function_pool.RandomSearchText,
			DeviceType = function_pool.detectDeviceType(kwargs['request']),
			WhichDevice = function_pool.which_device,
			NoneType = None,
			GetDBItem = function_pool.getDBItem,
			ToString = str,
        	DBORM = function_pool.dbORMJinja,
			ShortenText = function_pool.shorten_text,
			RoundFloat = round,
			CurrentDate = function_pool.getDateTime()[0],
			ToFloat = float,
			ToInt = int,
			RemoveAdmins = function_pool.removeAdmins,
			ReturnFaculty = function_pool.return_faculty,
			CurrencyExchange = function_pool.CurrencyExchange(),
			RandomID = id_generator.generateTID,
			PythonEval = function_pool.python_eval,
			ToFloatToInt = function_pool.floatToInt,
			Thousandify = function_pool.thousandify,
			getMIME = function_pool.get_mime_type,
			TimeDifference = function_pool.calcTimeDifference,
			CurrentTime = function_pool.getDateTime()[1],
			HTMLBreak_ = function_pool.HTMLBreak
		)
	else:
		return redirect(url_for("views.dashboard"))
	