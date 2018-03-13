import database as db
import json
from uuid import uuid4
import smtplib
from util import render
# Import the email modules we'll need
from email.mime.text import MIMEText

SMTP_HOST = "send.one.com:25"
SENDER = "website@silogemeente.nl"
SMTP_PASSWORD = "Pk__ZVA-fu-iJSNHg2"

#----------------------------------------------------------------------------
def surveys():
    surveys = db.query("SELECT * FROM survey")
    return render("/admin","surveys.html", surveys=surveys)
#----------------------------------------------------------------------------
def survey(id):
    stmt = "SELECT * FROM survey WHERE id = {id}".format(id=id)
    survey = db.query(stmt)[0]
    return render("/admin","survey.html", survey=survey)
#----------------------------------------------------------------------------
def delete_survey(survey_id):
    stmt = "delete from survey where id = {survey_id}".format(survey_id = survey_id)
    db.execute(stmt)
#     stmt = "delete from question where survey_id = {survey_id}".format(survey_id = survey_id)
#     db.execute(stmt)
#     stmt = "delete from option where survey_id = {survey_id}".format(survey_id = survey_id)
#     db.execute(stmt)
    return surveys()
#----------------------------------------------------------------------------
def create_survey(name="", description=""):
    stmt = "insert into survey (name, description) values (%(name)s, %(description)s)"
    new_id = db.update(stmt, {'name':name, 'description':description})
    return survey(new_id)
#----------------------------------------------------------------------------
def survey_questions(id):
    stmt = "SELECT * FROM survey WHERE id = {id}".format(id=id)
    survey = db.query(stmt)[0]
    stmt = "select * from question where survey_id = %(survey_id)s order by ordernumber"
    questions = db.query(stmt, {'survey_id':id})
    return render("/admin","survey_questions.html", survey=survey, questions = questions)
#----------------------------------------------------------------------------
def survey_participants(id):
    survey = db.query("SELECT * FROM survey WHERE id = %(id)s", {'id':id})[0]
    participants = db.query("SELECT * FROM participant p "\
        "left join survey_participant sp on (p.id = sp.participant_id and sp.survey_id = %(survey_id)s) order by sp.survey_id",
        {'survey_id':id})
    return render("/admin","survey_participants.html", survey=survey, participants = participants)
#----------------------------------------------------------------------------
def save_survey(id, name, description):
    stmt = "UPDATE survey SET name = %(name)s, description = %(description)s WHERE id = %(id)s"
    db.update(stmt, {'name':name, 'description':description, 'id':int(id)})
    return survey(id)
#----------------------------------------------------------------------------
def question(id):
    stmt = "SELECT * FROM question WHERE id = %(id)s"
    question = db.query(stmt, {'id':id})[0]
    return render("/admin","question.html", question=question)
#----------------------------------------------------------------------------
def create_question(survey_id):
    #stmt = "INSERT INTO question (survey_id) values (%(survey_id)s)"
    stmt = "INSERT INTO question (survey_id, ordernumber) SELECT %(survey_id)s as survey_id, "\
        "coalesce(max(ordernumber),0)+1 as ordernumber FROM question WHERE survey_id = %(survey_id)s"
    new_id = db.update(stmt, {'survey_id': survey_id})
    return question(new_id)
#----------------------------------------------------------------------------
def save_question(**kwargs):
    stmt = "UPDATE question SET " \
        "type = %(type)s, "\
        "ordernumber = %(ordernumber)s, "\
        "question = %(question)s, "\
        "subquestion = %(subquestion)s, "\
        "description = %(description)s, "\
        "condition_question_id = %(condition_question_id)s, "\
        "condition_expression = %(condition_expression)s "\
        "WHERE id = %(id)s"
    db.update(stmt, {
        'type':kwargs["type"], 
        'ordernumber':kwargs["ordernumber"], 
        'question':kwargs["question"], 
        'subquestion':kwargs["subquestion"], 
        'description':kwargs["description"], 
        'condition_question_id':kwargs["condition_question_id"], 
        'condition_expression':kwargs["condition_expression"], 
        'id':int(kwargs["id"])}
    )
    return question(kwargs["id"])
#----------------------------------------------------------------------------
def up_question(question_id, ordernumber, survey_id):
    if int(ordernumber) > 1:
        db.update("update question set ordernumber = ordernumber + 1 where ordernumber = %(ordernumber)s - 1 and survey_id = %(survey_id)s", 
            {'ordernumber': ordernumber, 'survey_id': survey_id})
        db.update("update question set ordernumber = ordernumber - 1 where id = %(id)s", {'id':question_id})
        
    return survey_questions(survey_id)
#----------------------------------------------------------------------------
def down_question(question_id, ordernumber, survey_id):
    if int(ordernumber) < db.query("select max(ordernumber) as m from question where survey_id = %(survey_id)s",{'survey_id':survey_id})[0]["m"]:
        db.update("update question set ordernumber = ordernumber - 1 where ordernumber = %(ordernumber)s + 1 and survey_id = %(survey_id)s", 
            {'ordernumber': ordernumber, 'survey_id': survey_id})
        db.update("update question set ordernumber = ordernumber + 1 where id = %(id)s", {'id':question_id})
        
    return survey_questions(survey_id)
#----------------------------------------------------------------------------
def delete_question(survey_id, id):
    stmt = "delete from question where id = %(id)s"
    db.update(stmt, {'id': id})
    return survey_questions(survey_id)
#----------------------------------------------------------------------------
def question_options(question_id):
    stmt = "select * from question where id = %(question_id)s"
    question = db.query(stmt, {'question_id':question_id})[0]
    stmt = "select * from option where question_id = %(question_id)s order by ordernumber"
    options = db.query(stmt, {'question_id':question_id})
    return render("/admin","question_options.html", question = question, options=options)
#----------------------------------------------------------------------------
def add_option(question_id):
    stmt = "INSERT INTO option (question_id, ordernumber) SELECT %(question_id)s as question_id, "\
        "coalesce(max(ordernumber),0)+1 as ordernumber FROM option WHERE question_id = %(question_id)s"
    new_id = db.update(stmt, {'question_id':question_id})
    
    return question_options(question_id)
#----------------------------------------------------------------------------
def delete_option(id, question_id):
    stmt = "DELETE FROM option WHERE id = %(id)s"
    db.update(stmt, {'id':id})
    stmt = "SELECT id, ordernumber FROM option WHERE question_id = %(question_id)s order by ordernumber"
    options = db.query(stmt, {'question_id':question_id})
    ordernumber = 1
    for o in options:
        db.update("update option set ordernumber = %(ordernumber)s where id = %(id)s", {'ordernumber':ordernumber, 'id':o["id"]})
        ordernumber += 1
        
    return question_options(question_id)
#----------------------------------------------------------------------------
def update_options(**kwargs):
    for k in kwargs:
        if k.startswith("option:"):
            id = k.split(":")[1]
            value = kwargs[k]
            db.update("update option set value = %(value)s where id = %(id)s", {'id':id, 'value':value})
            
    return question_options(kwargs["id"])
#----------------------------------------------------------------------------
def up_option(option_id, ordernumber, question_id):
    if int(ordernumber) > 1:
        db.update("update option set ordernumber = ordernumber + 1 where ordernumber = %(ordernumber)s - 1 and question_id = %(question_id)s", 
            {'ordernumber': ordernumber, 'question_id': question_id})
        db.update("update option set ordernumber = ordernumber - 1 where id = %(id)s", {'id':option_id})
        
    return question_options(question_id)
#----------------------------------------------------------------------------
def down_option(option_id, ordernumber, question_id):
    if int(ordernumber) < db.query("select max(ordernumber) as m from option where question_id = %(question_id)s",{'question_id':question_id})[0]["m"]:
        db.update("update option set ordernumber = ordernumber - 1 where ordernumber = %(ordernumber)s + 1 and question_id = %(question_id)s", 
            {'ordernumber': ordernumber, 'question_id': question_id})
        db.update("update option set ordernumber = ordernumber + 1 where id = %(id)s", {'id':option_id})
        
    return question_options(question_id)
#----------------------------------------------------------------------------
def participants():
    participants = db.query("SELECT * FROM participant")
    return render("/admin","participants.html", participants=participants)
#----------------------------------------------------------------------------
def create_participant():
    new_id = db.update("insert into participant (email) values ('')")
    return participants()
#----------------------------------------------------------------------------
def delete_participant(id):
    db.update("delete from participant where id = %(id)s", {'id':id})
    return participants()
#----------------------------------------------------------------------------
def update_participants(**kwargs):
    for k in kwargs:
        if k.startswith("email:"):
            id = k.split(":")[1]
            value = kwargs[k]
            db.update("update participant set email = %(value)s where id = %(id)s", {'id':id, 'value':value})
        if k.startswith("firstname:"):
            id = k.split(":")[1]
            value = kwargs[k]
            db.update("update participant set firstname = %(value)s where id = %(id)s", {'id':id, 'value':value})
        if k.startswith("lastname:"):
            id = k.split(":")[1]
            value = kwargs[k]
            db.update("update participant set lastname = %(value)s where id = %(id)s", {'id':id, 'value':value})
            
    return participants()
#----------------------------------------------------------------------------
def invite_participant(survey_id, participant_id):
    # check if the participant is not already invited
    c = db.query("select count(*) as c from survey_participant where survey_id = %(survey_id)s and participant_id = %(participant_id)s",
        {'survey_id':survey_id, 'participant_id': participant_id})[0]["c"]
    # of not invited than make a session, send a mail and register as invited
    if c == 0:
        # make session
        session_id = str(uuid4())
        db.create_session(session_id, survey_id)
 
        # register invited
        db.update("insert into survey_participant (survey_id, participant_id) values (%(survey_id)s, %(participant_id)s)",
            {'survey_id': survey_id, 'participant_id': participant_id})
        return session_id
#----------------------------------------------------------------------------
def invite(survey_id, invitees):
    if not isinstance(invitees, list):
        invitees = [invitees]
        
    for participant_id in invitees:
        session_id = invite_participant(survey_id, participant_id)
        participant = db.query("select * from participant where id = %(participant_id)s", {'participant_id':participant_id})[0]
        body = render("/admin","invitation.html", session_id = session_id, participant = participant)
        email("Uitnodiging", body, participant["email"])

    return survey_participants(survey_id)
#----------------------------------------------------------------------------
def email(subject, body, email):
    msg = MIMEText(body)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = email

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(SMTP_HOST)
    s.login(SENDER, SMTP_PASSWORD)
    try:
        s.sendmail(SENDER, email, msg.as_string())
    except Exception as e:
        print e
    s.quit()    
    

if __name__ == "__main__":
    create_survey("testje", "")