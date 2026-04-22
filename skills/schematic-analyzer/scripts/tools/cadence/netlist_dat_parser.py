r"""Cadence Allegro netlist (.dat) parser.

Parses pstxnet.dat and pstxprt.dat files exported from OrCAD/Allegro.
These files provide authoritative pin-net connectivity computed by the
OrCAD engine, which is more accurate than XML coordinate matching.

Key features:
- Dual-format pin extraction: CDS_PINID='...' and plain 'PIN_NAME' styles
- CDS_PINID escape sequence handling (\X\ -> X)
- Mux pin name resolution for SoC GPIO (| separated alternatives)
- Flexible page detection from pstxprt.dat (P_PATH, SECTION_NUMBER, etc.)
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional


def find_netlist_dir(root_path: Path) -> Optional[Path]:
    """Find the directory containing Allegro netlist files.

    Searches for netlist directories using multiple strategies:
    1. Direct child dirs with 'netlist' in name (case-insensitive) + pstxnet.dat
    2. Common exact directory names (netlist, allegro, etc.)
    3. pstxnet.dat in search_path itself
    4. Recursive search (max depth 3) for pstxnet.dat

    Args:
        root_path: Root schematic directory or file to search from.

    Returns:
        Path to netlist directory if found, None otherwise.
    """
    # If root_path is a file, use its parent directory
    search_path = root_path.parent if root_path.is_file() else root_path

    if not search_path.is_dir():
        return None

    # Helper: check if a directory contains a recognizable Allegro netlist file
    def _has_netlist_dat(d: Path) -> bool:
        for name in ("pstxnet.dat", "PSTXNET.DAT"):
            if (d / name).is_file():
                return True
        return False

    # Strategy 1: Direct child directories whose name suggests netlist data
    try:
        for child in search_path.iterdir():
            if not child.is_dir():
                continue
            low = child.name.lower()
            if "netlist" in low or low in ("allegro", "pstxnet", "cadence", "output"):
                if _has_netlist_dat(child):
                    return child
    except OSError:
        pass

    # Strategy 2: Check search_path itself
    if _has_netlist_dat(search_path):
        return search_path

    # Strategy 3: Recursive search with depth limit
    try:
        for dat_file in search_path.rglob("pstxnet.dat"):
            return dat_file.parent
        # Also try uppercase variant on case-sensitive filesystems
        for dat_file in search_path.rglob("PSTXNET.DAT"):
            return dat_file.parent
    except OSError:
        pass

    return None


def _select_mux_pin_name(pin_id: str, net_name: str) -> str:
    """Select the appropriate pin name from a mux table.

    SoC GPIO pins often have multiple functions separated by `|`.
    This function selects the most appropriate name based on the net name.

    Args:
        pin_id: Raw CDS_PINID value, possibly containing `|` separated mux options.
        net_name: The net name this pin is connected to.

    Returns:
        Selected pin name. If no match with net_name, returns the first
        non-empty option, or "GPIO" fallback.
    """
    if '|' not in pin_id:
        return pin_id

    # Split by | and clean up each option
    candidates = [p.strip() for p in pin_id.split('|')]

    # Filter out empty/dash placeholders
    valid_candidates = [c for c in candidates if c and c != '--']

    if not valid_candidates:
        return 'GPIO'

    # Try to match with net name first
    for candidate in valid_candidates:
        if candidate == net_name:
            return candidate

    # Fallback: return first valid option
    return valid_candidates[0]


def _clean_pin_escape(pin_name: str) -> str:
    r"""Clean Cadence escape sequences from pin names.

    Cadence uses \X\ format to mark active-low signals (with overline).
    This function removes all backslash escapes.

    Args:
        pin_name: Raw pin name from CDS_PINID.

    Returns:
        Cleaned pin name with escape sequences removed.
    """
    return pin_name.replace('\\', '')


def parse_pstxnet(file_path: Path) -> dict[str, dict[str, str]]:
    r"""Parse Allegro pstxnet.dat file to extract pin-net mapping.

    The pstxnet.dat file contains authoritative connectivity data
    computed by the OrCAD engine. Each NODE_NAME entry maps a
    component reference and pin to a net name.

    Supports two pin identification formats:

    Format A (CDS_PINID):
        NET_NAME
        'UART6_RX_M0'
        NODE_NAME  U7 1B5
         '@...': '\PINNAME':CDS_PINID='\PINID';

    Format B (plain quoted pin name, no CDS_PINID):
        NET_NAME
        'SYS_VIN_HV_01'
        NODE_NAME  J37 C65
         '@...': 'PIN_NAME';

    Args:
        file_path: Path to pstxnet.dat file.

    Returns:
        Dictionary mapping {refdes: {pin_name: net_name}}.
        Pin names are extracted from CDS_PINID (Format A) with proper
        escape sequence handling and mux resolution, or from plain
        quoted strings (Format B) as a fallback.
    """
    pin_net_map: dict[str, dict[str, str]] = {}

    if not file_path.is_file():
        return pin_net_map

    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    i = 0
    current_net = ""

    while i < len(lines):
        line = lines[i].strip()

        # Check for NET_NAME - the net name is on the next line in single quotes
        if line.startswith('NET_NAME'):
            # Net name is on the next line: 'netname'
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Extract net name from single quotes
                net_match = re.match(r"'([^']+)'", next_line)
                if net_match:
                    current_net = net_match.group(1)

        # Check for NODE_NAME - format: NODE_NAME refdes pin_number
        elif line.startswith('NODE_NAME'):
            # Parse: NODE_NAME U7 1B5
            node_match = re.match(r'NODE_NAME\s+(\S+)\s+(\S+)', line)
            if node_match:
                refdes = node_match.group(1)
                pin_number = node_match.group(2)
                pin_id = None

                # Look for pin identification in the next few lines
                # Priority 1: CDS_PINID='...' (Format A)
                # Priority 2: Plain quoted pin name (Format B)
                # Fallback: Use pin_number from NODE_NAME line
                j = i + 1
                while j < len(lines) and j < i + 5:
                    check_line = lines[j]
                    # Stop scanning if we hit the next NET_NAME/NODE_NAME block
                    stripped = check_line.strip()
                    if stripped.startswith('NET_NAME') or stripped.startswith('NODE_NAME'):
                        break

                    # Format A: CDS_PINID='pinid'
                    pinid_match = re.search(r"CDS_PINID='([^']+)'", check_line)
                    if pinid_match:
                        raw_pin_id = pinid_match.group(1)

                        # Clean escape sequences (e.g., \FAULT1\ -> FAULT1)
                        pin_id = _clean_pin_escape(raw_pin_id)

                        # Resolve mux pin if needed (e.g., "FUNC1 | FUNC2 | GPIO")
                        if '|' in pin_id:
                            pin_id = _select_mux_pin_name(pin_id, current_net)
                        break

                    # Format B: plain quoted pin name like 'PIN_NAME';
                    # Look for a quoted string that looks like a pin identifier
                    # (not a full path with ':' which is a component reference line)
                    plain_pin_match = re.search(r"^\s*'([^':]+)'\s*;", check_line)
                    if plain_pin_match and pin_id is None:
                        raw_name = plain_pin_match.group(1)
                        pin_id = _clean_pin_escape(raw_name)
                        # Don't break yet — CDS_PINID on a later line takes priority
                    j += 1

                # Fallback: use pin_number from NODE_NAME line
                if pin_id is None:
                    pin_id = _clean_pin_escape(pin_number)

                if pin_id and current_net:
                    if refdes not in pin_net_map:
                        pin_net_map[refdes] = {}
                    pin_net_map[refdes][pin_id] = current_net

        i += 1

    return pin_net_map


def parse_pstxprt(file_path: Path) -> dict[str, dict]:
    r"""Parse Allegro pstxprt.dat file to extract component page information.

    The pstxprt.dat file contains component-to-page mapping data.
    Supports multiple page identification methods:

    Method 1: P_PATH with pageX pattern:
        P_PATH='...\pageX_...'

    Method 2: P_PATH without pageX — extract page from other patterns:
        P_PATH='...\SCH_1_PAGE_X_...'

    Method 3: SECTION_NUMBER as fallback page indicator.

    Args:
        file_path: Path to pstxprt.dat file.

    Returns:
        Dictionary mapping {refdes: {"page": page_name, "footprint": ..., ...}}.
    """
    page_info: dict[str, dict] = {}

    if not file_path.is_file():
        return page_info

    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    i = 0
    current_refdes = ""
    current_value = ""
    current_section = ""

    while i < len(lines):
        line = lines[i].strip()

        # Check for PART_NAME block start
        if line.startswith('PART_NAME'):
            # If previous component had SECTION_NUMBER but no P_PATH, save it now
            if current_refdes and current_section:
                page_info[current_refdes] = {
                    "primitive": current_value,
                    "page": f"page{current_section}",
                    "footprint": "",
                    "value": current_value,
                }

            # Next line has: REFDES 'VALUE':;
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                part_match = re.match(r"(\S+)\s+'([^']+)':", next_line)
                if part_match:
                    current_refdes = part_match.group(1)
                    current_value = part_match.group(2)
                    current_section = ""

        # Track SECTION_NUMBER as fallback page info
        elif line.startswith('SECTION_NUMBER'):
            sec_match = re.match(r'SECTION_NUMBER\s+(\d+)', line)
            if sec_match:
                current_section = sec_match.group(1)

        # Look for P_PATH which contains page info
        elif 'P_PATH=' in line and current_refdes:
            ppath_match = re.search(r"P_PATH='([^']+)'", line)
            if ppath_match:
                ppath = ppath_match.group(1)
                page_name = _extract_page_from_path(ppath)

                page_info[current_refdes] = {
                    "primitive": current_value,
                    "page": page_name,
                    "footprint": "",
                    "value": current_value,
                }
                # Reset after processing
                current_refdes = ""
                current_value = ""
                current_section = ""

        i += 1

    # Handle last component if it didn't get P_PATH but has SECTION_NUMBER
    if current_refdes and current_section:
        page_info[current_refdes] = {
            "primitive": current_value,
            "page": f"page{current_section}",
            "footprint": "",
            "value": current_value,
        }

    return page_info


def _extract_page_from_path(ppath: str) -> str:
    """Extract page identifier from a P_PATH string.

    Tries multiple patterns:
    1. pageN (standard OrCAD)
    2. PAGE_N (alternative naming)
    3. Last numeric segment as fallback
    """
    # Pattern 1: pageN (e.g., page1, page9)
    m = re.search(r'[Pp][Aa][Gg][Ee](\d+)', ppath)
    if m:
        return f"page{m.group(1)}"

    # Pattern 2: PAGE_N or PAGE.N
    m = re.search(r'PAGE[_\.\s]*(\d+)', ppath, re.IGNORECASE)
    if m:
        return f"page{m.group(1)}"

    # Pattern 3: Look for SCH_X or similar schematic sheet references
    m = re.search(r'SCH[_\.\s]*(\d+)', ppath, re.IGNORECASE)
    if m:
        return f"page{m.group(1)}"

    # Fallback: use a deterministic hash of the full path as a unique page identifier
    digest = hashlib.md5(ppath.encode('utf-8', errors='ignore')).hexdigest()[:4]
    return f"page_{digest}"


def build_pin_net_map_from_dat(netlist_dir: Path) -> dict[str, dict[str, str]]:
    """Build pin-net map from Allegro netlist directory.

    Reads pstxnet.dat from the given directory and returns
    the pin-to-net connectivity mapping.

    Args:
        netlist_dir: Directory containing pstxnet.dat file.

    Returns:
        Dictionary mapping {refdes: {pin_name: net_name}}.
        Returns empty dict if file not found or parsing fails.
    """
    pstxnet_file = netlist_dir / "pstxnet.dat"

    if not pstxnet_file.is_file():
        return {}

    return parse_pstxnet(pstxnet_file)


def parse_pstchip(file_path: Path) -> dict[str, dict[str, str]]:
    r"""Parse Allegro pstchip.dat to extract pin-function-to-physical-pin mapping.

    The pstchip.dat file defines library part primitives with pin sections that
    map functional pin names (e.g. ``VOUT1``, ``NLDO1``) to physical pin numbers
    via ``PIN_NUMBER='(...)'`` tuples.

    PIN_NUMBER tuple formats:
      - Simple: ``PIN_NUMBER='(1)'`` → physical pin 1
      - Complex: ``PIN_NUMBER='(49,0,0)'`` → first non-zero element = pin 49
      - Complex: ``PIN_NUMBER='(0,14,0)'`` → first non-zero element = pin 14

    The result is indexed by ``PART_NAME`` so callers can look up a component's
    pin map using the part name extracted from its library_id.

    Args:
        file_path: Path to pstchip.dat file.

    Returns:
        Dictionary mapping ``{PART_NAME: {pin_function_name: physical_pin_number}}``.
        Pin function names have Cadence escape sequences (``\\X\\``) stripped.
        Returns empty dict if file not found.
    """
    pin_map: dict[str, dict[str, str]] = {}

    if not file_path.is_file():
        return pin_map

    content = file_path.read_text(encoding='utf-8', errors='ignore')
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for primitive block start: primitive 'NAME';
        if line.startswith('primitive'):
            prim_match = re.match(r"primitive\s+'([^']+)'", line)
            if prim_match:
                current_pins: dict[str, str] = {}
                current_part_name: str | None = None
                in_pin_section = False
                i += 1

                while i < len(lines):
                    inner = lines[i].strip()

                    if inner.startswith('end_primitive'):
                        # Save if we have a PART_NAME
                        if current_part_name and current_pins:
                            pin_map[current_part_name] = current_pins
                        break

                    if inner == 'pin':
                        in_pin_section = True
                        i += 1
                        continue

                    if inner == 'end_pin':
                        in_pin_section = False
                        i += 1
                        continue

                    if in_pin_section:
                        # Pin function name line: '\VOUT1\':
                        # or for simple parts: '1':
                        pin_name_match = re.match(r"'([^']+)'\s*:", inner)
                        if pin_name_match:
                            raw_pin_name = _clean_pin_escape(pin_name_match.group(1))
                            # Look ahead for PIN_NUMBER on the next line
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                pn_match = re.search(r"PIN_NUMBER\s*=\s*'\(([^)]+)\)'", next_line)
                                if pn_match:
                                    tuple_str = pn_match.group(1)
                                    # Extract first non-zero element as physical pin number
                                    parts = tuple_str.split(',')
                                    pin_num = ""
                                    for p in parts:
                                        p = p.strip()
                                        if p and p != '0':
                                            pin_num = p
                                            break
                                    if pin_num:
                                        current_pins[raw_pin_name] = pin_num

                    # Look for PART_NAME in body section
                    if inner.startswith('PART_NAME'):
                        pn_match = re.search(r"PART_NAME\s*=\s*'([^']+)'", inner)
                        if pn_match:
                            current_part_name = pn_match.group(1)

                    i += 1
        i += 1

    return pin_map
