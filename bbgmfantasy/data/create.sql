DROP TABLE IF EXISTS labels;

CREATE TABLE labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    labelSet TEXT,
    label TEXT,
    UNIQUE(labelSet,label)
);