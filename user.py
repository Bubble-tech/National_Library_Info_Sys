import pymongo

# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Connection to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["NaLib"]
users_collection = db["users"]
staff_collection = db["staff"]
books_collection = db["books"]
members_collection = db["members"]

# Create a database named 'Library'
db = client["NaLib"]


users_collection = db["users"]
members_collection= db["members"]

# Insert admin data
admin_data = {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "phone": "123-456-7890",
    "password": "admin_password",
    "type": "admin"
}

users_collection.insert_one(admin_data)
print("Admin data inserted successfully.")

# Close the MongoDB connection
client.close()
print("MongoDB connection closed.")

# Re-establish the connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["NaLib"]
users_collection = db["users"]
staff_collection = db["staff"]
books_collection = db["books"]
members_collection = db["members"]

