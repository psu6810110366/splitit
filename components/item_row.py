from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty, ObjectProperty


class ItemRow(MDCard):
    item_name = StringProperty('')
    price = NumericProperty(0.0)
    price_text = StringProperty('฿0.00')
    delete_cb = ObjectProperty(None, allownone=True)

    def on_price(self, instance, value):
        self.price_text = '฿' + '{:.2f}'.format(value)

    def do_delete(self):
        if self.delete_cb:
            self.delete_cb()
