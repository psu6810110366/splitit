from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from kivymd.toast import toast
import os

class SettingsScreen(Screen):
    def on_enter(self, *args):
        # โหลดค่า PromptPay จาก settings.json
        store = JsonStore('settings.json')
        if store.exists('user'):
            promptpay_no = store.get('user').get('promptpay', '')
            if 'promptpay_input' in self.ids:
                self.ids.promptpay_input.text = promptpay_no

    def save_promptpay(self):
        # บันทึกเบอร์ PromptPay ทันทีเมื่อผู้ใช้แก้ไขเสร็จ (on_text_validate or unfocus)
        if 'promptpay_input' not in self.ids:
            return
            
        promptpay_no = self.ids.promptpay_input.text.strip()
        store = JsonStore('settings.json')
        
        # ถ้ายาว 10 หรือ 13 หรือ 15 จะถือว่าครบถ้วน (เบอร์มือถือ หรือ บัตรประชาชน หรือ e-Wallet)
        # แต่เพื่อความสะดวก เราก็ให้บันทึกไปก่อน
        if store.exists('user'):
            user_data = store.get('user')
            user_data['promptpay'] = promptpay_no
            store.put('user', **user_data)
        else:
            store.put('user', promptpay_no=promptpay_no)
            
        toast("บันทึก PromptPay แล้ว")

    def go_back(self):
        self.manager.current = 'dashboard'
