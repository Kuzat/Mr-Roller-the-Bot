set -e -x

cd Mr-Roller-the-Bot
kill "$(ps -ef | grep '[r]oller_bot.main' | awk '{print $2}')"
poetry run backup
git pull
poetry install
nohup poetry run bot &
