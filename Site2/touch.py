import sys
from datetime import datetime

def main():
    if len(sys.argv) != 2:
        print("Usage: python touch_file.py <name>")
        sys.exit(1)

    name = sys.argv[1]
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M")
    filename = f"{name}-{date_str}-{time_str}.md"

    with open(filename, 'w'):
        pass  # Create the file

    print(f"Created: {filename}")

if __name__ == "__main__":
    main()