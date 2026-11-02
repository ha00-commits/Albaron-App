[app]
title = Albaron
package.name = albaron
package.domain = org.albaron

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 1.0

requirements = python3,kivy==2.2.1,telethon,pycryptodome,requests
orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# اختيار ملف التشغيل
android.entrypoint = org.kivy.android.PythonActivity
p4a.bootstrap = sdl2
