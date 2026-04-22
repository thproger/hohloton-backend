import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://vadimvrachenko_db_user:<db_password>@cluster0.47ucd3e.mongodb.net/?appName=Cluster0")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "hohloton")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAp6uTF1lx5C6g4GOud9h8RZsw0CTOtERo")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
