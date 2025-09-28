import subprocess
import sys

def open_terminal(title):
    """
    Opens a new Windows command prompt window with the specified title.
    """
    cmd = f'start "{title}" cmd /k title {title}'
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 open_terminal.py "TERMINAL NAME"')
        sys.exit(1)
    title = sys.argv[1]
    open_terminal(title)