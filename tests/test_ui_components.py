"""
Unit tests สำหรับ component Python logic
ทดสอบ property callbacks, state changes ของ UI components
ใช้ MDApp headless mode
"""

import os
import sys
import pytest

# ── Kivy headless setup (ต้องทำก่อน import Kivy modules) ──────────────
os.environ["KIVY_NO_ARGS"] = "1"
os.environ["KIVY_NO_CONSOLELOG"] = "1"
os.environ["KIVY_LOG_LEVEL"] = "critical"

from kivymd.app import MDApp  # noqa: E402
from kivy.clock import Clock  # noqa: E402

# เพิ่ม project root เข้า path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.item_row import ItemRow  # noqa: E402
from components.bottom_nav import BottomNav  # noqa: E402
from components.person_toggle_row import PersonToggleRow  # noqa: E402


# ── Fixture สำหรับ MDApp ──────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def kivymd_app():
    """สร้าง MDApp instance ครั้งเดียวสำหรับทุก test
    (KivyMD ต้องมี app ก่อนสร้าง widget)"""
    app = MDApp()
    app.theme_cls.primary_palette = "Green"
    return app


# ══════════════════════════════════════════════════════════════════════
#  ItemRow Tests
# ══════════════════════════════════════════════════════════════════════


class TestItemRow:
    """ทดสอบ logic ของ ItemRow component"""

    def setup_method(self):
        self.row = ItemRow()

    # ── Price formatting ──────────────────────────────────────────────

    def test_price_format_zero(self):
        """ราคา 0 ต้องแสดง ฿0.00"""
        self.row.price = 0
        assert self.row.price_text == "฿0.00"

    def test_price_format_integer(self):
        """ราคาจำนวนเต็มต้องมีทศนิยม 2 ตำแหน่ง"""
        self.row.price = 500
        assert self.row.price_text == "฿500.00"

    def test_price_format_decimal(self):
        """ราคาทศนิยมต้องแสดงถูกต้อง"""
        self.row.price = 123.45
        assert self.row.price_text == "฿123.45"

    def test_price_format_thousands(self):
        """ราคาหลักพันต้องมี comma"""
        self.row.price = 1500.50
        assert self.row.price_text == "฿1,500.50"

    # ── Assigned text ─────────────────────────────────────────────────

    def test_assigned_empty_shows_everyone(self):
        """ไม่มี assigned → แสดง 'ทุกคน'"""
        self.row.assigned_to = []
        assert self.row.assigned_text == "ทุกคน"

    def test_assigned_one_person(self):
        """assigned 1 คน → แสดงชื่อคนเดียว"""
        self.row.assigned_to = ["Alice"]
        assert self.row.assigned_text == "Alice"

    def test_assigned_two_people(self):
        """assigned 2 คน → แสดงชื่อ 2 คนคั่นด้วย comma"""
        self.row.assigned_to = ["Alice", "Bob"]
        assert self.row.assigned_text == "Alice, Bob"

    def test_assigned_many_people(self):
        """assigned 3+ คน → แสดงชื่อแรก +N คน"""
        self.row.assigned_to = ["Alice", "Bob", "Charlie"]
        assert self.row.assigned_text == "Alice +2 คน"

    def test_assigned_four_people(self):
        """assigned 4 คน → แสดงชื่อแรก +3 คน"""
        self.row.assigned_to = ["A", "B", "C", "D"]
        assert self.row.assigned_text == "A +3 คน"

    # ── Callbacks ─────────────────────────────────────────────────────

    def test_do_delete_calls_callback(self):
        """do_delete() ต้องเรียก delete_cb"""
        called = []
        self.row.delete_cb = lambda: called.append(True)
        self.row.do_delete()
        assert called == [True]

    def test_do_delete_no_callback(self):
        """do_delete() ไม่ crash ถ้าไม่มี callback"""
        self.row.delete_cb = None
        self.row.do_delete()  # ต้องไม่ raise

    def test_do_assign_calls_callback(self):
        """do_assign() ต้องเรียก assign_cb"""
        called = []
        self.row.assign_cb = lambda: called.append(True)
        self.row.do_assign()
        assert called == [True]

    def test_do_assign_no_callback(self):
        """do_assign() ไม่ crash ถ้าไม่มี callback"""
        self.row.assign_cb = None
        self.row.do_assign()  # ต้องไม่ raise


# ══════════════════════════════════════════════════════════════════════
#  BottomNav Tests
# ══════════════════════════════════════════════════════════════════════

ACTIVE = [0.957, 0.349, 0.145, 1.0]  # #F45925
INACTIVE = [0.580, 0.635, 0.722, 1.0]  # #94A3B8


class TestBottomNav:
    """ทดสอบ logic ของ BottomNav component"""

    def setup_method(self):
        self.nav = BottomNav()

    def test_default_tab_is_home(self):
        """tab เริ่มต้นต้องเป็น 'home'"""
        assert self.nav.active_tab == "home"

    def test_home_tab_colors(self):
        """เลือก home → home สีส้ม, ที่เหลือสีเทา"""
        self.nav.active_tab = "home"
        assert list(self.nav.home_icon_color) == ACTIVE
        assert list(self.nav.scan_icon_color) == INACTIVE
        assert list(self.nav.friends_icon_color) == INACTIVE
        assert list(self.nav.settings_icon_color) == INACTIVE

    def test_scan_tab_colors(self):
        """เลือก scan → scan สีส้ม, ที่เหลือสีเทา"""
        self.nav.active_tab = "scan"
        assert list(self.nav.home_icon_color) == INACTIVE
        assert list(self.nav.scan_icon_color) == ACTIVE
        assert list(self.nav.friends_icon_color) == INACTIVE
        assert list(self.nav.settings_icon_color) == INACTIVE

    def test_friends_tab_colors(self):
        """เลือก friends → friends สีส้ม, ที่เหลือสีเทา"""
        self.nav.active_tab = "friends"
        assert list(self.nav.home_icon_color) == INACTIVE
        assert list(self.nav.scan_icon_color) == INACTIVE
        assert list(self.nav.friends_icon_color) == ACTIVE
        assert list(self.nav.settings_icon_color) == INACTIVE

    def test_settings_tab_colors(self):
        """เลือก settings → settings สีส้ม, ที่เหลือสีเทา"""
        self.nav.active_tab = "settings"
        assert list(self.nav.home_icon_color) == INACTIVE
        assert list(self.nav.scan_icon_color) == INACTIVE
        assert list(self.nav.friends_icon_color) == INACTIVE
        assert list(self.nav.settings_icon_color) == ACTIVE

    def test_switch_tabs(self):
        """สลับ tab ต้องเปลี่ยนสีถูก"""
        self.nav.active_tab = "scan"
        assert list(self.nav.scan_icon_color) == ACTIVE

        self.nav.active_tab = "friends"
        assert list(self.nav.scan_icon_color) == INACTIVE
        assert list(self.nav.friends_icon_color) == ACTIVE


# ══════════════════════════════════════════════════════════════════════
#  PersonToggleRow Tests
# ══════════════════════════════════════════════════════════════════════


class TestPersonToggleRow:
    """ทดสอบ logic ของ PersonToggleRow component"""

    def setup_method(self):
        self.row = PersonToggleRow()

    # ── Display name → first letter ───────────────────────────────────

    def test_first_letter_normal(self):
        """ชื่อปกติ → ตัวอักษรแรกเป็นพิมพ์ใหญ่"""
        self.row.display_name = "alice"
        assert self.row.first_letter == "A"

    def test_first_letter_thai(self):
        """ชื่อภาษาไทย → ตัวอักษรแรก"""
        self.row.display_name = "สมชาย"
        assert self.row.first_letter == "ส"

    def test_first_letter_empty(self):
        """ชื่อว่าง → แสดง '?'"""
        self.row.display_name = ""
        assert self.row.first_letter == "?"

    # ── Selection state ───────────────────────────────────────────────

    def test_default_is_selected(self):
        """สถานะเริ่มต้นต้องเป็น selected"""
        assert self.row.is_selected is True

    def test_selected_opacity(self):
        """selected → opacity 1.0"""
        self.row.is_selected = True
        assert self.row.check_opacity == 1.0

    def test_unselected_opacity(self):
        """unselected → opacity 0.0"""
        self.row.is_selected = False
        assert self.row.check_opacity == 0.0

    def test_toggle_flips_state(self):
        """toggle() ต้องสลับสถานะ"""
        self.row.is_selected = True
        self.row.toggle()
        assert self.row.is_selected is False

    def test_toggle_twice_restores(self):
        """toggle() 2 ครั้ง → กลับสถานะเดิม"""
        original = self.row.is_selected
        self.row.toggle()
        self.row.toggle()
        assert self.row.is_selected == original

    def test_selection_changes_bg_color(self):
        """เลือก/ไม่เลือก ต้องเปลี่ยนสีพื้นหลัง"""
        self.row.is_selected = True
        selected_color = list(self.row.md_bg_color)

        self.row.is_selected = False
        unselected_color = list(self.row.md_bg_color)

        assert selected_color != unselected_color
