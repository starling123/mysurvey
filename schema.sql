CREATE TABLE survey (
  id integer auto_increment,
  name varchar(100),
  description text,
  primary key (id)
);

CREATE TABLE question(
    id integer auto_increment,
    survey_id integer,
    section char(2),
    type char(10),
    question varchar(255),
    subquestion varchar(255),
    description text,
    condition_question_id integer,
    condition_expression varchar(255),

    ordernumber integer,
    question_number integer,

    primary key(id),
    constraint fk_survey foreign key (survey_id) references survey (id)
    	on delete cascade
    	on update restrict
);

CREATE TABLE option (
    id integer auto_increment,
    question_id integer,
    value text,
    ordernumber integer, 

    primary key(id),
    constraint fk_question foreign key (question_id) references question (id)
    	on delete cascade
    	on update restrict
);
    
    
CREATE TABLE session (
    id varchar(40),
    survey_id integer,
    question_ordernumber integer,
    completed boolean,
    
    primary key(id)
);

CREATE TABLE response (
    session_id varchar(40),
    question_id integer,
    value text,
    primary key(session_id, question_id)
);

CREATE TABLE participant (
    id integer auto_increment,
    
    email varchar(255),
    firstname varchar(255),
    lastname varchar(255),
    
    primary key(id),
    constraint uk_email unique (email)
);

CREATE TABLE survey_participant (
    survey_id integer,
    participant_id integer,

    invited boolean,

    primary key(survey_id, participant_id)
)



    
