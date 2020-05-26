#!/bin/sh
if test -f "../bot.log"; then
    rm ../bot.log
fi
nohup python3 -u index.py > bot.log &