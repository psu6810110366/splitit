from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from peewee import fn
from core.models import Friend


class FriendsScreen(Screen):
    """
    หน้าจัดการเพื่อน — แสดงรายชื่อเพื่อนทั้งหมดพร้อมยอดค้างชำระ
    Data-flow: on_enter → load_friends() → DB query → friends_list → KV RecycleView

    Properties:
        friends_list (ListProperty): รายการ dict ของข้อมูลเพื่อน ที่ bind กับ RecycleView
        dialog (MDDialog | None): Dialog สำหรับเพิ่มเพื่อนใหม่ (lazy-init)
    """

    friends_list = ListProperty([])
    dialog = None

    def on_enter(self, *args):
        """รีโหลดรายชื่อเพื่อนจาก DB ทุกครั้งที่เข้าหน้านี้"""
        self.load_friends()

    def load_friends(self):
        """ดึงรายชื่อเพื่อนจาก DB แล้วอัปเดต list"""
        try:
            from core.models import BillParticipant

            friends = Friend.select().order_by(Friend.name)
            data = []

            for f in friends:
                initials = f.name[:2].upper() if f.name else "??"

                # คำนวณยอดค้างจ่ายของเพื่อนคนนี้ (เพื่อนติดหนี้เรา ในบิลที่เราเป็นเจ้าของ)
                # ในที่นี้ตัวอย่างง่ายๆ คือหาบิลที่คนนี้ยังไม่จ่าย และเรา (Me) เป็นคนสร้าง
                unpaid_total = (
                    BillParticipant.select(fn.SUM(BillParticipant.amount_owed))
                    .where(
                        (BillParticipant.display_name == f.name)
                        & (BillParticipant.is_paid == False)  # noqa: E712
                    )
                    .scalar()
                    or 0.0
                )

                if unpaid_total > 0:
                    balance_text = f"Owes you ฿{unpaid_total:,.2f}"
                    balance_color = "#E11D48"  # แดง
                else:
                    balance_text = "Settled up"
                    balance_color = "#6B7280"  # เทา

                data.append(
                    {
                        "name": f.name,
                        "avatar_initials": initials,
                        "avatar_color": f.avatar_color or "#16A34A",
                        "balance_text": balance_text,
                        "balance_color": balance_color,
                    }
                )
            self.friends_list = data
        except Exception as e:
            print(f"[Friends] Error loading friends: {e}")

    def open_add_friend_dialog(self):
        """เปิด dialog สำหรับเพิ่มเพื่อนใหม่ (สร้าง dialog ครั้งแรกแบบ lazy-init)"""
        if not self.dialog:
            self.name_input = MDTextField(
                hint_text="Friend's Name",
                helper_text="e.g. John Doe",
                helper_text_mode="on_focus",
                size_hint_x=1,
            )
            app = MDApp.get_running_app()
            self.dialog = MDDialog(
                title="Add a Friend",
                type="custom",
                content_cls=self.name_input,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.error_color,
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                    MDFlatButton(
                        text="ADD",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.add_friend_action,
                    ),
                ],
            )
        self.name_input.text = ""
        self.dialog.open()

    def add_friend_action(self, *args):
        name = self.name_input.text.strip()
        if not name:
            toast("Name cannot be empty")
            return

        # ป้องกันชื่อซ้ำ
        if Friend.select().where(Friend.name == name).exists():
            toast(f"{name} is already your friend!")
            return

        try:
            import random

            colors = ["#16A34A", "#2563EB", "#D97706", "#7C3AED", "#DB2777"]
            Friend.create(name=name, avatar_color=random.choice(colors))
            self.dialog.dismiss()
            toast(f"Added {name} to friends!")
            self.load_friends()
        except Exception as e:
            print(f"[Friends] Error adding friend: {e}")
            toast("Failed to add friend")

    def go_back(self):
        """ย้อนกลับไปหน้า Dashboard"""
        self.manager.current = "dashboard"

    def go_to_dashboard(self):
        """นำทางไปหน้า Dashboard"""
        self.manager.current = "dashboard"

    def go_to_scan(self):
        """นำทางไปหน้าสแกนใบเสร็จ"""
        self.manager.current = "scan_screen"
