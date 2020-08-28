set -e
set -o pipefail
python ./utils/genthumbnail.py
python ./utils/fillupload.py README.md
git add .
git commit -m 'common update'
git push