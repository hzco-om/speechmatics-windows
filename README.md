### Speechmatics Batch Transcriber – Windows
1. دانلود `ffmpeg-7.1.1-essentials_build.zip` → فقط `bin/ffmpeg.exe` را کنار پروژه بگذارید.
2. `pip install -r requirements.txt`  (صرفاً برای توسعه)
3. API Token را در env یا `config.json` قرار دهید.
4. تست اجرا: `python speechmatics_batch_gui.py`
5. ساخت exe: `pyinstaller -y pyi-speechmatics.spec`
6. برای انتشار Installer: فایل `setup.iss` را در Inno Setup Compiler باز و Build کنید.
```
