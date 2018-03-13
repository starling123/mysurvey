import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import database as db
import json
import admin
from util import render
#----------------------------------------------------------------------------
def get_template(type):
    type = type.strip()
    if type == "1":
        return "select_one.html"
    if type == "M":
        return "select_more.html"
    if type == "START":
        return "start_survey.html"
    if type == "END":
        return "end_survey.html"
    if type == "SECTION":
        return "section_start.html"
    if type == "O":
        return "open_question.html"
    if type == "JN":
        return "yesno_question.html"

#----------------------------------------------------------------------------
def render_survey(id, survey_id=0):
    # check if the id is a valid id if invite only
    # if there's no session with this id create it
    try:
        if survey_id != 0:
            db.create_session(id, survey_id)
    except:
        pass

    # get the session
    try:
        session = db.get_session(id)
    except:
        return render("/templates", "error.html", errormessage="Ongeldige toegangscode")

    # load the current question
    question = db.get_question(session["survey_id"], session["question_ordernumber"])

    # get options if needed
    options = {}
    if question["type"] in {"1","M"}:
        options = db.get_options(question["id"])

    # get the template for the question type
    template = get_template(question["type"])
    # load response of question if any
    response = db.get_response(id, question["id"])
    if question["type"] == "M":
        if response != None and len(response) > 0:
            response = map(int, response.split(","))
        else:
            response = []
    # render question
    return render("/templates", template, session_id=id,question=question, options=options, response=response)
#----------------------------------------------------------------------------
def test_question(question_id):
     # load the current question
    question = db.query("SELECT * FROM question WHERE id = %(question_id)s", {'question_id':question_id})[0]

    # get options if needed
    options = {}
    if question["type"] in {"1","M"}:
        options = db.get_options(question["id"])

    # get the template for the question type
    template = get_template(question["type"])
    # load response of question if any
    response = None
    if question["type"] == "M":
        response = []
    # render question
    return render("/templates", template, session_id=id,question=question, options=options, response=response)

#----------------------------------------------------------------------------
def check_condition(session_id):
    session = db.get_session(session_id)
 #   question_id = session["question_id"]
    # load the current question
    question = db.get_question(session["survey_id"], session["question_ordernumber"])
    # evaluate condition if present
    if question["condition_question_id"] != None:
        print(question["condition_expression"])
        # get the response
        response = db.get_response(session["id"], question["condition_question_id"])
        if response != None:
            print response
            condition = question["condition_expression"].format(response = response)
            print condition, "[", response, "]"
            result = eval(condition)
            print "conditie: ", result
            return result
    return True
#----------------------------------------------------------------------------
def process_response(**kwargs):
    print json.dumps(kwargs)
    # save response
    session = db.get_session(kwargs["session_id"])
    question = db.get_question(session["survey_id"], session["question_ordernumber"])
    question_id = question["id"]
    response = ""
    if str(question_id) in kwargs:
        response = kwargs[str(question_id)]

    if question["type"] in {"1", "M", "O", "JN"}:
        if question["type"] == "M":
            response = ",".join(response)
        db.save_response(session["id"], question_id, response)

    if "next" in kwargs:
        c = db.next_question(kwargs["session_id"])
        print "wat is c?", c
        while c and not check_condition(session["id"]):
           c = db.next_question(kwargs["session_id"]) 
    if "back" in kwargs:
        c = db.prev_question(kwargs["session_id"])
        while c and not check_condition(session["id"]):
           c = db.prev_question(kwargs["session_id"]) 
    return render_survey(kwargs["session_id"])

#----------------------------------------------------------------------------
def report(session_id):
    data = db.get_question_responses(session_id)
    return render("/templates","report.html", data=data)
     
#----------------------------------------------------------------------------
class MySurvey(object):

#----------------------------------------------------------------------------
    @cherrypy.expose
    def index(self):
        return admin.surveys()
#----------------------------------------------------------------------------
    @cherrypy.expose
    def start_survey(self, id, survey_id):
        return render_survey(id, survey_id)
#----------------------------------------------------------------------------
    @cherrypy.expose
    def survey(self, id):
        return render_survey(id)
#----------------------------------------------------------------------------
    @cherrypy.expose
    def process_response(self, **kwargs):
        return process_response(**kwargs)
#----------------------------------------------------------------------------
    @cherrypy.expose
    def report(self, session_id):
        return report(session_id)
#----------------------------------------------------------------------------
    @cherrypy.expose
    def test_question(self, question_id):
        return test_question(question_id)

#----------------------------------------------------------------------------
    @cherrypy.expose
    def admin(self, command, **kwargs):
        if command == "SURVEYS":
            return admin.surveys()
        if command == "SURVEY":
            return admin.survey(kwargs["id"])
        if command == "NEW_SURVEY":
            return admin.create_survey()
        if command == "DELETE_SURVEY":
            return admin.delete_survey(kwargs["id"])
        if command == "SAVE_SURVEY":
            return admin.save_survey(kwargs["id"], kwargs["name"], kwargs["description"])

        if command == "SURVEY_QUESTIONS":
            return admin.survey_questions(kwargs["survey_id"])
        if command == "SURVEY_PARTICIPANTS":
            return admin.survey_participants(kwargs["survey_id"])
        if command == "QUESTION":
            return admin.question(kwargs["id"])
        if command == "NEW_QUESTION":
            return admin.create_question(str(kwargs["survey_id"]))
        if command == "SAVE_QUESTION":
            return admin.save_question(**kwargs)
        if command == "DELETE_QUESTION":
            return admin.delete_question(kwargs["survey_id"], kwargs["id"])
        if command == "UP_QUESTION":
            return admin.up_question(kwargs["question_id"], kwargs["ordernumber"], kwargs["survey_id"])
        if command == "DOWN_QUESTION":
            return admin.down_question(kwargs["question_id"], kwargs["ordernumber"], kwargs["survey_id"])
        
        if command == "QUESTION_OPTIONS":
            return admin.question_options(kwargs["id"])
        if command == "ADD_OPTION":
            return admin.add_option(kwargs["id"])
        if command == "DELETE_OPTION":
            return admin.delete_option(kwargs["option_id"], kwargs["question_id"])
        if command == "UPDATE_OPTIONS":
            return admin.update_options(**kwargs)
        if command == "UP_OPTION":
            return admin.up_option(kwargs["option_id"], kwargs["ordernumber"], kwargs["question_id"])
        if command == "DOWN_OPTION":
            return admin.down_option(kwargs["option_id"], kwargs["ordernumber"], kwargs["question_id"])

        if command == "PARTICIPANTS":
            return admin.participants()
        if command == "NEW_PARTICIPANT":
            return admin.create_participant()
        if command == "UPDATE_PARTICIPANTS":
            return admin.update_participants(**kwargs)
        if command == "DELETE_PARTICIPANT":
            return admin.delete_participant(kwargs["id"])
        if command == "INVITE":
            return admin.invite(kwargs["survey_id"], kwargs["invitees"])
            
#----------------------------------------------------------------------------
if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(MySurvey())
