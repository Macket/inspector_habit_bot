DROP_USERS_TABLE = """
       DROP TABLE users;
"""

# id == telegram_id
CREATE_USERS_TABLE = """
       CREATE TABLE users (
           id BIGINT PRIMARY KEY,
           username VARCHAR(255),
           first_name VARCHAR(255),
           last_name VARCHAR(255),
           timezone VARCHAR(255),
           language_code VARCHAR(15),
           is_active BOOLEAN DEFAULT TRUE,
           referrer BIGINT DEFAULT NULL,
           FOREIGN KEY (referrer) REFERENCES users (id) ON DELETE SET NULL
       )
       """
