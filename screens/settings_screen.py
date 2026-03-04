from kivy.uix.screenmanager import Screen


class SettingsScreen(Screen):
    def go_back(self):
        self.manager.current = 'dashboard'
