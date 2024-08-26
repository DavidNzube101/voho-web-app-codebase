from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_from_directory, session, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename


# from datetime import datetime
from datetime import datetime, timedelta
import base64
import random
import imghdr
import json
import datetime as dt

from . import DateToolKit as dtk
from . import function_pool
from . import ScreenGoRoute
from . import id_generator

from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt

if dbORM == None:
    User, Notes = None, None
else:
    User, Assignment = dbORM.get_all("UserAPRO"), dbORM.get_all("AssignmentAPRO")




client_actions = Blueprint('client_actions', __name__)
ca = client_actions

@ca.route("/leave-lobby")
def leaveLobby():

    dbORM.update_entry(
        "UserAPRO", 
        f"{dbORM.find_one('UserAPRO', 'id', str(current_user.id))}", 
        encrypt.encrypter(str(
            {
                "waitlist": "launched"
            }
        )), 
        dnd=False
    )

    return redirect(url_for("views.dashboard"))

@ca.route('/finish-onboarding')
def finishOnboarding():
    u = dbORM.get_all("UserAPRO")
    numbers = []
    for x in range(100):
        numbers.append(x)

    return render_template("onboarding_stages.html", CUser=u[current_user.id], num_list=numbers)

@ca.route('/onboarding', methods=['POST'])
def onboardStage():
    u = dbORM.get_all("UserAPRO")

    def onb_func(data):
        try:
            dbORM.update_entry(
                "UserAPRO", 
                f"{dbORM.find_one('UserAPRO', 'id', str(current_user.id))}", 
                encrypt.encrypter(str(data)), 
                dnd=False
            )
            return "Success"
        except Exception as e:
            return f"Failed\n{e}"

    onboarding_steps = {
        "1": ["Registration", ""] ,
        "2": ["Phone Number Sumbit", "phone_number"] ,
        "3": ['AssignmentPro Hire Waitlist', 'waitlist_apro_hire']
    }
    user_onb_stage = u[current_user.id]['onboarding_stage']
    stage = request.form['current_stage']
    next_stage = f"{int(stage) + 1}"

    if onb_func(data={onboarding_steps[next_stage][1]: request.form['data']}) != "Success":
        print(onb_func(data={onboarding_steps[next_stage][1]: request.form['data']}))
    else:
        dbORM.update_entry(
            "UserAPRO", 
            f"{dbORM.find_one('UserAPRO', 'id', str(current_user.id))}", 
            encrypt.encrypter(str(
                {
                    "onboarding_stage": f"{next_stage}"
                }
            )), 
            dnd=False
        )

    flash("Finished setting up", category=['SUC', "Set up complete"])
    return redirect(url_for("views.dashboard"))

@ca.route("/create-assignment", methods=['POST'])
def createAssignment():
    u = dbORM.get_all("UserAPRO")[current_user.id]
    image = request.files['image']
    random_token = id_generator.generateTID()
    if image:
        _ = {
            'name': request.form['name'], 
            'description': request.form['description'], 
            'reg_number': u['reg_number'], 
            'image_raw': random_token, 
            'image_name': image.filename, 
            'price': "0.0", 
            'subject': request.form['subject'], 
            'level': u['level'], 
            'is_done': "no",
            "datestamp": f"{function_pool.getDateTime()[0]}",
            "timestamp": f"{function_pool.getDateTime()[1]}",
            "visibility": request.form['visibility'],
            "solution_count": "0"
        }
        dbORM.add_entry("AssignmentAPRO", encrypt.encrypter(str(_)))
        dbORM.update_entry(
            "AssignmentAPRO", 
            f"{dbORM.find_one('AssignmentAPRO', 'image_raw', random_token)}", 
            str(
                {
                    "image_raw": f"{function_pool.encode_image(image)}"
                }
            ), 
            dnd=True
        )
    else:
        _ = {
            'name': request.form['name'], 
            'description': request.form['description'], 
            'reg_number': u['reg_number'], 
            'image_raw': "", 
            'image_name': "APRO-Image", 
            'price': "0.0", 
            'subject': request.form['subject'], 
            'level': u['level'], 
            'is_done': "no",
            "datestamp": f"{function_pool.getDateTime()[0]}",
            "timestamp": f"{function_pool.getDateTime()[1]}",
            "visibility": request.form['visibility'],
            "solution_count": "0"
        }
        dbORM.add_entry("AssignmentAPRO", encrypt.encrypter(str(_)))

    # the_assignment = dbORM.get_all("AssignmentAPRO")[dbORM.find_one("AssignmentAPRO", "reg_number", u['reg_number'])]
    u = dbORM.get_all("UserAPRO")[current_user.id]
    _not = {
        'sender_id': dbORM.get_all("UserAPRO")[current_user.id]['id'],
        'recipient_id': u['id'],
        'title': f"Assignment & Solution count",
        'content': f"Hey {u['first_name']}, its David from Voho. We are just letting you know that you have used {len(dbORM.find_all('AssignmentAPRO', 'reg_number', u['reg_number']))}/20 assignment & solutions. The 20 mark limit is due to the fact that you are still on the basic plan. Upgrade now to any of the upper tiers and gain the access to post unlimited assignment & solutions.",
        'type': "official",
        "data": f"[1, 6]",
        'datestamp': f"{function_pool.getDateTime()[0]}",
        'timestamp': f"{function_pool.getDateTime()[1]}",
        'status': "delivered",
        "broadcast": "false"
    }
    dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_not)))

    flash(f"Created {request.form['name']}.", category=['SUC', 'Created assignment'])
    return redirect(url_for("views.dashboard"))

@ca.route("/dashboard/filter/<string:active_tab>")
def filterDashboardTab(active_tab):
    u = dbORM.get_all("UserAPRO")[current_user.id]
    def checkSource(data_list):
        if len(data_list) < 1:
            return data_list
        else:
            new_list = []
            for data in data_list:
                if data['reg_number'] != u['reg_number'] and data['visibility'] == "Public":
                    new_list.append(data)

            return new_list



    a_list = []
    if active_tab == "All":
        _ = dbORM.get_all("AssignmentAPRO")
        all_t_list = []
        for x, y in _.items():
            all_t_list.append(y)
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Your Level":
        all_t_list = dbORM.find_all("AssignmentAPRO", "level", u['level'])
        all_t_list = checkSource(all_t_list)

    elif active_tab == f"Today - {u['level']}L":
        all_t_list1 = dbORM.find_all("AssignmentAPRO", "datestamp", f"{function_pool.getDateTime()[0]}")
        all_t_list2 = dbORM.find_all("AssignmentAPRO", "level", u['level'])
        all_t_list3 = [element for element in all_t_list1 if element in all_t_list2]
        all_t_list = checkSource(all_t_list3)

    # elif active_tab == "Today":
    #     all_t_list = dbORM.find_all("AssignmentAPRO", "datestamp", f"{function_pool.getDateTime()[0]}")
    #     all_t_list = checkSource(all_t_list)

    a_list = all_t_list
    # print(">>>>>>>>>>>>>>>>>>>>>>", (a_list), active_tab)

    return ScreenGoRoute.go_to("1", request=request, main_tab=active_tab, assignment_list=a_list)

@ca.route("/search", methods=['POST'])
def searchItem():
    def refine_input(text):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        numbers = [100, 200, 300, 400, 500]

        if ('today' in text.lower()) or ('yesterday' in text.lower()):
            what = 'date'
            if text.lower() == 'today':
                return [what, f"{function_pool.getDateTime()[0]}"]
            elif text.lower() == 'yesterday':
                return [what, f"{function_pool.getDateTime()[0]}"]

        for n in numbers:
            if str(n) in text:
                what = 'level'
                return [what, str(n)]

        try:
            if int(text) in numbers:
                what = 'level'
                return [what, text]
            else:
                what = 'none'
                return [what, ""]
        except:
            pass

        for l in text:
            if l in letters:
                what = 'subject'
                return [what, text.upper()]
            else:
                what = 'none'
                return [what, ""]

    search_input = request.form['search_input']

    refined_search_input = refine_input(search_input)
    if refined_search_input[0] == 'subject':
        result = dbORM.find_all("AssignmentAPRO", "subject", refined_search_input[1])
    elif refined_search_input[0] == 'level':
        result = dbORM.find_all("AssignmentAPRO", "level", refined_search_input[1])
    elif refined_search_input[0] == 'date':
        result = dbORM.find_all("AssignmentAPRO", "datestamp", refined_search_input[1])
    else:
        result = []

    print("search result>>>>>>>>>>>>>>>>>>>>>>>>>", search_input, refined_search_input, result if result == [] else [], len(result))

    return ScreenGoRoute.go_to("1", request=request, search_result=result, main_tab="Search", search_input=search_input)

@ca.route("/search/query/<string:the_query>")
def searchQuery(the_query):
    def refine_input(text):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        numbers = [100, 200, 300, 400, 500]

        if ('today' in text.lower()) or ('yesterday' in text.lower()):
            what = 'date'
            if text.lower() == 'today':
                return [what, f"{function_pool.getDateTime()[0]}"]
            elif text.lower() == 'yesterday':
                return [what, f"{function_pool.getDateTime()[0]}"]

        for n in numbers:
            if str(n) in text:
                what = 'level'
                return [what, str(n)]

        try:
            if int(text) in numbers:
                what = 'level'
                return [what, text]
            else:
                what = 'none'
                return [what, ""]
        except:
            pass

        for l in text:
            if l in letters:
                what = 'subject'
                return [what, text.upper()]
            else:
                what = 'none'
                return [what, ""]

    search_input = the_query

    refined_search_input = refine_input(search_input)
    if refined_search_input[0] == 'subject':
        result = dbORM.find_all("AssignmentAPRO", "subject", refined_search_input[1])
    elif refined_search_input[0] == 'level':
        result = dbORM.find_all("AssignmentAPRO", "level", refined_search_input[1])
    elif refined_search_input[0] == 'date':
        result = dbORM.find_all("AssignmentAPRO", "datestamp", refined_search_input[1])
    else:
        result = []

    print("search result>>>>>>>>>>>>>>>>>>>>>>>>>", search_input, refined_search_input, result if result == [] else [], len(result))

    return ScreenGoRoute.go_to("1", request=request, search_result=result, main_tab="Search", search_input=search_input)

@ca.route("/filter/<string:active_tab>")
def filterToTab(active_tab):
    u = dbORM.get_all("UserAPRO")[current_user.id]
    def checkSource(data_list):
        if len(data_list) < 1:
            return data_list
        else:
            new_list = []
            for data in data_list:
                if data['reg_number'] == u['reg_number']:
                    new_list.append(data)

            return new_list



    a_list = []
    if active_tab == "All":
        all_t_list = dbORM.find_all("AssignmentAPRO", "reg_number", u['reg_number'])

    elif active_tab == "Public":
        all_t_list = dbORM.find_all("AssignmentAPRO", "visibility", "Public")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Private":
        all_t_list = dbORM.find_all("AssignmentAPRO", "visibility", "Private")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Today":
        all_t_list = dbORM.find_all("AssignmentAPRO", "datestamp", f"{function_pool.getDateTime()[0]}")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Done":
        all_t_list = dbORM.find_all("AssignmentAPRO", "is_done", "yes")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Saved":
        saved_assignments = dbORM.get_all("SavedAssignmentAPRO")
        all_t_list = []
        for x, y in saved_assignments.items():
            if y['reg_number'] == u['reg_number']:
                all_t_list.append(dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", y["assignment_id"])}'])
        # all_t_list = dbORM.find_all("AssignmentAPRO", "reg_number", the_assignment['reg_number'])
        # all_t_list = checkSource(all_t_list)

    a_list = all_t_list
    print(">>>>>>>>>>>>>>>>>>>>>>", len(a_list))

    return ScreenGoRoute.go_to("3", request=request, active_tab=active_tab, the_assignment=a_list)

@ca.route("/view-assignment/<string:assignment_id>")
def ViewAssignment(assignment_id):
    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']

    return ScreenGoRoute.go_to("4", request=request, TheAssignmentToView=the_assignment)

@ca.route("/edit-assignment/<string:what>/<string:which>/<string:assignment_id>")
def editAssignment(what, which, assignment_id):
    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']

    dbORM.update_entry(
        "AssignmentAPRO", 
        f"{dbORM.find_one('AssignmentAPRO', 'id', assignment_id)}", 
        encrypt.encrypter(str(
            {
                what: which
            }
        )), 
        dnd=False
    )
    flash(f"Changed visibility to {which}. Only you can and the people you hire can see this assignment." if which == "Private" else f"Changed visibility to {which}. Everyone can see this assignment.", category=["SUC", "Visibility Updated"])

    return ScreenGoRoute.go_to("4", request=request, TheAssignmentToView=the_assignment)

@ca.route("/assignment/thread/<string:assignment_id>")
def renderAddSolution(assignment_id):
    u = dbORM.get_all("UserAPRO")[current_user.id]
    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']
    solutions = dbORM.find_all("SolutionAPRO", "assignment_id", assignment_id)

    return render_template("AssignmentThread.html", 
        Assignment=the_assignment, 
        CUser=u, 
        getMIME = function_pool.get_mime_type, 
        DTK=dtk,
        GetOppositeVisibility = function_pool.GetOppositeVisibility,
        Solutions = solutions,
        DBORM = function_pool.dbORMJinja,
        GetReviewCount = function_pool.getReviewCount,
        ShortenText = function_pool.shorten_text)

@ca.route("/assignment/thread/<string:assignment_id>/solution/<string:solution_id>")
def renderSolutionThread(assignment_id, solution_id):
    u = dbORM.get_all("UserAPRO")[current_user.id]
    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']
    solutions = dbORM.find_all("SolutionAPRO", "id", solution_id)

    return render_template("SolutionThread.html", 
        Assignment=the_assignment, 
        CUser=u, 
        getMIME = function_pool.get_mime_type, 
        DTK=dtk,
        GetOppositeVisibility = function_pool.GetOppositeVisibility,
        Solutions = solutions,
        DBORM = function_pool.dbORMJinja,
        GetReviewCount = function_pool.getReviewCount,
        ShortenText = function_pool.shorten_text)

@ca.route("/add-solution", methods=['POST'])
def addSolution():
    assignment_id = request.form['assignment_id']
    user_id = request.form['user_id']
    # print(">>>>>>>>>>>>>>>>>>>>>>>", request.form['assignment_id'], request.form['user_id'])
    u = dbORM.get_all("UserAPRO")[user_id]
    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']
    solutions = dbORM.find_all("SolutionAPRO", "assignment_id", assignment_id)
    session_id = id_generator.generateTID()
    try:
        image = request.files['image']
    except:
        image = request.form['image']

    if image != "null":
        _ = {
            'name': f"{the_assignment['name']} Solution",
            'assignment_id': assignment_id,
            'provider': u['reg_number'],
            'content': request.form['content'].replace("'", ""),
            'image_name': f"{image.filename}",
            'image_raw': f"{session_id}",
            'review': "[]",
            'datestamp': f"{function_pool.getDateTime()[0]}",
            'timestamp': f"{function_pool.getDateTime()[1]}"
        }
        dbORM.add_entry("SolutionAPRO", encrypt.encrypter(str(_)))
        dbORM.update_entry(
            "SolutionAPRO", 
            f"{dbORM.find_one('SolutionAPRO', 'image_raw', session_id)}", 
            str(
                {
                    "image_raw": f"{function_pool.encode_image(image)}"
                }
            ), 
            dnd=True
        )
    else:
        _ = {
            'name': f"{the_assignment['name']} Solution",
            'assignment_id': assignment_id,
            'provider': u['reg_number'],
            'content': request.form['content'].replace("'", ""),
            'image_name': "APRO-Image",
            'image_raw': "",
            'review': "[]",
            'datestamp': f"{function_pool.getDateTime()[0]}",
            'timestamp': f"{function_pool.getDateTime()[1]}"
        }
        dbORM.add_entry("SolutionAPRO", encrypt.encrypter(str(_)))


    # flash("Added your solution to the assignment thread.", category=['SUC', 'Added Solution'])

    dbORM.update_entry(
        "AssignmentAPRO", 
        f"{dbORM.find_one('AssignmentAPRO', 'id', assignment_id)}", 
        encrypt.encrypter(str(
            {
                "solution_count": f"{int(the_assignment['solution_count']) + 1}"
            }
        )), 
        dnd=False
    )
    rec_ = dbORM.get_all("UserAPRO")[f'{dbORM.find_one("UserAPRO", "reg_number", the_assignment["reg_number"])}']
    _not = {
        'sender_id': dbORM.get_all("UserAPRO")[current_user.id]['id'],
        'recipient_id': rec_['id'],
        'title': f"Assignment Solution Provided by {u['first_name']}",
        'content': f"Hey {rec_['first_name']}, its {u['first_name']}. I just added a solution to your question, check it out.",
        'type': "answer_question",
        "data": f"{assignment_id}",
        'datestamp': f"{function_pool.getDateTime()[0]}",
        'timestamp': f"{function_pool.getDateTime()[1]}",
        'status': "delivered",
        "broadcast": "false"
   }
    dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_not)))

    return render_template("AssignmentThread.html", 
        Assignment=the_assignment, 
        CUser=u, 
        getMIME = function_pool.get_mime_type, 
        DTK=dtk,
        GetOppositeVisibility = function_pool.GetOppositeVisibility,
        Solutions = solutions,
        DBORM = function_pool.dbORMJinja,
        GetReviewCount = function_pool.getReviewCount,
        ShortenText = function_pool.shorten_text)

@ca.route('/add-review', methods=['POST'])
def addReview():
    u = dbORM.get_all("UserAPRO")[current_user.id]
    the_solution = dbORM.get_all("SolutionAPRO")[f'{dbORM.find_one("SolutionAPRO", "id", request.form["solution_id"])}']
    current_reviews = eval(the_solution['review'])

    reviewers = []
    for x in current_reviews:
        for y, z in x.items():
            reviewers.append(y)

    if int(u['id']) in reviewers:
        pass
        return "Reviewed already"
    else:
        if u['reg_number'] == the_solution['provider']:
            return "Reviewed yourself"
        # [{7: [1, 0]}]
        else:
            if request.form['what'] == "good":
                new_review = {int(u['id']): [1, 0]}
            else:
                new_review = {int(u['id']): [0, 1]}

            current_reviews.append(new_review)
            dbORM.update_entry(
                "SolutionAPRO", 
                f"{dbORM.find_one('SolutionAPRO', 'id', request.form['solution_id'])}", 
                encrypt.encrypter(str(
                    {
                        "review": f"{current_reviews}"
                    }
                )), 
                dnd=False
            )

            the_assignment = dbORM.get_all("SolutionAPRO")[f'{dbORM.find_one("SolutionAPRO", "provider", the_solution["provider"])}']
            rec_ = dbORM.get_all("UserAPRO")[f'{dbORM.find_one("UserAPRO", "reg_number", the_assignment["provider"])}']
            u = dbORM.get_all("UserAPRO")[current_user.id]
            _not = {
                'sender_id': dbORM.get_all("UserAPRO")[current_user.id]['id'],
                'recipient_id': rec_['id'],
                'title': f"Solution Review",
                'content': f"Your solution has gotten a {'positive' if request.form['what'] == 'good' else 'negative'} review.",
                'type': "solution_review",
                "data": f"{the_assignment['id']}",
                'datestamp': f"{function_pool.getDateTime()[0]}",
                'timestamp': f"{function_pool.getDateTime()[1]}",
                'status': "delivered",
                "broadcast": "false"
            }
            dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_not)))
        

            return "Success"

@ca.route("/profile/<string:reg_number>")
def renderProfilePage(reg_number):
    
    the_u = dbORM.get_all("UserAPRO")[f'{dbORM.find_one("UserAPRO", "reg_number", reg_number)}']

    def checkSource(data_list):
        if len(data_list) < 1:
            return data_list
        else:
            new_list = []
            for data in data_list:
                if data['reg_number'] == the_u['reg_number'] and data['visibility'] == "Public":
                    new_list.append(data)

            return new_list

    all_t_list = dbORM.find_all("AssignmentAPRO", "reg_number", the_u['reg_number'])

    rec_ = the_u
    u = dbORM.get_all("UserAPRO")[current_user.id]
    _not = {
        'sender_id': dbORM.get_all("UserAPRO")[current_user.id]['id'],
        'recipient_id': rec_['id'],
        'title': f"Profile View",
        'content': f"{u['first_name']} just viewed your profile.",
        'type': "engagement",
        "data": f"{u['id']}",
        'datestamp': f"{function_pool.getDateTime()[0]}",
        'timestamp': f"{function_pool.getDateTime()[1]}",
        'status': "delivered",
        "broadcast": "false"
    }
    dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_not)))

    return render_template("ProfilePage.html",
        TheAssignments = checkSource(all_t_list)[::-1],
        CUser = dbORM.get_all("UserAPRO")[current_user.id],
        ReturnFaculty = function_pool.return_faculty,
        AssignmentFilterTabs = ['All', 'Public', 'Private', 'Today', 'Done', 'Saved'], #AFT
        TheUser = the_u,
        ActiveAFT_Tab = "All",
        DTK = dtk
        )

@ca.route("/profile/<string:reg_number>/filter/<string:tab>")
def filterToTab_Profile(reg_number, tab):
    active_tab = tab

    the_u = dbORM.get_all("UserAPRO")[f'{dbORM.find_one("UserAPRO", "reg_number", reg_number)}']
    def checkSource(data_list):
        if len(data_list) < 1:
            return data_list
        else:
            new_list = []
            for data in data_list:
                if data['reg_number'] == the_u['reg_number'] and data['visibility'] == "Public":
                    new_list.append(data)

            return new_list

    a_list = []
    if active_tab == "All":
        all_t_list = dbORM.find_all("AssignmentAPRO", "reg_number", the_u['reg_number'])
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Public":
        all_t_list = dbORM.find_all("AssignmentAPRO", "visibility", "Public")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Private":
        all_t_list = []

    elif active_tab == "Today":
        all_t_list = dbORM.find_all("AssignmentAPRO", "datestamp", f"{function_pool.getDateTime()[0]}")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Done":
        all_t_list = dbORM.find_all("AssignmentAPRO", "is_done", "yes")
        all_t_list = checkSource(all_t_list)

    elif active_tab == "Saved":
        all_t_list = []
        # all_t_list = checkSource(all_t_list)

    a_list = all_t_list

    return render_template("ProfilePage.html",
        TheAssignments = a_list[::-1],
        CUser = dbORM.get_all("UserAPRO")[current_user.id],
        ReturnFaculty = function_pool.return_faculty,
        AssignmentFilterTabs = ['All', 'Public', 'Private', 'Today', 'Done', 'Saved'], #AFT
        TheUser = the_u,
        ActiveAFT_Tab = tab,
        DTK = dtk
        )

@ca.route("/hire/<string:assignment_id>")
def hireSomeone(assignment_id):



    return ScreenGoRoute.go_to("5", request=request)

@ca.route("/add-saved-assignment/<string:assignment_id>")
def addSavedAssignment(assignment_id):
    _ = {
        'assignment_id': f"{assignment_id}",
        'datestamp': f"{function_pool.getDateTime()[0]}",
        'timestamp': f"{function_pool.getDateTime()[1]}",
        'reg_number': f"{dbORM.get_all('UserAPRO')[current_user.id]['reg_number']}"
   }
    dbORM.add_entry("SavedAssignmentAPRO", encrypt.encrypter(str(_)))

    the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']
    rec_ = dbORM.get_all("UserAPRO")[f'{dbORM.find_one("UserAPRO", "reg_number", the_assignment["reg_number"])}']
    u = dbORM.get_all("UserAPRO")[current_user.id]
    _not = {
        'sender_id': dbORM.get_all("UserAPRO")[current_user.id]['id'],
        'recipient_id': rec_['id'],
        'title': f"Assignment Engagement",
        'content': f"{u['first_name']} saved your assignment.",
        'type': "engagement",
        "data": f"{u['id']}",
        'datestamp': f"{function_pool.getDateTime()[0]}",
        'timestamp': f"{function_pool.getDateTime()[1]}",
        'status': "delivered",
        "broadcast": "false"
    }
    dbORM.add_entry("NotificationAPRO", encrypt.encrypter(str(_not)))


    flash("Saved Assignment. To view, go to 'Profile' and among the filter options, choose Saved.", category=['SUC', 'Saved successfully'])
    return ScreenGoRoute.go_to("1", request=request, _redirect=True)

@ca.route("/remove-saved-assignment/<string:assignment_id>")
def removeSavedAssignment(assignment_id):
    l1 = dbORM.find_all("SavedAssignmentAPRO", "reg_number", dbORM.get_all("UserAPRO")[current_user.id]['reg_number'])
    l2 = dbORM.find_all("SavedAssignmentAPRO", "assignment_id", assignment_id)
    l3 = [element for element in l1 if element in l2]
    print("l2l3l1>>>>>>>>>>>>>>>>>>>>", l3, type(l3))
    try:
        dbORM.delete_entry("SavedAssignmentAPRO", l3[0]['id'])
        flash("Removed Assignment from Saved List.", category=['SUC', 'Unsaved successfully'])
        return ScreenGoRoute.go_to("1", request=request, _redirect=True)
    except Exception as e:


        flash(f"Error occured while unsaving assignment. Try again later.", category=['EOC', 'Unsaved unsuccessful'])
        return ScreenGoRoute.go_to("1", request=request, _redirect=True)

@ca.route('/open-notification/<string:notification_id>')
def showNotificatio(notification_id):
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

        return ScreenGoRoute.go_to("7", request=request)

@ca.route("/delete-assignment/<string:assignment_id>")
def deleteAssignment(assignment_id):
    try:
        the_assignment = dbORM.get_all("AssignmentAPRO")[f'{dbORM.find_one("AssignmentAPRO", "id", assignment_id)}']
        dbORM.delete_entry("AssignmentAPRO", dbORM.find_one("AssignmentAPRO", "id", assignment_id))

        flash(f"Deleted {the_assignment['name']}", category=['SUC', 'Deleted successfully'])
        return ScreenGoRoute.go_to("3", request=request)
    except:
        flash(f"Error occured while deleting assignment. Try again later.", category=['EOC', 'Unable to delete'])

        return ScreenGoRoute.go_to("3", request=request)

@ca.route("/delete-notification/<string:notification_id>")
def deleteNotification(notification_id):
    try:
        the_notification = dbORM.get_all("NotificationAPRO")[f'{dbORM.find_one("NotificationAPRO", "id", notification_id)}']
        if the_notification['broadcast'] == "false":
            dbORM.delete_entry("NotificationAPRO", dbORM.find_one("NotificationAPRO", "id", notification_id))

            flash(f"Deleted {the_notification['title']}", category=['SUC', 'Deleted successfully'])
            return ScreenGoRoute.go_to("3", request=request)
        else:
            flash(f"You can not delete this broadcast.", category=['AAW', 'Halted Action'])
            return ScreenGoRoute.go_to("3", request=request)
    except Exception as e:
        flash(f"Error occured while deleting notification. Try again later.\n{e}", category=['EOC', 'Unable to delete'])

        return ScreenGoRoute.go_to("7", request=request, _redirect=True)