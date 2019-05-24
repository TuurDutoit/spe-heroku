# Run the following command in your terminal to export the variables in .env
sed 's/^/export /' .env > .env.sh
set -a
source .env.sh
rm .env.sh