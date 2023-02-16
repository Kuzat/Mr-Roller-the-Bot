set -e

# SSH into the server using the key in environment variable SSH_KEY
ssh-add - <<< "$SSH_KEY"
ssh "$REMOTE_USER"@"$REMOTE_HOST"
cd Mr-Roller-the-Bot
kill "$(ps -ef | grep '[r]oller_bot.main' | awk '{print $2}')"
poetry run backup
git pull
poetry install
nohup poetry run bot &
