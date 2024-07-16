import json
import os
import uuid
from datetime import datetime

class UserBase:
    def __init__(self, db_path='db/users.json'):
        self.db_path = db_path
        self.users = self.load_users()
    
    def load_users(self):
       
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w') as file:
                json.dump({}, file)
        
        with open(self.db_path, 'r') as file:
            return json.load(file)
    
    def save_users(self):
        with open(self.db_path, 'w') as file:
            json.dump(self.users, file, indent=4)
    
    def create_user(self, request: str) -> str:
        try:
            data = json.loads(request)
            name = data["name"]
            display_name = data["display_name"]
        
            if len(name) > 64:
                return json.dumps({"error": "name exceeds 64 characters"})
            if len(display_name) > 64:
                return json.dumps({"error": "display_name exceeds 64 characters"})
        
            if any(user["name"] == name for user in self.users.values()):
                return json.dumps({"error": "user name must be unique"})
        
            user_id = str(uuid.uuid4())
            creation_time = datetime.now().isoformat()
        
            self.users[user_id] = {
                "name": name,
                "display_name": display_name,
                "creation_time": creation_time
            }

            self.save_users()
        
            return json.dumps({"id": user_id})
        except Exception as e:
            return json.dumps({"error": f"Failed to create user: {str(e)}"})
    
    def list_users(self) -> str:

        users_list = [
            {
                "name": user["name"],
                "display_name": user["display_name"],
                "creation_time": user["creation_time"]
            }
            for user in self.users.values()
        ]
        return json.dumps(users_list)
    
    def describe_user(self, request: str) -> str:

        data = json.loads(request)
        user_id = data["id"]
        
        if user_id not in self.users:
            return json.dumps({"error": "user not found"})
        
        user = self.users[user_id]
        return json.dumps({
            "name": user["name"],
            "description": user.get("description", ""),
            "creation_time": user["creation_time"]
        })
    
    def update_user(self, request: str) -> str:

        data = json.loads(request)
        user_id = data["id"]
        user_details = data["user"]
        
        if user_id not in self.users:
            return json.dumps({"error": "user not found"})

        if "name" in user_details:
            return json.dumps({"error": "user name cannot be updated"})
        if "display_name" in user_details and len(user_details["display_name"]) > 64:
            return json.dumps({"error": "display_name exceeds 64 characters"})
        
        self.users[user_id].update(user_details)
        self.save_users()
        return json.dumps({"status": "success"})
    
    def get_user_teams(self, request: str) -> str:

        data = json.loads(request)
        user_id = data["id"]
        
        if user_id not in self.users:
            return json.dumps({"error": "user not found"})
        
        user_teams = [
            {
                "name": "team1",
                "description": "description1",
                "creation_time": datetime.now().isoformat()
            },
            {
                "name": "team2",
                "description": "description2",
                "creation_time": datetime.now().isoformat()
            }
        ]
        
        return json.dumps(user_teams)


user_base = UserBase()
unique_name = f"john_joseph{uuid.uuid4().hex[:8]}" 
request_create = json.dumps({"name": unique_name, "display_name": "John Joseph"})
response_create = user_base.create_user(request_create)
print(response_create)

response_data = json.loads(response_create)
if "id" in response_data:
    user_id = response_data["id"]

    print(user_base.list_users())

    request_describe = json.dumps({"id": user_id})
    print(user_base.describe_user(request_describe))
       
    request_update = json.dumps({"id": user_id, "user": {"display_name": "John J."}})
    print(user_base.update_user(request_update))
    
    request_teams = json.dumps({"id": user_id})
    print(user_base.get_user_teams(request_teams))
else:
    print("User creation failed:", response_create)
