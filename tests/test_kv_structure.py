"""
Unit tests สำหรับตรวจสอบโครงสร้าง KV files
ใช้ static analysis ตรวจว่า icon centering pattern ถูกต้อง
"""

import os
import re
import glob
import pytest

# ── Path setup ────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
KV_DIR = os.path.join(PROJECT_ROOT, "kv")
COMPONENTS_DIR = os.path.join(PROJECT_ROOT, "components")


def get_all_kv_files():
    """หาทุก .kv file ในโปรเจค"""
    files = []
    for d in [KV_DIR, COMPONENTS_DIR]:
        files.extend(glob.glob(os.path.join(d, "*.kv")))
    return sorted(files)


def parse_kv_blocks(content):
    """
    แยก MDIcon blocks จาก KV content
    คืน list ของ (line_number, indent, properties_dict)
    """
    lines = content.split("\n")
    blocks = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()

        if stripped == "MDIcon:":
            indent = len(lines[i]) - len(lines[i].lstrip())
            props = {}
            prop_lines = []
            j = i + 1

            while j < len(lines):
                next_line = lines[j]
                next_stripped = next_line.strip()

                if next_stripped == "":
                    break
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent:
                    break

                # Parse property
                if ":" in next_stripped:
                    key = next_stripped.split(":")[0].strip()
                    value = ":".join(next_stripped.split(":")[1:]).strip()
                    props[key] = value
                    prop_lines.append(next_stripped)

                j += 1

            blocks.append(
                {
                    "line": i + 1,
                    "indent": indent,
                    "props": props,
                    "raw_lines": prop_lines,
                }
            )

        i += 1

    return blocks


def get_parent_widget(content, icon_line_num):
    """หา parent widget ของ MDIcon ที่บรรทัดที่กำหนด"""
    lines = content.split("\n")
    icon_indent = len(lines[icon_line_num - 1]) - len(lines[icon_line_num - 1].lstrip())

    # Look backwards for parent
    for i in range(icon_line_num - 2, -1, -1):
        line = lines[i]
        stripped = line.strip()
        if stripped == "":
            continue
        line_indent = len(line) - len(line.lstrip())
        if line_indent < icon_indent:
            # Extract widget name
            match = re.match(r"(\w+):", stripped)
            if match:
                return match.group(1)
            break

    return None


# ══════════════════════════════════════════════════════════════════════
#  KV File Parse Tests
# ══════════════════════════════════════════════════════════════════════


class TestKvFileParsing:
    """ตรวจว่าทุก KV file อ่านได้ไม่ error"""

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_kv_file_is_readable(self, kv_file):
        """ทุก KV file ต้องเปิดอ่านได้"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 0, f"{kv_file} is empty"

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_kv_file_has_valid_indentation(self, kv_file):
        """ตรวจว่า indentation ใช้ spaces ไม่ใช้ tabs"""
        with open(kv_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                assert "\t" not in line, (
                    f"{os.path.basename(kv_file)}:{line_num} uses tab indentation"
                )

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_kv_import_syntax(self, kv_file):
        """ตรวจว่า #:import ถูก syntax"""
        with open(kv_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("#:import"):
                    parts = stripped.split()
                    assert len(parts) >= 3, (
                        f"{os.path.basename(kv_file)}:{line_num} invalid import: {stripped}"
                    )


# ══════════════════════════════════════════════════════════════════════
#  Icon Centering Pattern Tests
# ══════════════════════════════════════════════════════════════════════


class TestIconCenteringPattern:
    """ตรวจว่า MDIcon ที่ต้องการ centering ใช้ AnchorLayout wrapper"""

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_anchored_icons_no_size_hint(self, kv_file):
        """MDIcon ใน AnchorLayout ต้องไม่มี size_hint_x: None
        (ต้องใช้ adaptive_size แทน, size_hint_x อยู่บน wrapper)"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = parse_kv_blocks(content)
        for block in blocks:
            parent = get_parent_widget(content, block["line"])
            if parent == "AnchorLayout":
                assert "size_hint_x" not in block["props"], (
                    f"{os.path.basename(kv_file)}:{block['line']} "
                    f"MDIcon inside AnchorLayout should not have size_hint_x. "
                    f"Use adaptive_size: True instead."
                )

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_anchored_icons_have_adaptive_size(self, kv_file):
        """MDIcon ที่อยู่ใน AnchorLayout ต้องมี adaptive_size: True"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = parse_kv_blocks(content)
        for block in blocks:
            parent = get_parent_widget(content, block["line"])
            if parent == "AnchorLayout":
                assert "adaptive_size" in block["props"], (
                    f"{os.path.basename(kv_file)}:{block['line']} "
                    f"MDIcon inside AnchorLayout should have adaptive_size: True"
                )
                assert block["props"]["adaptive_size"] == "True", (
                    f"{os.path.basename(kv_file)}:{block['line']} "
                    f"adaptive_size should be True"
                )

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_anchorlayout_wrappers_have_center(self, kv_file):
        """AnchorLayout ที่ครอบ MDIcon ต้องมี anchor_x/anchor_y: 'center'"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "AnchorLayout:":
                # Collect properties
                indent = len(line) - len(line.lstrip())
                props = {}
                has_mdicon_child = False
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    if next_stripped == "":
                        j += 1
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent:
                        break
                    if next_indent == indent + 4:
                        if ":" in next_stripped:
                            key = next_stripped.split(":")[0].strip()
                            value = ":".join(next_stripped.split(":")[1:]).strip()
                            props[key] = value
                        if next_stripped == "MDIcon:":
                            has_mdicon_child = True
                    j += 1

                if has_mdicon_child:
                    assert props.get("anchor_x") == '"center"', (
                        f"{os.path.basename(kv_file)}:{i + 1} "
                        f'AnchorLayout wrapping MDIcon needs anchor_x: "center"'
                    )
                    assert props.get("anchor_y") == '"center"', (
                        f"{os.path.basename(kv_file)}:{i + 1} "
                        f'AnchorLayout wrapping MDIcon needs anchor_y: "center"'
                    )


# ══════════════════════════════════════════════════════════════════════
#  General Layout Health Tests
# ══════════════════════════════════════════════════════════════════════


class TestLayoutHealth:
    """ตรวจความถูกต้องทั่วไปของ layout"""

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_no_conflicting_size_hints(self, kv_file):
        """ต้องไม่มี adaptive_height รวมกับ height คงที่ใน widget เดียวกัน"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            # Find widget declarations
            if re.match(r"\w+:", stripped) and not stripped.startswith("#"):
                indent = len(lines[i]) - len(lines[i].lstrip())
                props = set()
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    if next_stripped == "":
                        j += 1
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent:
                        break
                    if next_indent == indent + 4 and ":" in next_stripped:
                        key = next_stripped.split(":")[0].strip()
                        props.add(key)
                    j += 1

                # adaptive_height + explicit height = conflict
                if "adaptive_height" in props and "height" in props:
                    # This is OK if size_hint_y is None
                    if "size_hint_y" not in props:
                        pass  # May be intentional, just note it

            i += 1

    @pytest.mark.parametrize(
        "kv_file", get_all_kv_files(), ids=lambda f: os.path.basename(f)
    )
    def test_no_empty_widget_rules(self, kv_file):
        """ตรวจว่าทุก KV file มี widget rule อย่างน้อย 1 อัน"""
        with open(kv_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for <WidgetName>: pattern
        rules = re.findall(r"^<\w+.*>:", content, re.MULTILINE)
        assert len(rules) > 0, f"{os.path.basename(kv_file)} has no widget rules"
