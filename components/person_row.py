from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty


class PersonRow(MDCard):
    display_name = StringProperty('')
    first_letter = StringProperty('?')
    amount = StringProperty('0.00')
    is_custom_mode = BooleanProperty(False)
    remove_cb = ObjectProperty(None, allownone=True)
    on_amount_change = ObjectProperty(None, allownone=True)

    def on_display_name(self, instance, value):
        self.first_letter = value[:1].upper() if value else '?'

    def do_remove(self):
        if self.remove_cb:
            self.remove_cb()

    def on_text_validate(self, text):
        if self.on_amount_change:
            self.on_amount_change(text)
