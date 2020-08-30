set -e
set -o pipefail
python ./utils/genthumbnail.py
python ./utils/fillupload.py README.md
git add README.md
git add covers
git add src
git add thumbnail
git commit -m 'common update'
git push