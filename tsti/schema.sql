DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS post_likes;
DROP TABLE IF EXISTS kingdom;
DROP TABLE IF EXISTS kingdom_requests;
DROP TABLE IF EXISTS question_answers;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS managers;
DROP TABLE IF EXISTS happened;
DROP TABLE IF EXISTS warnings;

CREATE TABLE kingdom
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kingdomname TEXT UNIQUE NOT NULL,
    kingdom_exp TEXT NOT NULL,
    kingdom_level INTEGER DEFAULT 0,
    color_hex TEXT NOT NULL,
    pp_file_name TEXT DEFAULT 'userlogos/default.jpg'
);

CREATE TABLE kingdom_requests
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    join_desc TEXT NOT NULL,
    kingdom_id INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (kingdom_id) REFERENCES kingdom (id)
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    email_verified INTEGER DEFAULT 0,
    sendedmail_code TEXT,
    point INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    ban INTEGER DEFAULT 1, /* if ban divides by 2, that means user is banned from messages, if 3, that means user is banned from point addition, if 5, that means user cannot log in*/
    kingdom_id INTEGER DEFAULT 0,
    report_level INTEGER DEFAULT 0,
    kingdom_perm INTEGER DEFAULT 0,
    editorer INTEGER DEFAULT 1, /* Dividing rules. 2:Equations, 3:Inferences, 5:Geometric Questions, 7: Who Wants to be a Millionaire */

    /* Profile */
    pp_file_name TEXT DEFAULT 'userlogos/default.jpg',
    profile_explanation TEXT DEFAULT 'Ben bir TSTi kullanıcısıyım.'
);

CREATE TABLE post_likes(
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    answer_to INTEGER DEFAULT -1,
    attachedQuestionID INTEGER DEFAULT -1,
    attachedQuestionSeed INTEGER DEFAULT 0,
    visibility INTEGER DEFAULT 1,
    channelId INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE question_answers
(
    author_id INTEGER NOT NULL,
    question_seed INTEGER,
    question_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE reports
(
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type INTEGER DEFAULT 0, /* 0 = an message, 1 = an kingdom */
    author_id INTEGER NOT NULL,
    i_id INTEGER DEFAULT 0, /* if (report_type = 0, i_id = message_id),(report_type = 1, i_id = kingdom_id)*/
    report_state INTEGER DEFAULT 0,
    infoFR TEXT NOT NULL,
    visibility INTEGER DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (i_id) REFERENCES post (id)
);

CREATE TABLE happened
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    indpart_id INTEGER NOT NULL, /* indirect participant */
    explanation TEXT NOT NULL,
    manager_id INTEGER NOT NULL, /* participant manager, if equals to zero there is no manager for that */
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES user (id),
    FOREIGN KEY (indpart_id) REFERENCES user (id),
    FOREIGN KEY (manager_id) REFERENCES managers (id)
);

CREATE TABLE managers
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE warnings
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warning_type INTEGER NOT NULL,
    warning_from INTEGER DEFAULT 0, 
        /* if warning_from equals to 0, means warning came from a manager. 
            if 1 warning came from kingdom leader*/
    id_to INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
        /* this would be kingdom_id when warning_from is 1, so kingdom */
    warning TEXT NOT NULL,
    seen INTEGER DEFAULT 0,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO kingdom (kingdomname, color_hex, kingdom_exp) VALUES ("Zigot Ustanın Kraliyeti","#17ad3a","ÇOK GÜZEL HAA");
INSERT INTO kingdom (kingdomname, color_hex, kingdom_exp) VALUES ("Elitizm Başsöz","#ffdd00","Gelin evlatlarım.");