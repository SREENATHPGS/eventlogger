DROP TABLE IF EXISTS log_database;

CREATE TABLE log_database (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_tag TEXT NOT NULL,
    log_type TEXT NOT NULL,
    log_data JSON,
    log_text TEXT
);