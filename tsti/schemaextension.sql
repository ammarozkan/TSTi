DROP TABLE IF EXISTS warnings;

CREATE TABLE warnings
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warning_type INTEGER NOT NULL,
    warning_from INTEGER DEFAULT 0, 
        /* if warning_from equals to 0, means warning came from a manager. 
            if 1 warning came from kingdom leader*/
    id_to INTEGER NOT NULL,
    manager_id INTEGER NOT NULL,
    warning TEXT NOT NULL,
    seen INTEGER DEFAULT 0,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);