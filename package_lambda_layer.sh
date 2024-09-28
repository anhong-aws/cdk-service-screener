rm -rf ./lambda-code/layer-deps/python/lib/python3.10
pip install -r ./requirements.txt --target lambda-code/layer-deps/python/lib/python3.10/site-packages --upgrade
