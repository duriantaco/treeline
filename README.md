# treeline
A simple directory tree structure generator that can create ASCII tree representations and save them as markdown files.

## Installation

`pip install treeline`

## Usage

### As a python module 

```
# Generate and print tree structure
print(treeline("/path/to/directory"))

#Generate tree and save to markdown file
treeline("/path/to/directory", create_md=True)`
```

#### Example output:
```
my_project
├── src
│   ├── __init__.py
│   └── main.py
├── tests
│   └── test_main.py
├── README.md
└── setup.py
```

### In terminal 

1. `treeline # Show current directory tree`
2. `treeline /path/to/dir # Show specific directory tree`
3. `treeline -m # Create markdown file (tree.md)`
4. `treeline -i ".pyc,.git" # Ignore patterns`
5. `treeline -h # Show help message`

## Note

the .treeline-ignore will ignore whatever is in the folder. 

For example, if you were to put the treeline-ignore inside the src folder, only files within the src folder will be ignored


## Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b branch)
3. Commit your changes (git commit -m 'cool stuff')
4. Push to the branch (git push origin branch)
5. Open a Pull Request

## Author
Oha