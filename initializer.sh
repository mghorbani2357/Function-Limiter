coverage run -m unittest tests/limiter.py
coverage xml
bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r coverage.xml

git commit -m "Update coverage"

# shellcheck disable=SC2162
read -p "Please enter tag: " git_tag
git commit tag "$git_tag"
git push

python3 setup.py sdist bdist_wheel
twine check dist/*

# shellcheck disable=SC2162
read -n 1 -p "Do you want to upload to pypi repository? (Yes/No): " confirm

# shellcheck disable=SC2086
if [ $confirm == "y" ] || [ $confirm == "Y" ]; then

  python3 -m twine upload --repository pypi dist/*

fi
