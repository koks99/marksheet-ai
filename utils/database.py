from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://kokulan99:koku1999@mongocluster.tb95q.mongodb.net/?retryWrites=true&w=majority&appName=MongoCluster"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["mydatabase"]

students_col = mydb["students"]
users_col = mydb["users"]