from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ListProperty

from core.storage import get_recent_bills, get_balance_summary


class DashboardScreen(Screen):
    """
    หน้าหลักของแอป — แสดง Balance Summary และ Recent Bills
    Data-flow: on_enter → load_dashboard_data → storage.py → DB → properties → KV binds
    """
    total_owed = NumericProperty(0.0)
    total_owe_me = NumericProperty(0.0)
    recent_splits = ListProperty([])

    def on_enter(self, *args):
        """รีโหลดข้อมูลจาก DB ทุกครั้งที่กลับมาหน้านี้"""
        self.load_dashboard_data()

    def load_dashboard_data(self):
        """
        ดึงข้อมูลจาก DB และอัปเดต properties
        KV จะ re-render อัตโนมัติเมื่อ properties เปลี่ยน
        """
        balance = get_balance_summary()
        self.total_owed = balance["total_owed"]
        self.total_owe_me = balance["total_owe_me"]
        self.recent_splits = get_recent_bills(limit=10)

    def go_to_new_split(self):
        """นำทางไปหน้าสร้างบิลใหม่"""
        self.manager.current = 'new_split_screen'

    def go_to_scan(self):
        """นำทางไปหน้าสแกนใบเสร็จ"""
        self.manager.current = 'scan_screen'

    def go_to_add_friend(self):
        """นำทางไปหน้าจัดการเพื่อน (Phase B — ของสรวิศ)"""
        print("[Dashboard] go_to_add_friend: Phase B not yet implemented")
