from kivy.uix.modalview import ModalView
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from core.models import Friend
import os

# โหลด KV
kv_path = os.path.join(os.path.dirname(__file__), "select_friend_dialog.kv")
Builder.load_file(kv_path)

class SelectFriendItem(MDCard):
    name = StringProperty("")
    is_selected = BooleanProperty(False)
    avatar_color = StringProperty("#16A34A")

    def toggle_selection(self):
        self.is_selected = not self.is_selected
        # อัปเดตข้อมูลใน parent data list เพื่อให้ RecycleView จำสถานะได้
        rv = self.parent.parent
        for item in rv.data:
            if item['name'] == self.name:
                item['is_selected'] = self.is_selected
                break
        rv.refresh_from_data()

class SelectFriendDialog(ModalView):
    friends_data = ListProperty([])
    callback = ObjectProperty(None)  # ฟังก์ชันที่จะเรียกเมื่อยืนยัน

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_friends()

    def load_friends(self):
        """โหลดรายชื่อเพื่อนทั้งหมดจาก DB"""
        try:
            friends = Friend.select().order_by(Friend.name)
            data = []
            for f in friends:
                data.append({
                    "name": f.name,
                    "avatar_color": f.avatar_color or "#16A34A",
                    "is_selected": False
                })
            self.friends_data = data
        except Exception as e:
            print(f"[SelectFriend] Error loading DB: {e}")

    def add_custom_name(self):
        """กรณีพิมพ์ชื่อใหม่ที่ไม่มีในลิสต์ — จะบันทึกลง DB ทันทีเพื่อให้คราวหน้าเห็นเลย"""
        name = self.ids.new_name_input.text.strip()
        if not name:
            return
            
        # ตรวจสอบว่ามีในลิสต์หรือยัง
        for item in self.friends_data:
            if item['name'].lower() == name.lower():
                item['is_selected'] = True
                self.ids.friends_rv.refresh_from_data()
                self.ids.new_name_input.text = ""
                return
        
        # บันทึกลง Database จริงๆ
        try:
            import random
            colors = ["#16A34A", "#2563EB", "#D97706", "#7C3AED", "#DB2777"]
            color = random.choice(colors)
            Friend.create(name=name, avatar_color=color)
            
            # เพิ่มเข้าลิตส์ที่แสดงผลใน Dialog
            self.friends_data.insert(0, {
                "name": name,
                "avatar_color": color,
                "is_selected": True
            })
            self.ids.friends_rv.refresh_from_data()
            self.ids.new_name_input.text = ""
            from kivymd.toast import toast
            toast(f"Added {name} to your friends!")
        except Exception as e:
            print(f"[SelectFriend] Error saving new friend: {e}")

    def confirm_selection(self):
        selected_names = [item['name'] for item in self.friends_data if item['is_selected']]
        if self.callback:
            self.callback(selected_names)
        self.dismiss()
