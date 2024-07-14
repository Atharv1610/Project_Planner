import json
import os
import uuid
from datetime import datetime

class ProjectBoardBase:
    def __init__(self, db_path='db/boards.json'):
        self.db_path = db_path
        self.boards = self.load_boards()
    
    def load_boards(self):
        """
        Load boards from the file, creating the file if it does not exist.
        """
        if not os.path.exists(self.db_path):
            # Create the directory if it does not exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Create an empty boards file
            with open(self.db_path, 'w') as file:
                json.dump({}, file)
        
        with open(self.db_path, 'r') as file:
            return json.load(file)
    
    def save_boards(self):
        """
        Save boards to the file.
        """
        with open(self.db_path, 'w') as file:
            json.dump(self.boards, file, indent=4)
    
    def create_board(self, request: str):
        try:
            data = json.loads(request)
            name = data["name"]
            description = data["description"]
            team_id = data["team_id"]
            creation_time = data["creation_time"]
        
            # Constraints
            if len(name) > 64:
                return json.dumps({"error": "name exceeds 64 characters"})
            if len(description) > 128:
                return json.dumps({"error": "description exceeds 128 characters"})
        
            # Check for duplicate board names within the same team
            if any(board["name"] == name and board["team_id"] == team_id for board in self.boards.values()):
                return json.dumps({"error": "board name must be unique for a team"})
        
            board_id = str(uuid.uuid4())
        
            # Add the new board to self.boards
            self.boards[board_id] = {
                "name": name,
                "description": description,
                "team_id": team_id,
                "creation_time": creation_time,
                "status": "OPEN",
                "tasks": []
            }
        
            # Save the updated boards to file
            self.save_boards()
        
            return json.dumps({"id": board_id})
        except Exception as e:
            return json.dumps({"error": f"Failed to create board: {str(e)}"})
    
    def close_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data["id"]
        
        if board_id not in self.boards:
            return json.dumps({"error": "board not found"})
        
        board = self.boards[board_id]
        
        # Ensure all tasks are marked as COMPLETE
        if any(task["status"] != "COMPLETE" for task in board["tasks"]):
            return json.dumps({"error": "cannot close board with incomplete tasks"})
        
        board["status"] = "CLOSED"
        board["end_time"] = datetime.now().isoformat()
        self.save_boards()
        return json.dumps({"status": "success"})
    
    def add_task(self, request: str) -> str:
        try:
            data = json.loads(request)
            title = data["title"]
            description = data["description"]
            user_id = data["user_id"]
            creation_time = data["creation_time"]
            board_id = data["board_id"]
        
            # Constraints
            if len(title) > 64:
                return json.dumps({"error": "title exceeds 64 characters"})
            if len(description) > 128:
                return json.dumps({"error": "description exceeds 128 characters"})
        
            if board_id not in self.boards:
                return json.dumps({"error": "board not found"})
            
            board = self.boards[board_id]
        
            if board["status"] != "OPEN":
                return json.dumps({"error": "can only add tasks to an OPEN board"})
        
            # Check for duplicate task titles within the same board
            if any(task["title"] == title for task in board["tasks"]):
                return json.dumps({"error": "task title must be unique for a board"})
        
            task_id = str(uuid.uuid4())
        
            # Add the new task to the board
            board["tasks"].append({
                "id": task_id,
                "title": title,
                "description": description,
                "user_id": user_id,
                "creation_time": creation_time,
                "status": "OPEN"
            })
        
            # Save the updated boards to file
            self.save_boards()
        
            return json.dumps({"id": task_id})
        except Exception as e:
            return json.dumps({"error": f"Failed to add task: {str(e)}"})
    
    def update_task_status(self, request: str):
        data = json.loads(request)
        task_id = data["id"]
        status = data["status"]
        
        for board in self.boards.values():
            for task in board["tasks"]:
                if task["id"] == task_id:
                    task["status"] = status
                    self.save_boards()
                    return json.dumps({"status": "success"})
        
        return json.dumps({"error": "task not found"})
    
    def list_boards(self, request: str) -> str:
        data = json.loads(request)
        team_id = data["id"]
        
        boards_list = [
            {
                "id": board_id,
                "name": board["name"]
            }
            for board_id, board in self.boards.items()
            if board["team_id"] == team_id and board["status"] == "OPEN"
        ]
        return json.dumps(boards_list)
    
    def export_board(self, request: str) -> str:
        data = json.loads(request)
        board_id = data["id"]
        
        if board_id not in self.boards:
            return json.dumps({"error": "board not found"})
        
        board = self.boards[board_id]
        output = f"Board Name: {board['name']}\n"
        output += f"Description: {board['description']}\n"
        output += f"Creation Time: {board['creation_time']}\n"
        output += f"Status: {board['status']}\n"
        output += f"Tasks:\n"
        
        for task in board["tasks"]:
            output += f"\tTask Title: {task['title']}\n"
            output += f"\tDescription: {task['description']}\n"
            output += f"\tAssigned User: {task['user_id']}\n"
            output += f"\tCreation Time: {task['creation_time']}\n"
            output += f"\tStatus: {task['status']}\n"
            output += "\n"
        
        out_file = f"out/{board_id}.txt"
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, 'w') as file:
            file.write(output)
        
        return json.dumps({"out_file": out_file})

# Example usage
project_board_base = ProjectBoardBase()

# Create a board
request_create_board = json.dumps({
    "name": "Board Alpha",
    "description": "Board for Alpha project",
    "team_id": "team_alpha",
    "creation_time": datetime.now().isoformat()
})
response_create_board = project_board_base.create_board(request_create_board)
print(response_create_board)

# Check if board creation was successful
response_data_board = json.loads(response_create_board)
if "id" in response_data_board:
    board_id = response_data_board["id"]

    # Add a task to the board
    request_add_task = json.dumps({
        "title": "Task 1",
        "description": "First task for Board Alpha",
        "user_id": "user_alpha",
        "creation_time": datetime.now().isoformat(),
        "board_id": board_id
    })
    response_add_task = project_board_base.add_task(request_add_task)
    print(response_add_task)
    
    # List boards for the team
    request_list_boards = json.dumps({"id": "team_alpha"})
    print(project_board_base.list_boards(request_list_boards))
    
    # Export board to a file
    request_export_board = json.dumps({"id": board_id})
    print(project_board_base.export_board(request_export_board))

    # Update task status
    response_data_task = json.loads(response_add_task)
    if "id" in response_data_task:
        task_id = response_data_task["id"]
        request_update_task = json.dumps({"id": task_id, "status": "COMPLETE"})
        print(project_board_base.update_task_status(request_update_task))
    
    # Close the board
    request_close_board = json.dumps({"id": board_id})
    print(project_board_base.close_board(request_close_board))

else:
    print("Board creation failed:", response_create_board)
