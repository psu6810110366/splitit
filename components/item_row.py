from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty


class ItemRow(MDCard):
    item_name = StringProperty('')
    price = NumericProperty(0.0)
    price_text = StringProperty('฿0.00')
    assigned_to = ListProperty([])
    assigned_text = StringProperty('ทุกคน')
    delete_cb = ObjectProperty(None, allownone=True)
    assign_cb = ObjectProperty(None, allownone=True)

    def on_price(self, instance, value):
        self.price_text = '฿' + '{:,.2f}'.format(value)

    def on_assigned_to(self, instance, value):
        if not value:
            self.assigned_text = 'ทุกคน'
        elif len(value) == 1:
            self.assigned_text = value[0]
        elif len(value) == 2:
            self.assigned_text = value[0] + ', ' + value[1]
        else:
            self.assigned_text = value[0] + ' +' + str(len(value) - 1) + ' คน'

    def do_delete(self):
        if self.delete_cb:
            self.delete_cb()

    def do_assign(self):
        if self.assign_cb:
            self.assign_cb()
