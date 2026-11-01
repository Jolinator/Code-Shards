#https://www.codewars.com/api/v1/code-challenges/{challenge}
from pathlib import Path
import requests
from validate_solutions import *


own_path = Path(__file__).parent
problem_path = own_path / "Problems"




replace_name_dir = {
    " ": "_",
    "-": "_",
    "!": "",
    ".": "",
    ",": "",
    ":": "",
    ";": ""
}   

def replace_name(name):
    if not name:
        return name
    if name:
        for old, new in replace_name_dir.items():
            name = name.replace(old, new)
    return name

Tasks = {}

class Task:

    @classmethod
    def get(cls, id):
        if id in Tasks:
            return Tasks[id]
        return cls(id)

    def __init__(self, id):
        if id in Tasks:
            raise Exception(f"Task {id} already exists")
        self.id = id
        self.url = f"https://www.codewars.com/api/v1/code-challenges/{id}"
        self.request = None
        self.valid = False
        self.name = None
        self.description = None
        self.rank = None
        self.tags = None
        self.challenge_languages = None
        self.dir_path = None
        self.file_solution_dirs = None
        self.file_solution_files = None
        self.created = False
        self.created_languages = set()
        Tasks[id] = self

        
    def is_fetched(self):
        return self.request is not None and self.valid

    def fetch(self):
        if self.is_fetched():
            return self.request
        self.request = requests.get(self.url)
        if self.request.status_code != 200:
            raise Exception(f"Failed to fetch task {self.id}: {self.request.status_code}")
        self.parse()
        self.validate()
        return self.request

    def parse(self):
        if self.request is None:
            self.fetch()
        data = self.request.json()
        self.name = replace_name(data.get("name"))
        self.description = data.get("description")
        self.rank = data.get("rank")
        self.tags = data.get("tags")
        self.challenge_languages = data.get("languages")

    def validate(self):
        if any(attr is None for attr in [self.name, self.description, self.rank, self.tags, self.challenge_languages]):
            raise Exception(f"Task {self.id} is not fully parsed")
        self.valid = True

    def is_created(self, languages = None):
        if languages is None:
            return self.created
        return self.created and all(lang in self.created_languages for lang in languages)

    def create_dir(self, languages):
        if self.is_created(languages):
            return

        self.fetch()
        if not self.is_fetched():
            raise Exception(f"Task {self.id} has not been fetched")
        
        self.dir_path = problem_path / self.name

        file_solution_base = self.dir_path / "solution"
        self.file_solution_dirs = []
        self.file_solution_files = []
        for lang in languages:
            self.file_solution_dirs.append(file_solution_base / lang)
            self.file_solution_files.append(self.file_solution_dirs[-1] / f"solution.{language_to_filetype[lang]}")
        
        self.description_path = str(self.dir_path / "task.md")
        if not self.dir_path.exists():
            self.dir_path.mkdir(parents=True, exist_ok=True)
        for dir in self.file_solution_dirs:
            if not dir.exists():
                dir.mkdir(parents=True, exist_ok=True)
        for file in self.file_solution_files:
            if not file.exists():
                file.touch()
            else:
                if not validate_file(file):
                    print(f"WARNING: Invalid language file: {file}")
        with open(self.description_path, "w", encoding="utf-8") as f:
            f.write(self.description)
        self.created = True
        for lang in languages:
            self.created_languages.add(lang)


class User:

    def __init__(self, username=None, id=None):
        if not username and not id:
            raise ValueError("Either username or id must be provided")
        self.username = username
        self.id = id
        self.name = None
        self.honor = None
        self.clan = None
        self.leaderboard_position = None
        self.skills = None
        self.languages = set()
        self.user_url = f"https://www.codewars.com/api/v1/users/{username or id}"
        self.challenges_url = f"https://www.codewars.com/api/v1/users/{username or id}/code-challenges/completed"
        self.ids = set()
        self.completed_languages_per_id = {}
        self.valid = False

    def is_fetched(self):
        return self.ids and self.valid

    def fetch(self):
        if self.is_fetched():
            return self.ids
        user_response = requests.get(self.user_url)
        if user_response.status_code != 200:
            raise Exception(f"Failed to fetch user data: {user_response.status_code}")
        user_data = user_response.json()
        self.name = user_data.get("name")
        self.name = replace_name(user_data.get("name"))
        self.honor = user_data.get("honor")
        self.clan = user_data.get("clan")
        self.leaderboard_position = user_data.get("leaderboardPosition")
        self.skills = user_data.get("skills")
        for lang in user_data.get("ranks", {}).get("languages", {}):
            self.languages.add(lang)

        challenges_response = requests.get(self.challenges_url)
        if challenges_response.status_code != 200:
            raise Exception(f"Failed to fetch challenges data: {challenges_response.status_code}")
        challenges_data = challenges_response.json()
        if not challenges_data.get("data"):
            raise Exception("No challenges data found")
        for challenge in challenges_data.get("data", []):
            self.ids.add(challenge.get("id"))
            self.completed_languages_per_id[challenge.get("id")] = set(challenge.get("completedLanguages", []))

        self.valid = True
        return self.ids

    def create_dirs(self):
        self.fetch()
        for id in self.ids:
            task = Task.get(id)
            task.create_dir(self.languages)

def validate_all_solutions():
    failed = False
    supported_endings = set()
    for lang in supported_languages:
        supported_endings.add(language_to_filetype[lang])

    files = sorted(problem_path.rglob("*.*"))
    if not files:
        print(f"No files found in {problem_path}")
        return

    for file in files:
        if file.suffix[1:] in supported_endings:
            if not validate_file(file):
                failed = True
    if failed:
        print("Some solutions failed validation.")
    else:
        print("All solutions passed validation.")

if __name__ == "__main__":
    options = f'''
1 - Fetch and create directories for a user
2 - Validate solutions in supported languages: {', '.join(supported_languages)}
3 - Create directory for task ID
4 - Exit
'''
    if not problem_path.exists():
        problem_path.mkdir(parents=True, exist_ok=True)
    while True:
        print(options)
        choice = input("Enter your choice: ")
        if choice == "1":
            username = input("Enter Codewars username: ")
            user = User(username=username)
            user.create_dirs()
        elif choice == "2":
            validate_all_solutions()
        elif choice == "3":
            task_id = input("Enter task ID: ")
            task = Task.get(task_id)
            task.create_dir(supported_languages)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


        
        

    



