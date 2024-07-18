#!/bin/sh

# 定义要删除的目录
dirs="./log ./model ./predictions ./summary"

# 打印警告信息
echo "WARNING: You are about to delete the following directories:"
for dir in $dirs; do
    echo " - $dir"
done

# 提示用户确认
read -p "Do you want to continue? (yes/no): " confirmation

# 根据用户输入决定是否删除
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
