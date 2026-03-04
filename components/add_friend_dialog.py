from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty


class AddFriendDialog(MDCard):
    callback = ObjectProperty(None)

    def confirm_add(self):
        name = self.ids.friend_name_input.text.strip()
        if name and self.callback:
            self.callback(name)
        self._dismiss()

    def cancel(self):
        self._dismiss()

    def _dismiss(self):
        parent = self.parent
        if parent:
            parent.remove_widget(self)
