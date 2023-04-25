#!/usr/bin/env bash
set -e -x

cd Mr-Roller-the-Bot
BOT_PID="$(ps -ef | grep '[r]oller_bot.main' | awk '{print $2}')"
if [ -n "$BOT_PID" ]; then
  kill "$BOT_PID"
  poetry run backup
fi

git pull
poetry install
nohup poetry run bot > nohup.out 2> nohup.err < /dev/null &
