from kivy.uix.screenmanager import Screen

class SummaryScreen(Screen):
    def on_save_and_finish(self):
        """Callback: บันทึกข้อมูลบิลลงระบบ (SQLite) และจบงาน"""
        print("Saving bill to database...")
        # self.manager.current = 'result_screen' หรือ 'dashboard_screen'
