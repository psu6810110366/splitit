from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

_SEL_COLOR = [0.196, 0.784, 0.471, 0.18]
_UNSEL_COLOR = [0.953, 0.961, 0.973, 1.0]


class PersonToggleRow(MDCard):
    display_name = StringProperty('')
    first_letter = StringProperty('?')
    is_selected = BooleanProperty(True)
    check_opacity = NumericProperty(1.0)

    def on_display_name(self, instance, value):
        self.first_letter = value[:1].upper() if value else '?'

    def on_is_selected(self, instance, value):
        self.md_bg_color = _SEL_COLOR if value else _UNSEL_COLOR
        self.check_opacity = 1.0 if value else 0.0

    def toggle(self):
        self.is_selected = not self.is_selected
