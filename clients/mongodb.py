from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://Anshh_xotx:Anshul092004@webhostmanager.uer5akp.mongodb.net/?appName=WebHostManager"
)

db = client["webhostmanager"]

clients_collection = db["clients"]
users_collection = db["users"]