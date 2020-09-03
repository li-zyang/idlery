set -e
set -o pipefail
python ./utils/genthumbnail.py
python ./utils/removeexif.py -s src/
python ./utils/fillupload.py README.md
python ./utils/convertcovers.py --modify-readme
git add README.md
git add covers
git add src
git add thumbnail
git commit -m 'common update'
git push