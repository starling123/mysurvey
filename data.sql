insert into survey (id, name, description) values (1, "Enquête gemeenteopbouw Silo 2018","");

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 0, "A", "START", "Begin van de enquête", NULL, NULL);

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 1, "B", "SECTION", "Begin van onderdeel A", NULL, NULL);

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 2, "A", "1", "Ik ben woonachtig", NULL, NULL);
insert into option (survey_id, question_id, id, value) values 
  (1,2,1, "in de stad Utrecht"),
  (1,2,2, "niet in de stad Utrecht");


insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 3, "A", "1", "Ik kom in Silo", NULL, NULL);
insert into option (survey_id, question_id, id, value) values 
  (1,3,1, "korter dan 2 jaar"),
  (1,3,2, "tussen 2 en 5 jaar"),
  (1,3,3, "tussen 5 en 10 jaar"),
  (1,3,4, "langer dan 10 jaar");

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 4, "A", "M", "Ik neem min of meer regelmatig deel aan de volgende activiteiten:", NULL, NULL);
insert into option (survey_id, question_id, id, value) values 
  (1,4,1, "Wijkavond"),
  (1,4,2, "Bijbelstudie"),
  (1,4,3, "30ers groep"),
  (1,4,4, "Eetgroep");

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 5, "B", "SECTION", "Begin van onderdeel B", NULL, NULL);

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 6, "A", "1", "Ik waardeer de zondagochtenddienst als:", "traditioneel", NULL);
insert into option (survey_id, question_id, id, value) values 
  (1,6,1, "1. zou meer kunnen"),
  (1,6,2, "2. goed"),
  (1,6,3, "3. overdreven"),
  (1,6,4, "4. weet niet/nvt");

insert into question(survey_id, id, section, type, question, subquestion, description, condition_question_id, condition_expression)
values (1, 7, "A", "1", "Ik waardeer de eetgroep als:", "traditioneel", NULL, 4, '4 in [{response}]');
insert into option (survey_id, question_id, id, value) values 
  (1,7,1, "1. zou meer kunnen"),
  (1,7,2, "2. goed"),
  (1,7,3, "3. overdreven"),
  (1,7,4, "4. weet niet/nvt");

insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 8, "A", "O", "Vul maar wat in:", NULL, NULL);


insert into question(survey_id, id, section, type, question, subquestion, description)
values (1, 9, "A", "END", "Einde van de enquête", NULL, NULL);


insert into participant (email, firstname, lastname) values 
	("peter.spreeuwers@gmail.com", "Peter", "Spreeuwers")
	,("regien.smit@hotmail.com", "Regien", "Smit")



