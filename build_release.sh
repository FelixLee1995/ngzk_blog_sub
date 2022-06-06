rm -rf dist
source venv/Scripts/activate
pyinstaller -F --clean main.py
mkdir -p dist/images
cp config.yaml dist/
cp readme.md dist/
mv dist/main.exe   dist/blog_subscribe.exe
tar -czvf 乃木坂博客订阅提醒工具.tar.gz dist
rm main.spec