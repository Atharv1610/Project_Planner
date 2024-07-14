import json
import os
import uuid
from datetime import datetime

class TeamBase:
    def __init__(self, db_path='db/teams.json'):
        self.db_path = db_path
        self.teams = self.load_teams()
    
    def load_teams(self):
        """
        Load teams from the file, creating the file if it does not exist.
        """
        if not os.path.exists(self.db_path):
            # Create the directory if it does not exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Create an empty teams file
            with open(self.db_path, 'w') as file:
                json.dump({}, file)
        
        with open(self.db_path, 'r') as file:
            return json.load(file)
    
    def save_teams(self):
        """
        Save teams to the file.
        """
        with open(self.db_path, 'w') as file:
            json.dump(self.teams, file, indent=4)
    
    def create_team(self, request: str) -> str:
        try:
            data = json.loads(request)
            name = data["name"]
            description = data["description"]
            admin = data["admin"]
        
            # Constraints
            if len(name) > 64:
                return json.dumps({"error": "name exceeds 64 characters"})
            if len(description) > 128:
                return json.dumps({"error": "description exceeds 128 characters"})
        
            # Check for duplicate team names
            if any(team["name"] == name for team in self.teams.values()):
                return json.dumps({"error": "team name must be unique"})
        
            team_id = str(uuid.uuid4())
            creation_time = datetime.now().isoformat()
        
            # Add the new team to self.teams
            self.teams[team_id] = {
                "name": name,
                "description": description,
                "creation_time": creation_time,
                "admin": admin,
                "users": []
            }
        
            # Save the updated teams to file
            self.save_teams()
        
            return json.dumps({"id": team_id})
        except Exception as e:
            return json.dumps({"error": f"Failed to create team: {str(e)}"})
    
    def list_teams(self) -> str:
        """
        List all teams.
        """
        teams_list = [
            {
                "name": team["name"],
                "description": team["description"],
                "creation_time": team["creation_time"],
                "admin": team["admin"]
            }
            for team in self.teams.values()
        ]
        return json.dumps(teams_list)
    
    def describe_team(self, request: str) -> str:
        """
        Describe a team.
        """
        data = json.loads(request)
        team_id = data["id"]
        
        if team_id not in self.teams:
            return json.dumps({"error": "team not found"})
        
        team = self.teams[team_id]
        return json.dumps({
            "name": team["name"],
            "description": team["description"],
            "creation_time": team["creation_time"],
            "admin": team["admin"]
        })
    
    def update_team(self, request: str) -> str:
        """
        Update team details.
        """
        data = json.loads(request)
        team_id = data["id"]
        team_details = data["team"]
        
        if team_id not in self.teams:
            return json.dumps({"error": "team not found"})
        
        # Constraints
        if "name" in team_details and len(team_details["name"]) > 64:
            return json.dumps({"error": "name exceeds 64 characters"})
        if "description" in team_details and len(team_details["description"]) > 128:
            return json.dumps({"error": "description exceeds 128 characters"})
        if "name" in team_details and any(team["name"] == team_details["name"] for tid, team in self.teams.items() if tid != team_id):
            return json.dumps({"error": "team name must be unique"})
        
        self.teams[team_id].update(team_details)
        self.save_teams()
        return json.dumps({"status": "success"})
    
    def add_users_to_team(self, request: str) -> str:
        """
        Add users to a team.
        """
        data = json.loads(request)
        team_id = data["id"]
        user_ids = data["users"]
        
        if team_id not in self.teams:
            return json.dumps({"error": "team not found"})
        
        team = self.teams[team_id]
        
        if len(team["users"]) + len(user_ids) > 50:
            return json.dumps({"error": "adding these users exceeds the maximum of 50 users"})
        
        team["users"].extend(user_ids)
        team["users"] = list(set(team["users"]))  # Ensure uniqueness
        self.save_teams()
        return json.dumps({"status": "success"})
    
    def remove_users_from_team(self, request: str) -> str:
        """
        Remove users from a team.
        """
        data = json.loads(request)
        team_id = data["id"]
        user_ids = data["users"]
        
        if team_id not in self.teams:
            return json.dumps({"error": "team not found"})
        
        team = self.teams[team_id]
        team["users"] = [user for user in team["users"] if user not in user_ids]
        self.save_teams()
        return json.dumps({"status": "success"})
    
    def list_team_users(self, request: str) -> str:
        """
        List users of a team.
        """
        data = json.loads(request)
        team_id = data["id"]
        
        if team_id not in self.teams:
            return json.dumps({"error": "team not found"})
        
        team = self.teams[team_id]
        users_list = [{"id": user_id} for user_id in team["users"]]
        return json.dumps(users_list)

# Example usage
team_base = TeamBase()
request_create_team = json.dumps({
    "name": "team_alpha",
    "description": "Alpha team for project",
    "admin": "admin_user_id"
})
response_create_team = team_base.create_team(request_create_team)
print(response_create_team)

# Check if team creation was successful
response_data_team = json.loads(response_create_team)
if "id" in response_data_team:
    team_id = response_data_team["id"]

    # List teams
    print(team_base.list_teams())

    # Describe team
    request_describe_team = json.dumps({"id": team_id})
    print(team_base.describe_team(request_describe_team))
       
    # Update team
    request_update_team = json.dumps({"id": team_id, "team": {"description": "Updated Alpha team for project"}})
    print(team_base.update_team(request_update_team))
    
    # Add users to team
    request_add_users = json.dumps({"id": team_id, "users": ["user1", "user2"]})
    print(team_base.add_users_to_team(request_add_users))
    
    # List team users
    request_list_team_users = json.dumps({"id": team_id})
    print(team_base.list_team_users(request_list_team_users))
    
    # Remove users from team
    request_remove_users = json.dumps({"id": team_id, "users": ["user1"]})
    print(team_base.remove_users_from_team(request_remove_users))
    
    # List team users after removal
    print(team_base.list_team_users(request_list_team_users))
else:
    print("Team creation failed:", response_create_team)
