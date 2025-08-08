from database.mongo import db
from bson import ObjectId

user_db = db['users']
def get_users( role: str = None, first_name: str = None, start_birth_date: str = None, end_birth_date: str = None):

    results = []

    filters = {}
    if role:
        filters['role']= role #{"role" : role}
    if first_name:
        filters['first_name'] = first_name #{"first_name": first_name}
    if start_birth_date and end_birth_date:
        filters['birth_date'] = {"$gte": start_birth_date, "$lte": end_birth_date}


    users = user_db.find(filters)
    for user in users:
        user['_id'] = str(user['_id'])
        user['password'] = None
        results.append(user)

    return {"message": "Ok", "data":results}

def update_user(user_id: str, user):
    data_user = user.model_dump()
    user_db.update_one({"_id":ObjectId(user_id)}, {"$set": data_user})
    return {"message": "User updated successfully"}

def get_user(user_id: str):
    user = user_db.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"message": "User not found"}

    user['_id'] = str(user['_id'])
    user['password'] = None
    return {"message": "Ok", "data": user}

def delete_user(user_id: str):
    user = user_db.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"message": "User not found"}

    user_db.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted successfully"}