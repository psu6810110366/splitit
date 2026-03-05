from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from core.models import Friend


class FriendsScreen(Screen):
    friends_list = ListProperty([])
    dialog = None

    def on_enter(self, *args):
        self.load_friends()

    def load_friends(self):
        """ดึงรายชื่อเพื่อนจาก DB แล้วอัปเดต list"""
        try:
            friends = Friend.select().order_by(Friend.name)
            data = []
            for f in friends:
                initials = f.name[:2].upper() if f.name else "??"
                data.append({
                    "name": f.name,
                    "avatar_initials": initials,
                    "avatar_color": f.avatar_color,
                    "balance_text": "Settled up",
                    "balance_color": "#BDBDBD"
                })
            self.friends_list = data
        except Exception as e:
            print(f"[Friends] Error loading friends: {e}")

    def open_add_friend_dialog(self):
        if not self.dialog:
            self.name_input = MDTextField(
                hint_text="Friend's Name",
                size_hint_x=1
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
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="ADD",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_release=self.add_friend_action
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
        try:
            Friend.create(name=name)
            self.dialog.dismiss()
            toast(f"Added {name} to friends!")
            self.load_friends()
        except Exception as e:
            print(f"[Friends] Error adding friend: {e}")
            toast("Failed to add friend")

    def go_back(self):
        self.manager.current = 'dashboard'

    def go_to_dashboard(self):
        self.manager.current = 'dashboard'

    def go_to_scan(self):
        self.manager.current = 'scan_screen'
