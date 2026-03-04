from kivy.uix.screenmanager import Screen


class FriendsScreen(Screen):
    def go_back(self):
        self.manager.current = 'dashboard'
