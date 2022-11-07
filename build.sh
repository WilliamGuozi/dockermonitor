#!/bin/bash
#
# Created by William Guozi
#

# venv and generate requirement
source ~/venv/$(basename "$PWD")/bin/activate
pip3 freeze > requirement

# push with commit
git add .
minsec=$(date "+%H-%M")
git commit -m "update $minsec"
git push

# push with tag
versionCommit=$(git rev-parse --short=8 HEAD)
versionDate=$(git log --pretty=format:"%ad" --date=short | head -1)
version=v$versionCommit-$versionDate
git tag -a $version -m "auto tag $version"
git push origin --tags


export version=v$versionCommit-$versionDate
