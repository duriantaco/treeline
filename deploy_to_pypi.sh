#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting deployment to PyPI...${NC}"

echo -e "${GREEN}Cleaning up old build artifacts...${NC}"
rm -rf dist/ build/ *.egg-info/

echo -e "${GREEN}Building source and wheel distributions...${NC}"
python3 setup.py sdist bdist_wheel

echo -e "${GREEN}Checking the distributions with Twine...${NC}"
twine check dist/*

echo -e "${GREEN}Uploading to PyPI...${NC}"
twine upload dist/*

echo -e "${GREEN}Deployment successful! Your package is live on PyPI.${NC}"

exit 0
