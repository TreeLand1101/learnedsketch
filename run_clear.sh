#!/bin/sh

dirs="./log ./model ./predictions ./summary"

echo "WARNING: You are about to delete the following directories:"
for dir in $dirs; do
    echo " - $dir"
done

read -p "Do you want to continue? (yes/no): " confirmation

if [ "$confirmation" = "yes" ]; then
    for dir in $dirs; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo "Deleted $dir"
        else
            echo "$dir does not exist"
        fi
    done
else
    echo "Operation cancelled"
fi
