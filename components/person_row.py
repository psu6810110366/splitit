from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ObjectProperty


class PersonRow(MDCard):
    display_name = StringProperty('')
    first_letter = StringProperty('?')
    remove_cb = ObjectProperty(None, allownone=True)

    def on_display_name(self, instance, value):
        self.first_letter = value[:1].upper() if value else '?'

    def do_remove(self):
        if self.remove_cb:
            self.remove_cb()
