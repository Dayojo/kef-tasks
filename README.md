# kef-tasks

A collection of Python utilities for file management and automation.

## Repository Structure

```
kef-tasks/
├── file_checker/
│   ├── file_type_checker.py
│   ├── README.md
│   └── source_folder/
│       ├── alpha.hpp, beta.c, charlie.py, ...
│       ├── dev/, int/, prod/, qa/ (subdirectories)
├── open_terminal/
│   ├── open_terminal.py
│   └── README.md
└── README.md
```

## Projects

### 1. file_checker

- **file_type_checker.py**: Scans a directory (optionally recursively) and prints the type of each recognized source file (C, C++, Python, Java, Matlab).
- **source_folder/**: Example directory structure with various file types and nested subdirectories for testing.
- See `file_checker/README.md` for usage instructions and test scenarios.

### 2. open_terminal

- **open_terminal.py**: Opens a new Windows command prompt window with a custom title.
- See `open_terminal/README.md` for usage details.

## Getting Started

- Requires Python 3.x and Windows OS.
- Each project contains its own README with detailed instructions.
