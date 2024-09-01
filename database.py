import pymysql.cursors

class Database:
    def __init__(self, database, user, password, host='localhost', port=3306):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            print("Xatolik yuz berdi:", str(e))
            self.connection.rollback()

    def add_user(self, first_name, last_name, phone_number):
        query = "INSERT INTO users (first_name, last_name, phone_number) VALUES (%s, %s, %s)"
        self.execute(query, (first_name, last_name, phone_number))

    def close(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
