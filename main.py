import os
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# นำเข้าโมเดลและระบบฐานข้อมูล (Import db logic)
from core.models import initialize_db

# นำเข้าหน้าจอต่างๆ (Import screens)
from screens.dashboard_screen import DashboardScreen
# หมายเหตุ: นำเข้าหน้าอื่นเพิ่มในอนาคต (scan, new_split, summary)

class SplitItApp(MDApp):
    def build(self):
        # 1. ตั้งค่าโทนสี (Setup KivyMD Color Palette)
        # Primary: #00C853 (Green), Secondary: #FF6B6B (Red)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.theme_style = "Light"
        
        # 2. โหลดไฟล์ UI ทั้งหมด (.kv files)
        kv_dir = os.path.join(os.path.dirname(__file__), 'kv')
        Builder.load_file(os.path.join(kv_dir, 'dashboard.kv'))
        
        # 3. สร้างระบบนไทางหน้าจอ (ScreenManager)
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        
        return sm
        
    def on_start(self):
        """ทำงานทันทีที่แอปเปิด (Run right after app starts)"""
        # สร้างตาราง Sqlite (Initialize DB)
        initialize_db()
        print("Database initialized successfully.")

if __name__ == '__main__':
    SplitItApp().run()
