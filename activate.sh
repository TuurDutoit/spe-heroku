echo 'Exporting environment variables from .env.local...'

if [ -f '.env.local' ]; then
    export $(cat .env.local | xargs)
    echo 'Done.'
else
    echo 'activate.sh: .env.local: No such file or directory' >&2
    exit 1
fi