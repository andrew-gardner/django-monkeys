# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

BU=$DIR/backup
stamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
dst=$BU/db-$stamp.sqlite3
echo "Timestamp: $stamp"

mkdir -p $BU
cp db.sqlite3 $dst
echo "Saved: $dst"

