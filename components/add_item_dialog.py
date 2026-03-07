from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty


class AddItemDialog(MDCard):
    callback = ObjectProperty(None)

    def confirm_add(self):
        name = self.ids.item_name_input.text.strip()
        price_text = self.ids.item_price_input.text.strip()
        if not name:
            return
        try:
            price = float(price_text.replace(',', ''))
        except ValueError:
            price = 0.0
        if self.callback:
            self.callback(name, price)
        self._dismiss()

    def cancel(self):
        self._dismiss()

    def _dismiss(self):
        parent = self.parent
        if parent:
            parent.remove_widget(self)
