import mysql.connector as db
import json
from uuid import uuid4

#DBHOST = "mysurveydb"
DBHOST = "localhost"
USER = "root"
PASSWORD = "mysurvey"
DBNAME = "mysurvey"


#----------------------------------------------------------------------------
def getConn():
    return db.connect(user=USER, password=PASSWORD, database=DBNAME, host=DBHOST)
#----------------------------------------------------------------------------
def create_schema():
    script = open("schema.sql", "r").read()
    conn = db.connect(user=USER, password=PASSWORD, host=DBHOST)
    conn.cmd_query("DROP DATABASE IF EXISTS " + DBNAME)
    conn.cmd_query("CREATE DATABASE " + DBNAME)
    conn.close()
    conn = getConn()
    #conn.start_transaction()
    for stmt in script.split(";"):
        conn.cmd_query(stmt)
    #conn.commit()

    #cursor = conn.cursor()

#----------------------------------------------------------------------------
def query(query, params = None):
    conn = getConn()
    cursor = conn.cursor(buffered=True)
    cursor.execute(query, params)
    result = []
    for r in cursor:
        record = {}
        for i in range(0,len(r)):
            record[cursor.column_names[i]] = r[i]
        result.append(record)
    conn.close()
    return result
#----------------------------------------------------------------------------
def execute(query):
    conn = getConn()
    conn.start_transaction()
    result = conn.cmd_query(query)
    conn.commit()
    conn.close()
    return result
#----------------------------------------------------------------------------
def update(query, params=None):
    conn = getConn()
    conn.start_transaction()
    cursor = conn.cursor(buffered=True)
    cursor.execute(query, params)
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id
#----------------------------------------------------------------------------
def fill():
    sql = open("data.sql","r").read()
    print sql
    conn = getConn()
    conn.start_transaction();
    for stmt in sql.split(";"):
        try:
            conn.cmd_query(stmt)
        except:
            print stmt
    conn.commit();
    conn.close()

#----------------------------------------------------------------------------
def create_session(id, survey_id):
    stmt = "insert into session (id, survey_id, question_ordernumber, completed) " \
            "values ('{id}', {survey_id}, 1, false)".format(
        id = id, survey_id = survey_id
    )
    execute(stmt)
#----------------------------------------------------------------------------
def get_session(id):
    stmt = "select * from session where id = '{id}'".format(id = id)
    result = query(stmt)
    return result[0]
#----------------------------------------------------------------------------
def get_question(survey_id, question_ordernumber):
    result = query("select * from question where survey_id = %(survey_id)s and ordernumber = %(question_ordernumber)s",
        {'survey_id': survey_id, 'question_ordernumber':question_ordernumber}
    )
    
    return result[0]
#----------------------------------------------------------------------------
def next_question(session_id):
    session = get_session(session_id)
    # get max ordernumber
    stmt = "select max(ordernumber) as max_ordernumber from question where survey_id = {survey_id}".format(
        survey_id = session["survey_id"]
    )
    max_ordernumber = query(stmt)[0]["max_ordernumber"]
    if session["question_ordernumber"] < max_ordernumber:
        stmt = "update session set question_ordernumber = question_ordernumber + 1 where id = '{session_id}'".format(
            session_id = session_id
        )
        execute(stmt)
        return True
    return False
#----------------------------------------------------------------------------
def prev_question(session_id):
    session = get_session(session_id)
    if session["question_ordernumber"] > 1:
        stmt = "update session set question_ordernumber = question_ordernumber - 1 where id = '{session_id}'".format(
            session_id = session_id
        )
        execute(stmt)
        return True
    return False
#----------------------------------------------------------------------------
def get_options(question_id):
    result = query("select * from option where question_id = %(question_id)s",
        {'question_id': question_id}
    )
    return result;
#----------------------------------------------------------------------------
def save_response(session_id, question_id, response):
    stmt = "INSERT INTO response (session_id, question_id, value) VALUES " \
           "('{session_id}',{question_id},'{response}')" \
           "ON DUPLICATE KEY UPDATE value='{response}'".format(
        session_id = session_id,
        question_id = question_id,
        response = response
    )
    print stmt
    execute(stmt)
#----------------------------------------------------------------------------
def get_response(session_id, question_id):
    stmt = "select * from response where session_id = '{session_id}' and question_id = {question_id}".format(
        session_id = session_id,
        question_id = question_id
    )
    result = query(stmt)
    if len(result) > 0:
        return result[0]["value"]
    else:
        return None
#----------------------------------------------------------------------------
def get_question_responses(session_id):
    stmt = "select q.id as q_id, q.type as q_type, q.question as q_question, r.value as r_value, o.id as o_id, o.value as o_value "\
           "from session s "\
           "join question q on (s.survey_id = q.survey_id) "\
           "left join response r on (s.id = r.session_id and q.id = r.question_id) "\
           "left join option o on (q.id = o.question_id) "\
           "where s.id = '{session_id}'".format(
               session_id = session_id)
    return query(stmt)
        
if __name__ == "__main__":
    create_schema()
    fill()
    #select("select * from survey")
    #email("test", "Dit is een test", "peter.spreeuwers@gmil.com")
    
