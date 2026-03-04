import os
from dotenv import load_dotenv

# โหลด API Key จากไฟล์ .env อัตโนมัติเวลาเปิดแอป
load_dotenv()

from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# นำเข้าโมเดลและระบบฐานข้อมูล (Import db logic)
from core.models import initialize_db

# ── Register Thai font (Sarabun) ────────────────────────────────────────────
_fonts_dir = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
LabelBase.register(
    name='Sarabun',
    fn_regular=os.path.join(_fonts_dir, 'Sarabun-Regular.ttf'),
    fn_bold=os.path.join(_fonts_dir, 'Sarabun-Bold.ttf'),
)
# ────────────────────────────────────────────────────────────────────────────

# นำเข้าหน้าจอต่างๆ (Import screens)
from screens.dashboard_screen import DashboardScreen
from components.bottom_nav import BottomNav  # noqa: F401
from components.add_friend_dialog import AddFriendDialog  # noqa: F401
from components.add_item_dialog import AddItemDialog  # noqa: F401
from components.item_row import ItemRow  # noqa: F401
from components.person_row import PersonRow  # noqa: F401
from components.assign_item_dialog import AssignItemDialog  # noqa: F401
from components.person_toggle_row import PersonToggleRow  # noqa: F401
from screens.scan_screen import ScanScreen
from screens.new_split_screen import NewSplitScreen
from screens.summary_screen import SummaryScreen
from screens.result_screen import ResultScreen
from screens.friends_screen import FriendsScreen
from screens.settings_screen import SettingsScreen

# Global KV rule: apply Sarabun to all text widgets that use font_name directly
Builder.load_string("""
<MDTextField>:
    font_name: 'Sarabun'
<TextInput>:
    font_name: 'Sarabun'
""")


class SplitItApp(MDApp):
    def build(self):
        # 1. ตั้งค่าโทนสี (Setup KivyMD Color Palette)
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Red"
        self.theme_cls.theme_style = "Light"

        # 2. ตั้ง Sarabun เป็น font สำหรับทุก font_style ใน KivyMD
        #    ยกเว้น 'Icon' — ต้องใช้ MaterialIcons font ของ KivyMD ต่อไป
        for style_name in list(self.theme_cls.font_styles.keys()):
            if style_name == 'Icon':
                continue
            entry = list(self.theme_cls.font_styles[style_name])
            entry[0] = 'Sarabun'
            self.theme_cls.font_styles[style_name] = entry
        
        # 2. โหลดไฟล์ UI ทั้งหมด (.kv files)
        kv_dir = os.path.join(os.path.dirname(__file__), 'kv')
        components_dir = os.path.join(os.path.dirname(__file__), 'components')
        Builder.load_file(os.path.join(components_dir, 'bottom_nav.kv'))
        Builder.load_file(os.path.join(components_dir, 'add_friend_dialog.kv'))
        Builder.load_file(os.path.join(components_dir, 'add_item_dialog.kv'))
        Builder.load_file(os.path.join(components_dir, 'item_row.kv'))
        Builder.load_file(os.path.join(components_dir, 'person_row.kv'))
        Builder.load_file(os.path.join(components_dir, 'person_toggle_row.kv'))
        Builder.load_file(os.path.join(components_dir, 'assign_item_dialog.kv'))
        Builder.load_file(os.path.join(kv_dir, 'dashboard.kv'))
        Builder.load_file(os.path.join(kv_dir, 'new_split.kv'))
        Builder.load_file(os.path.join(kv_dir, 'summary.kv'))
        Builder.load_file(os.path.join(kv_dir, 'result.kv'))
        Builder.load_file(os.path.join(kv_dir, 'scan.kv'))
        Builder.load_file(os.path.join(kv_dir, 'friends.kv'))
        Builder.load_file(os.path.join(kv_dir, 'settings.kv'))
        
        # 3. สร้างระบบนำทางหน้าจอ (ScreenManager)
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ScanScreen(name='scan_screen'))
        sm.add_widget(NewSplitScreen(name='new_split_screen'))
        sm.add_widget(SummaryScreen(name='summary_screen'))
        sm.add_widget(ResultScreen(name='result_screen'))
        sm.add_widget(FriendsScreen(name='friends_screen'))
        sm.add_widget(SettingsScreen(name='settings_screen'))
        
        return sm
        
    def on_start(self):
        """ทำงานทันทีที่แอปเปิด (Run right after app starts)"""
        # สร้างตาราง Sqlite (Initialize DB)
        initialize_db()
        print("Database initialized successfully.")

if __name__ == '__main__':
    SplitItApp().run()
