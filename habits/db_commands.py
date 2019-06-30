DROP_HABITS_TABLE = """
       DROP TABLE habits;
"""

CREATE_HABITS_TABLE = """
       CREATE TABLE habits (
       id BIGSERIAL PRIMARY KEY,
       user_id INTEGER,
       label VARCHAR(255),
       question VARCHAR(255),
       days_of_week VARCHAR(15),
       time_array VARCHAR(255),
       fine SMALLINT,
       FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE 
       )
       """

#
# CREATE_HABITS_TABLE = """
#        CREATE TABLE habits (
#        id BIGSERIAL PRIMARY KEY,
#        user_id INTEGER,
#        label VARCHAR(255),
#        question VARCHAR(255),
#        monday BOOLEAN DEFAULT FALSE,
#        tuesday BOOLEAN DEFAULT FALSE,
#        wednesday BOOLEAN DEFAULT FALSE,
#        thursday BOOLEAN DEFAULT FALSE,
#        friday BOOLEAN DEFAULT FALSE,
#        saturday BOOLEAN DEFAULT FALSE,
#        sunday BOOLEAN DEFAULT FALSE,
#        fine SMALLINT,
#        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
#        )
#        """
