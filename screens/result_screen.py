from kivy.uix.screenmanager import Screen

class ResultScreen(Screen):
    def go_back(self):
        self.manager.current = 'summary_screen'

    def go_home(self):
        self.manager.current = 'dashboard'

    def on_copy_clipboard(self):
        """Callback: คัดลอกสรุปบิลไปแปะที่อื่น"""
        print("Copying bill text to clipboard...")
        
    def on_mark_paid(self, participant_id):
        """Callback: ติ๊กเพื่อให้รู้ว่าคนนี้จ่ายแล้ว"""
        print(f"Participant {participant_id} marked as PAID")
        
    def on_remind_press(self, name, amount):
        """Callback: คัดลอกข้อความทวงเงินส่งให้เพื่อนคนนึง"""
        print(f"Copying reminder for {name} to pay {amount}")
