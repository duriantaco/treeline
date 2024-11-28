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

## Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b branch)
3. Commit your changes (git commit -m 'cool stuff')
4. Push to the branch (git push origin branch)
5. Open a Pull Request

## Author
Oha