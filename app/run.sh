#/bin/bash

nohup python ./server.py 1>./logs/stdout.log 2>./logs/stderr$(date +%Y%m%d).log &
