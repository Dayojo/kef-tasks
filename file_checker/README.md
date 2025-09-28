# file_type_checker.py

This script identifies and prints the type of source code files in a given directory, supporting both root-level and recursive (subdirectory) checks.

## Features
- Detects file types: C, C++, Python, Java, Matlab (by extension)
- Can check only the specified directory or recursively include all subdirectories
- Prints a message for each recognized file type

## Directory Structure Example

```
file_checker/
├── file_type_checker.py
├── source_folder/
│   ├── alpha.hpp
│   ├── beta.c
│   ├── charlie.py
│   ├── debug.cpp
│   ├── delta.java
│   ├── gamma.h
│   ├── tango.m
│   ├── dev/
│   │   ├── dev_a.cpp
│   │   └── dev_b.hpp
│   ├── int/
│   │   ├── int_a.js
│   │   └── int_b.py
│   ├── prod/
│   │   ├── prod_a.java
│   │   └── prod_b.go
│   └── qa/
```

## Usage

```sh
python file_type_checker.py [folder] [--recursive]
```

- `[folder]`: Path to the directory to check (e.g., `source_folder`)
- `--recursive`: (Optional) Recursively check all subdirectories

## Example Tests

### 1. Root Level Directory
To check only the files directly inside `source_folder`:

```sh
python file_type_checker.py source_folder
```
**Expected Output:**
```
source_folder/alpha.hpp: This is a c++ file!
source_folder/beta.c: This is a c file!
source_folder/charlie.py: This is a python file!
source_folder/debug.cpp: This is a c++ file!
source_folder/delta.java: This is a java file!
source_folder/gamma.h: This is a c file!
source_folder/tango.m: This is a matlab file!
```

### 2. Subdirectories (Recursive)
To check all files, including those in subdirectories like `dev`, `int`, `prod`, and `qa`:

```sh
python file_type_checker.py source_folder --recursive
```
**Expected Output (partial):**
```
source_folder/alpha.hpp: This is a c++ file!
source_folder/dev/dev_a.cpp: This is a c++ file!
source_folder/dev/dev_b.hpp: This is a c++ file!
source_folder/int/int_b.py: This is a python file!
source_folder/prod/prod_a.java: This is a java file!
... (other recognized files)
```

### 3. Nested Subdirectories
The script will also check files in nested subdirectories (e.g., `dev`, `int`, `prod`, `qa`) when `--recursive` is used.

## Notes
- Only files with recognized extensions will be reported.
- Unrecognized files are ignored.
- Handles permission errors and invalid directories gracefully.
