#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Please provide a version number"
    echo "Usage: ./tag-release.sh <version-number>"
    echo "Example: ./tag-release.sh 1.0.0"
    exit 1
fi

VERSION=$1

# Validate version number format (x.x.x)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version number must be in format x.x.x (e.g., 1.0.0)"
    exit 1
fi

echo "About to create and push tag v$VERSION"
read -p "Continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Operation cancelled"
    exit 0
fi

echo "Creating tag v$VERSION..."
git tag "v$VERSION"

echo "Pushing tag to remote..."
git push origin "v$VERSION"

echo "✅ Successfully created and pushed tag v$VERSION"
