#!/bin/sh

NAME="zak"
EMAIL="nobody@exmaple.com"

git config user.name $NAME
git config user.email $EMAIL

echo $(git config user.name) $(git config user.email)
