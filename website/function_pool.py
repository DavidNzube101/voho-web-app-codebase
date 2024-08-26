# from .db import dbORM
from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_from_directory, session, jsonify
import base64
import magic
import imghdr
import datetime as dt
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from . import DateToolKit as dtk
import math as Math
import random
from . import id_generator
# from . import encrypt

from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt


def encode_image(file_storage):
    image_data = file_storage.read()
    encoded_string = base64.b64encode(image_data).decode("utf-8")

    return encoded_string

def calcTimeDifference(dpt, ct):
	return [int(x) for x in ("[" + str(datetime.strptime(dpt, "%H:%M") - datetime.strptime(ct, "%H:%M:%S")).replace(":", ", ").replace("-1 day, ", "") + "]").strip("[]").split(", ")]

def getDBItem(model, column, value, f=False):
	
	try:
		if f == True:
			i = dbORM.find_one(model, column, value)
		else:
			i = dbORM.get_all(model)[f'{dbORM.find_one(model, column, value)}']
	except Exception as e:
		i = {}

	return i

def dbORMJinja(what, table, column, value):

	try:
		if what == "get_all":
			return dbORM.get_all(table)[f'{dbORM.find_one(table, column, value)}']

		elif what == "find_all":
			return dbORM.find_all(table, column, value)

		else:
			return {}
	except KeyError as e:
		return None


def removeAdmins(d):
	new_list = []
	for _d in d:
		if _d['tier'] != 'god':
			new_list.append(_d)
			
	return new_list

def isAdmin(user_id):
	if dbORM.get_all("UserAPRO")[user_id]['tier'] == 'god':
		return True
	else:
		return False

def getReviewCount(solution_id):

	the_solution = dbORM.get_all("SolutionAPRO")[f'{dbORM.find_one("SolutionAPRO", "id", solution_id)}']
	review_data = eval(the_solution['review'])
	bad_count = 0
	good_count = 0
	if str(type(review_data)) == "<class 'list'>":
		for data in review_data:
			for x, y in data.items():

				if y[0] == 1:
					good_count = good_count + 1
				if y[1] == 1:
					bad_count = bad_count + 1

	return [good_count, bad_count]

def shorten_text(text, max_length):

	words = text.split()
	if len(words) > max_length:
		return " ".join(words[:max_length]) + "..."
	else:
		return text

def RandomSearchText():
	texts = ['today assignment', '100 level', 'gst103']
	def returnText():
		return random.choice(texts)

	text1 = returnText()
	text2 = returnText()

	return [text1, text2 if text1 != text2 else returnText()]

def python_eval(exp):

	try:
		return eval(exp)
	except:
		return []

def eddie():
	return "ds"

def loopAppendAndReverse(a, b):
	try:
		for k, v in a.items():
			b.append(v)
		return b[::-1]
	except Exception as e:
		return f"Error occured\nError: {e}"

def toJoin(i, j):
	return f"{i}{j}"

def thousandify(amount):
	amount = "{:,}".format(float(amount))
	return f"{amount}"

def is_test():
	return "True"

def floatToInt(n):
	return f"{Math.ceil(float(n))}"

def getDateTime():
	# Getting Date-Time Info
	current_date = dt.date.today()
	current_time = datetime.now().strftime("%H:%M:%S")

	# Date Format: "YYYY-MM-DD"
	formatted_date = current_date.strftime("%Y-%m-%d")
	date = formatted_date
	time = current_time

	return [date, time]


def HTMLBreak(n):
	breaks = ""

	for x in range(int(n)):
		breaks = breaks + "\n<br>"	

	return breaks

def getOppositeTheme(theme):
	if theme == 'light':
		return 'dark'
	else:
		return 'light'

def oppositeCurrency(currency):
	return "NGN" if currency == "$" else "NGN"

def CurrencyExchange():
	v1 = float(f"0.{dtk.split_date(getDateTime()[0])['Day']}") # initial float
	v2 = float(f"0.{dtk.split_date(getDateTime()[0])['Month']}") # error margin

	return round(v1 * v2, 2)

def get_mime_type(data):
    try:
    	decoded_data = base64.b64decode(data)
    	mime_type = magic.from_buffer(decoded_data, mime=True)
    	return mime_type if mime_type else ""
    except:
	    decoded_data = base64.b64decode(data)
	    image_type = imghdr.what(None, h=decoded_data)
	    return f'image/{image_type}' if image_type else ''
    

def checkImagePassError(image_raw):
	try:
		rr = f"data:{getMIME(image_raw)};base64,{image_raw}"
		return "false"
	except:
		return "true"

def return_approved_subjects():
	subject_codes = []
	subjects = {
		"MTH101": "Mathematics 100 Level",
		"GST103": "Philosophy 100 Level",
		"IFT203": "Information Technology 200 Level"
	}
	for x, y in subjects.items():
		subject_codes.append(x)

	return subject_codes

def GetOppositeVisibility(visibility):
	if visibility == "Private":
		return "Public"
	else:
		return "Private"

def return_faculty(faculty_code):

	faculty_def = {
		"SAAT": "School of Agriculture and Agricultural Technology (SAAT)",
		"SBMS": "School of Basic Medical Science (SBMS)",
		"SOBS": "School of Biological Science (SOBS)",
		"SEET": "School of Engineering and Engineering Technology (SEET)",
		"SESET": "School of Electrical Systems and Engineering Technology (SESET)",
		"SOHT": "School of Health Technology (SOHT)",
		"SICT": "School of Information and Communication Technology (SICT)",
		"SLIT": "School of Logistics and Innovation Technology (SLIT)",
		"SOPS": "School of Physical Science (SOPS)",
		"SOES": "School of Environmental Sciences (SOES)",
		"CMHS": "College of Medicine and Health Sciences (CMHS)",
		"SMAT": "School of Management Technology (SMAT)"
	}

	return faculty_def[faculty_code]

def detectDeviceType(theRequest):
	user_agent = theRequest.user_agent.string.lower()

	if 'android' in user_agent:
		device_type = 'Android'

	elif "iphone" in user_agent:
		device_type = 'iPhone'

	else:
		device_type = 'Desktop'

	return device_type

def which_device(dev_code):
	try:
		if dev_code == "ADR":
			return "Android"
		elif dev_code == "IOS":
			return "iPhone"
		elif dev_code == "DEK":
			return "Desktop"
		else:
			return "JustShow"
	except:
		return "error"

def calculate_net_value(_list):
	single_value = []
	single = []
	for j in _list:
		single.append(j)

	try:
		single.remove({})
	except:
		pass


	for k in single:
		single_value.append(float(k['wallet_balance']))

	# print(single_value)

	return sum(single_value)