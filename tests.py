import os
import subprocess

if __name__ == "__main__":
    os.chdir("app")

    if not os.path.exists("db.sqlite3"):
        subprocess.run(["python", "manage.py", "makemigrations"])
        subprocess.run(["python", "manage.py", "migrate"])


    subprocess.run(["python", "manage.py", "test", "main.tests"])
