# -*- coding: utf-8 -*-
import asyncio
import threading
import os
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

API_ID = 34631956
API_HASH = '698f653e51872719991eb0834b81dbe3'
SESSION_FILE = 'albaron_session'
WORDS_FILE = 'words.txt'

class AlbaronApp(App):
    def build(self):
        self.title = 'Albaron Clasher'
        self.client = None
        self.is_running = False
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.scroll = ScrollView(size_hint=(1, 0.5))
        self.log_label = Label(text="مرحباً بك في تطبيق Albaron\n", size_hint_y=None, halign='right', valign='top')
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        self.scroll.add_widget(self.log_label)
        layout.add_widget(self.scroll)
        
        self.phone_input = TextInput(hint_text='رقم الهاتف (+964...)', multiline=False, size_hint_y=None, height=40)
        self.code_input = TextInput(hint_text='الكود', multiline=False, size_hint_y=None, height=40)
        self.pass_input = TextInput(hint_text='كلمة السر (2FA)', password=True, multiline=False, size_hint_y=None, height=40)
        self.target_input = TextInput(hint_text='الهدف (@username أو -100...)', multiline=False, size_hint_y=None, height=40)
        self.speed_input = TextInput(hint_text='السرعة بالثواني (مثلاً 1)', multiline=False, size_hint_y=None, height=40)
        self.lines_input = TextInput(hint_text='عدد الكلمات (مثلاً 5)', multiline=False, size_hint_y=None, height=40)
        
        layout.add_widget(self.phone_input)
        layout.add_widget(self.code_input)
        layout.add_widget(self.pass_input)
        layout.add_widget(self.target_input)
        layout.add_widget(self.speed_input)
        layout.add_widget(self.lines_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.btn_login = Button(text='تسجيل الدخول')
        self.btn_login.bind(on_release=self.login_thread)
        self.btn_start = Button(text='بدء الإرسال', background_color=(0, 1, 0, 1))
        self.btn_start.bind(on_release=self.start_clash)
        self.btn_stop = Button(text='إيقاف', background_color=(1, 0, 0, 1))
        self.btn_stop.bind(on_release=self.stop_clash)
        
        btn_layout.add_widget(self.btn_login)
        btn_layout.add_widget(self.btn_start)
        btn_layout.add_widget(self.btn_stop)
        layout.add_widget(btn_layout)
        
        return layout

    def log(self, text):
        def update(dt):
            self.log_label.text += f"{text}\n"
            self.scroll.scroll_y = 0
        Clock.schedule_once(update, 0)

    def login_thread(self, instance):
        phone = self.phone_input.text.strip()
        code = self.code_input.text.strip()
        pw = self.pass_input.text.strip()
        if not phone:
            self.log("❌ اكتب رقم الهاتف أولاً")
            return
        threading.Thread(target=self.run_login, args=(phone, code, pw), daemon=True).start()

    def run_login(self, phone, code, pw):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_login(phone, code, pw))

    async def async_login(self, phone, code, pw):
        self.log("⏳ جاري الاتصال...")
        try:
            self.client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                if not code:
                    sent = await self.client.send_code_request(phone)
                    self.log("📩 تم إرسال الكود. اكتبه بالخانة واضغط دخول.")
                    return
                try:
                    await self.client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    if not pw:
                        self.log("🔒 الحساب محمي بكلمة سر. اكتبها واضغط دخول.")
                        return
                    await self.client.sign_in(password=pw)
            
            me = await self.client.get_me()
            self.log(f"✅ تم الدخول: {me.first_name}")
        except Exception as e:
            self.log(f"❌ خطأ: {e}")

    def start_clash(self, instance):
        if not self.client:
            self.log("❌ سجل دخول أولاً")
            return
        target = self.target_input.text.strip()
        if not target:
            self.log("❌ حدد الهدف")
            return
        self.is_running = True
        threading.Thread(target=self.clash_loop, daemon=True).start()

    def stop_clash(self, instance):
        self.is_running = False
        self.log("🔴 تم إيقاف الإرسال")

    def clash_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_clash())

    async def async_clash(self):
        try:
            speed = float(self.speed_input.text or 1)
            lines = int(self.lines_input.text or 5)
            target = self.target_input.text.strip()
            
            words = []
            if os.path.exists(WORDS_FILE):
                with open(WORDS_FILE, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip()]
            if not words:
                self.log("❌ ملف الكلمات فاضي أو غير موجود")
                return
            
            self.log("🚀 بدأ الإرسال...")
            while self.is_running:
                msg = " ".join(random.sample(words, min(len(words), lines * 3)))
                try:
                    await self.client.send_message(target, msg)
                    self.log(f"✅ أُرسل: {msg[:20]}...")
                except Exception as e:
                    self.log(f"⚠️ خطأ: {e}")
                await asyncio.sleep(speed)
        except Exception as e:
            self.log(f"❌ خطأ: {e}")

if __name__ == '__main__':
    AlbaronApp().run()
