import csv
import json
import database as db
import admin as admin

#----------------------------------------------------------------------------
def create_question(
    survey_id,
    section,
    type,
    question,
    subquestion = "",
    description = "",
    condition_question_id = "NULL",
    condition_expression = "",
    question_ordernumber = 0):

    new_id = db.update("insert into question (survey_id, section, type, question, subquestion, description, "\
           "condition_question_id, condition_expression, ordernumber) "\
           "values (%(survey_id)s, %(section)s,%(type)s,%(question)s,%(subquestion)s, "\
           "%(description)s,  %(condition_question_id)s, %(condition_expression)s, %(question_ordernumber)s)",
        {
            'survey_id' : survey_id,
            'section' : section,
            'type' :  type,
            'question' : json.dumps(question)[1:-1],
            'subquestion' : json.dumps(subquestion)[1:-1],
            'description' : description,
            'condition_question_id' : condition_question_id,
            'condition_expression' : condition_expression,
            'question_ordernumber' : question_ordernumber
        }
    )
    
    return new_id
#----------------------------------------------------------------------------
def create_option(question_id, value, ordernumber):
    stmt = "insert into option (question_id, value, ordernumber) values ( {question_id}, '{value}', {ordernumber})".format(
        question_id = question_id,
        value = value,
        ordernumber = ordernumber
    )
    print stmt
    db.execute(stmt)
#----------------------------------------------------------------------------
def import_enquete(filename, survey_id, name, description):
    #admin.delete_survey(survey_id)
    #admin.create_survey(survey_id, name, description)
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        question_ordernumber = 1
        for row in reader:
            condition_question_id = row["voorwaarde_vraag_id"]
            if len(condition_question_id.strip()) == 0:
                condition_question_id = 0

            new_id = create_question(
                survey_id,
                row["onderdeel"],
                row["type"],
                row["vraag"],
                row["subvraag"],
                row["toelichting"],
                condition_question_id,
                row["voorwaarde"],
                question_ordernumber)

            option_keys = sorted(filter(lambda s : s.startswith("optie"), row))
            option_ordernumber = 1
            for ok in option_keys:
                if row[ok] == "":
                    break
                create_option(new_id,row[ok], option_ordernumber)
                option_ordernumber += 1

            question_ordernumber += 1
#----------------------------------------------------------------------------
def csv_to_json(filename):
    result = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        vraagnummer = 1
        for row in reader:
            try:
                vraagnummer = int(row["vraagnummer"])
            except:
                pass           
            row["vraagnummer"] = vraagnummer
            result.append(row)
    
    #open("enquete.json", "w").write(json.dumps(result, indent=4))
    return json.dumps(result, indent=4)

if __name__ == "__main__":
#    print json.dumps(import_enquete("enquete.csv", 1, "De enquete", ""), indent = 3)
    csv_to_json("enquete.csv")    
