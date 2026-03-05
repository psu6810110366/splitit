from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivymd.uix.card import MDCard

from core.storage import get_recent_bills, get_balance_summary


class BillCardItem(MDCard):
    """
    RecycleView item widget สำหรับแสดง bill card แต่ละอันใน Dashboard
    ข้อมูลจะถูก bind เข้ามาผ่าน data dict โดย RecycleView อัตโนมัติ
    """
    bill_id = NumericProperty(-1)
    title = StringProperty('')
    amount_label = StringProperty('')
    date_label = StringProperty('')
    status_label = StringProperty('')
    status_type = StringProperty('owed')  # 'owed' | 'owe'
    emoji = StringProperty('🍽️')



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
        
        # Get recent bills and format for the new design
        recent_bills = get_recent_bills(limit=10)
        
        if not recent_bills:
            self.recent_splits = []
        else:
            # Format existing bills for new design
            formatted_splits = []
            for bill in recent_bills:
                formatted_splits.append({
                    "bill_id": bill.get("bill_id", -1),
                    "title": bill.get("title", "Split Bill"),
                    "amount_label": bill.get('amount_label', "฿0"),
                    "date_label": bill.get("date_label", "Recent"),
                    "status_label": bill.get("status_label", "Split"),
                    "status_type": bill.get("status_type", "owed"),
                    "emoji": bill.get("emoji", "🍽️")
                })
            self.recent_splits = formatted_splits

    def on_bill_selected(self, bill_id):
        """เปิดดูรายละเอียดบิลเมื่อคลิกการ์ด"""
        print(f"[Dashboard] Selected bill {bill_id}")
        if bill_id < 0:
            return  # Sample data or invalid
        
        result_screen = self.manager.get_screen('result_screen')
        result_screen.bill_id = bill_id
        # ให้ on_enter ของ ResultScreen ไปโหลดข้อมูลจาก DB ต่อ
        self.manager.current = 'result_screen'



    def go_to_new_split(self):
        """นำทางไปหน้าสร้างบิลใหม่"""
        self.manager.current = 'new_split_screen'

    def go_to_scan(self):
        """นำทางไปหน้าสแกนใบเสร็จ"""
        self.manager.current = 'scan_screen'

    def go_to_friends(self):
        """นำทางไปหน้าคลังเพื่อน"""
        self.manager.current = 'friends_screen'

    def go_to_add_friend(self):
        """นำทางไปหน้ารายชื่อเพื่อน"""
        self.manager.current = 'friends_screen'
