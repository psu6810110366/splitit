from kivy.properties import StringProperty, ListProperty
from kivymd.uix.card import MDCard

_ACTIVE = [0.957, 0.349, 0.145, 1.0]   # #F45925 orange
_INACTIVE = [0.580, 0.635, 0.722, 1.0]  # #94A3B8 grey


class BottomNav(MDCard):
    active_tab = StringProperty('home')
    home_icon_color = ListProperty(_ACTIVE)
    friends_icon_color = ListProperty(_INACTIVE)
    settings_icon_color = ListProperty(_INACTIVE)

    def on_active_tab(self, instance, value):
        self.home_icon_color = _ACTIVE if value == 'home' else _INACTIVE
        self.friends_icon_color = _ACTIVE if value == 'friends' else _INACTIVE
        self.settings_icon_color = _ACTIVE if value == 'settings' else _INACTIVE
