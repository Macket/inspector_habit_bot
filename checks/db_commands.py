DROP_CHECKS_TABLE = """
       DROP TABLE checks;
"""

CREATE_CHECKS_TABLE = """
       CREATE TABLE checks (
           id BIGSERIAL PRIMARY KEY,
           habit_id BIGINT,
           datetime_native TIMESTAMP,
           datetime_utc TIMESTAMP,
           status VARCHAR(15),
           FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE 
       )
       """
