import json
import os
import uuid
from datetime import datetime

class UserBase:
    def __init__(self, db_path='db/users.json'):
        self.db_path = db_path
        self.users = self.load_users()
    
    def load_users(self):
        """
        Load users from the file, creating the file if it does not exist.
        """
        if not os.path.exists(self.db_path):
            # Create the directory if it does not exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Create an empty users file
            with open(self.db_path, 'w') as file:
                json.dump({}, file)
        
        with open(self.db_path, 'r') as file:
            return json.load(file)
    
    def save_users(self):
        """
        Save users to the file.
        """
        with open(self.db_path, 'w') as file:
            json.dump(self.users, file, indent=4)
    
    def create_user(self, request: str) -> str:
        try:
            data = json.loads(request)
            name = data["name"]
            display_name = data["display_name"]
        
            # Constraints
            if len(name) > 64:
                return json.dumps({"error": "name exceeds 64 characters"})
            if len(display_name) > 64:
                return json.dumps({"error": "display_name exceeds 64 characters"})
        
            # Check for duplicate user names
            if any(user["name"] == name for user in self.users.values()):
                return json.dumps({"error": "user name must be unique"})
        
            user_id = str(uuid.uuid4())
            creation_time = datetime.now().isoformat()
        
            # Add the new user to self.users
            self.users[user_id] = {
                "name": name,
                "display_name": display_name,
                "creation_time": creation_time
            }
        
            # Save the updated users to file
            self.save_users()
        
            return json.dumps({"id": user_id})
        except Exception as e:
            return json.dumps({"error": f"Failed to create user: {str(e)}"})
    
    def list_users(self) -> str:
        """
        List all users.
        """
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
        """
        Describe a user.
        """
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
        """
        Update user details.
        """
        data = json.loads(request)
        user_id = data["id"]
        user_details = data["user"]
        
        if user_id not in self.users:
            return json.dumps({"error": "user not found"})
        
        # Constraints
        if "name" in user_details:
            return json.dumps({"error": "user name cannot be updated"})
        if "display_name" in user_details and len(user_details["display_name"]) > 64:
            return json.dumps({"error": "display_name exceeds 64 characters"})
        
        self.users[user_id].update(user_details)
        self.save_users()
        return json.dumps({"status": "success"})
    
    def get_user_teams(self, request: str) -> str:
        """
        Get teams associated with a user.
        """
        data = json.loads(request)
        user_id = data["id"]
        
        if user_id not in self.users:
            return json.dumps({"error": "user not found"})
        
        # Placeholder for user teams, assuming some data structure for teams exists
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

# Example usage
user_base = UserBase()
unique_name = f"john_doe_{uuid.uuid4().hex[:8]}"  # Ensure the user name is unique
request_create = json.dumps({"name": unique_name, "display_name": "John Doe"})
response_create = user_base.create_user(request_create)
print(response_create)

# Check if user creation was successful
response_data = json.loads(response_create)
if "id" in response_data:
    user_id = response_data["id"]

    # List users
    print(user_base.list_users())

    # Describe user
    request_describe = json.dumps({"id": user_id})
    print(user_base.describe_user(request_describe))
       
    # Update user
    request_update = json.dumps({"id": user_id, "user": {"display_name": "John D."}})
    print(user_base.update_user(request_update))
    
    # Get user teams
    request_teams = json.dumps({"id": user_id})
    print(user_base.get_user_teams(request_teams))
else:
    print("User creation failed:", response_create)
