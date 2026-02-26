from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock

class DashboardScreen(Screen):
    total_owed = NumericProperty(500.00) # Dummy start data (You owe) [Test เฉยๆ]
    total_owe_me = NumericProperty(725.00) # Dummy start data (Owed to you)
    
    # Dummy data for UI showcase
    recent_splits = ListProperty([
        {"title": "Shabu Buffet", "subtitle": "Today \u2022 You owe \u0E3F150", "icon": "food", "color": "#FF6B6B"},
        {"title": "Pattaya Trip", "subtitle": "Yesterday \u2022 You paid \u0E3F1,200", "icon": "car", "color": "#00C853"},
        {"title": "Grab Taxi", "subtitle": "Monday \u2022 You paid \u0E3F250", "icon": "taxi", "color": "#00C853"}
    ])

    def on_enter(self, *args):
        # Refresh logic here later
        pass
        
    def go_to_new_split(self):
        """Navigate to New Split screen (Create new bill)"""
        print("Navigation: Create New Bill")
        # self.manager.current = 'new_split_screen'

    def go_to_scan(self):
        """Navigate to Scan Receipt screen"""
        print("Navigation: Scan Receipt")
        self.manager.current = 'scan_screen'
        
    def go_to_add_friend(self):
        """Navigate to Add Friend context"""
        print("Action: Add Friend")
