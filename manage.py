import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_user():
    from scripts.create_user import run
    run()

def seed():
    from scripts.seed import run
    run()

COMMANDS = {
    "create_user": create_user,
    "seed": seed,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py <command>")
        print("Available commands:", ", ".join(COMMANDS.keys()))
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f"Unknown command: '{command}'")
        print("Available commands:", ", ".join(COMMANDS.keys()))
        sys.exit(1)

    COMMANDS[command]()
