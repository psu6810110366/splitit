from kivy.uix.screenmanager import Screen

class SummaryScreen(Screen):
    def go_back(self):
        self.manager.current = 'new_split_screen'

    def on_save_and_finish(self):
        """Callback: บันทึกข้อมูลบิลลงระบบ (SQLite) และจบงาน"""
        print("Saving bill to database...")
        # ในอนาคตต้องเอาข้อมูลจาก new_split_screen มาบันทึกเข้า DB
        # สำหรับตอนนี้ ให้เด้งกลับไปหน้า Home ก่อน
        self.manager.current = 'dashboard'
