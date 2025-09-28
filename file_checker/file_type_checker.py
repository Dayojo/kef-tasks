import os
import sys

POPUP_MSG = {
    '.cpp': "This is a c++ file!",
    '.hpp': "This is a c++ file!",
    '.c': "This is a c file!",
    '.h': "This is a c file!",
    '.py': "This is a python file!",
    '.java': "This is a java file!",
    '.m': "This is a matlab file!"
}

def check_files(folder, recursive=False):
    # Iterates through files in the specified folder (and subfolders, if recursive),
    # and prints a message for files of recognized types.
    try:
        if not os.path.isdir(folder):
            print(f"Error: '{folder}' is not a valid directory.")
            return

        if recursive:
            for root, _, files in os.walk(folder):
                for f in files:
                    try:
                        ext = os.path.splitext(f)[1]
                        if ext in POPUP_MSG:
                            print(f"{os.path.join(root, f)}: {POPUP_MSG[ext]}")
                    except Exception as e:
                        print(f"Error processing file '{f}': {e}")
        else:
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                if os.path.isfile(path):
                    try:
                        ext = os.path.splitext(f)[1]
                        if ext in POPUP_MSG:
                            print(f"{path}: {POPUP_MSG[ext]}")
                    except Exception as e:
                        print(f"Error processing file '{f}': {e}")

    except PermissionError:
        print(f"Error: Permission denied accessing '{folder}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python file_type_checker.py [folder] [--recursive]")
        sys.exit(1)
    folder = sys.argv[1]
    recursive = '--recursive' in sys.argv
    check_files(folder, recursive)