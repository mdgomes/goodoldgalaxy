# Variables
cd "$(dirname "$0")"/..

IMAGE="screenshot.jpg"

# Delete the old screenshot
rm -f ${IMAGE}

# Start goodoldgalaxy
bin/goodoldgalaxy &

# Wait for goodoldgalaxy
sleep 5s

# Get the window id
WID="$(xwininfo -tree -root|grep goodoldgalaxy|tail -1|awk '{print $1}')"

# Make the screenshot
import -window "${WID}" -strip -trim "${PWD}/${IMAGE}" && kill %1
