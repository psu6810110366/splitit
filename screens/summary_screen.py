from kivy.uix.screenmanager import Screen

class SummaryScreen(Screen):
    def go_back(self):
        self.manager.current = 'new_split_screen'

    def on_copy_clipboard(self):
        print('Copying summary to clipboard...')

    def on_save_and_finish(self):
        """Callback: บันทึกข้อมูลบิลลงระบบ (SQLite) และจบงาน"""
        print("Saving bill to database...")
        # self.manager.current = 'result_screen' หรือ 'dashboard_screen'
