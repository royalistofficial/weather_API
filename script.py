import os
import subprocess

if __name__ == "__main__":
    os.chdir("app")

    if not os.path.exists("db.sqlite3"):
        subprocess.run(["python", "manage.py", "makemigrations"])
        subprocess.run(["python", "manage.py", "migrate"])


    uvicorn_command = [
        "uvicorn",
        "app.asgi:application",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

    subprocess.run(uvicorn_command)
