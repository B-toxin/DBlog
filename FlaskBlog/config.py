class Config:
    SECRET_KEY = 'e71121f8359c7c241f56e489f91f32d7'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///clique.db'  # SQLite database file is named site.db in the current directory
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'caasi9092@gmail.com'
    MAIL_PASSWORD = 'wrxcyfiacptxmlib'
    STATIC_FOLDER = 'static'
