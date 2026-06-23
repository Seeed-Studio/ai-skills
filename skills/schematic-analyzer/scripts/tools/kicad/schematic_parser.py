"""Schematic file parser wrapper using kicad-skip."""

import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..utils.file_handlers import validate_kicad_file

# KiCad-defined boolean flags (fixed set, not user-extensible)
KICAD_SYMBOL_FLAGS = ("dnp", "in_bom", "on_board", "exclude_from_sim")
KICAD_FLAG_DEFAULTS = {"dnp": False, "in_bom": True, "on_board": True, "exclude_from_sim": False}

# Distance/coordinate thresholds (millimetres)
NEARBY_LABEL_DISTANCE_MM = 20.0
NEARBY_COMPONENT_DISTANCE_MM = 15.0
POINT_ON_SEGMENT_TOLERANCE = 0.05
WIRE_TRACE_MAX_TOLERANCE_MM = 20.0
LABEL_MATCH_TOLERANCE_MM = 5.0
POWER_SYMBOL_TOLERANCE_MM = 15.0
JUNCTION_MATCH_TOLERANCE = 0.01

# Parsing limits
MAX_SYMBOL_BLOCK_LINES = 500
BFS_TRACE_MAX_DEPTH = 20
NEARBY_RESULTS_LIMIT = 10

@dataclass
class SchematicComponent:
    """Component from schematic file."""

    reference: str
    value: str
    library_id: str
    footprint: Optional[str] = None
    properties: dict[str, str] = field(default_factory=dict)
    position: tuple[float, float] = (0.0, 0.0)
    unit: Optional[int] = None
    pins: list[dict[str, Any]] = field(default_factory=list)
    flags: dict[str, bool] = field(default_factory=lambda: dict(KICAD_FLAG_DEFAULTS))

    @classmethod
    def from_kicad_skip(cls, data: dict[str, Any]) -> "SchematicComponent":
        """Create from kicad-skip data structure."""
        # Extract properties
        properties = {}
        for prop in data.get("properties", []):
            key = prop.get("key", "")
            value = prop.get("value", "")
            if key and value:
                properties[key] = value

        # Get position
        at = data.get("at", {})
        position = (float(at.get("x", 0)), float(at.get("y", 0)))

        # Get unit
        unit = data.get("unit")

        return cls(
            reference=data.get("reference", ""),
            value=properties.get("Value", data.get("value", "")),
            library_id=data.get("lib_id", ""),
            footprint=properties.get("Footprint"),
            properties=properties,
            position=position,
            unit=unit,
            pins=data.get("pins", []),
            flags=data.get("flags", dict(KICAD_FLAG_DEFAULTS)),
        )


@dataclass
class SchematicNet:
    """Net from schematic file."""

    name: str
    code: int
    node_count: int = 0
    pins: list[str] = field(default_factory=list)
    type: str = "unknown"
    position: tuple[float, float] = (0.0, 0.0)

    @classmethod
    def from_kicad_skip(cls, data: dict[str, Any]) -> "SchematicNet":
        """Create from kicad-skip data structure."""
        return cls(
            name=data.get("name", ""),
            code=data.get("code", 0),
            type=data.get("type", "unknown"),
            position=data.get("position", (0.0, 0.0)),
        )


@dataclass
class SchematicPin:
    """Pin definition from symbol."""

    number: str
    name: str
    type: str

    @classmethod
    def from_kicad_skip(cls, data: dict[str, Any]) -> "SchematicPin":
        """Create from kicad-skip data structure."""
        return cls(
            number=data.get("number", ""),
            name=data.get("name", ""),
            type=data.get("electrical_type", ""),
        )


@dataclass
class SheetInstanceRecord:
    """One hierarchical sheet instance mapped from UUID path to display path."""

    sheet_name: str
    sheet_file: str
    sheet_uuid: str
    sheet_uuid_path: str
    sheet_name_path: str
    source_schematic: str


def _read_file_with_encoding_fallback(file_path: Path) -> str:
    """Read file with multiple encoding fallback support.

    Args:
        file_path: Path to the file to read

    Returns:
        File content as string

    Note:
        Tries multiple encodings to handle different KiCad file formats
        and potential encoding issues.
    """
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        # Last resort: read with error handling
        content = file_path.read_text(encoding='utf-8', errors='ignore')

    return content


class SchematicParser:
    """Parser for KiCad schematic files (.kicad_sch)."""

    def __init__(self, file_path: str, include_child_sheets: bool = True) -> None:
        """Initialize parser with schematic file.

        Args:
            file_path: Path to .kicad_sch file
            include_child_sheets: Recursively aggregate child sheets when True

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a .kicad_sch file
        """
        self.file_path = validate_kicad_file(file_path, ".kicad_sch")
        self.include_child_sheets = include_child_sheets
        self._data: Optional[dict[str, Any]] = None
        self._sheet_instances: Optional[list[str]] = None
        self._sheet_instance_records: Optional[list[dict[str, str]]] = None

    def _parse_file(self) -> dict[str, Any]:
        """Parse the schematic file.

        Returns:
            Parsed data structure

        Note:
            This is a simplified parser. For production use, integrate kicad-skip
            or use kicad-netlist for proper parsing.
        """
        if self._data is not None:
            return self._data

        if not self.include_child_sheets:
            content = _read_file_with_encoding_fallback(self.file_path.resolve())
            lib_symbols_lookup = self._parse_lib_symbols(content)
            self._data = {
                "path": str(self.file_path.resolve()),
                "title_block": self._parse_title_block(content),
                "components": self._dedupe_components(self._parse_components(content, lib_symbols_lookup)),
                "nets": self._dedupe_nets(self._parse_nets(content)),
                "sheets": self._dedupe_sheets(self._parse_sheets(content)),
            }
            return self._data

        self._data = self._parse_file_recursive(self.file_path.resolve(), set())
        return self._data

    def _parse_file_recursive(self, file_path: Path, visited: set[Path]) -> dict[str, Any]:
        """Parse a schematic and recursively aggregate child sheets."""
        resolved_path = file_path.resolve()
        if resolved_path in visited:
            return {
                "path": str(resolved_path),
                "title_block": self._parse_title_block(""),
                "components": [],
                "nets": [],
                "sheets": [],
            }

        visited.add(resolved_path)
        content = _read_file_with_encoding_fallback(resolved_path)
        lib_symbols_lookup = self._parse_lib_symbols(content)

        local_sheets = self._parse_sheets(content)
        aggregated_components = self._parse_components(content, lib_symbols_lookup)
        aggregated_nets = self._parse_nets(content)
        aggregated_sheets = list(local_sheets)

        for sheet in local_sheets:
            sheet_file = sheet.get("file", "")
            if not sheet_file:
                continue

            child_path = (resolved_path.parent / sheet_file).resolve()
            if not child_path.exists():
                continue

            child_data = self._parse_file_recursive(child_path, visited)
            aggregated_components.extend(child_data["components"])
            aggregated_nets.extend(child_data["nets"])
            aggregated_sheets.extend(child_data["sheets"])

        return {
            "path": str(resolved_path),
            "title_block": self._parse_title_block(content),
            "components": self._dedupe_components(aggregated_components),
            "nets": self._dedupe_nets(aggregated_nets),
            "sheets": self._dedupe_sheets(aggregated_sheets),
        }

    def _extract_balanced_blocks(
        self,
        content: str,
        block_prefix: str,
        *,
        exclude_prefixes: tuple[str, ...] = (),
    ) -> list[str]:
        """Extract balanced S-expression blocks that start with a given prefix."""
        blocks = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(block_prefix) and not any(line.startswith(prefix) for prefix in exclude_prefixes):
                block_lines = []
                depth = 0
                j = i

                while j < len(lines):
                    current_line = lines[j]
                    depth += current_line.count("(") - current_line.count(")")
                    block_lines.append(current_line)
                    if depth == 0 and block_lines:
                        break
                    j += 1

                blocks.append("\n".join(block_lines))
                i = j + 1
                continue

            i += 1

        return blocks

    def _parse_lib_symbols(self, content: str) -> dict[str, dict[str, dict[str, str]]]:
        """Parse lib_symbols section to extract pin names and electrical types.

        Returns:
            {lib_id: {pin_number: {"name": str, "electrical_type": str}}}
        """
        result = {}

        # Find the (lib_symbols ...) block
        ls_match = re.search(r'\(lib_symbols\b', content)
        if not ls_match:
            return result

        # Extract the full lib_symbols block by counting parens
        start = ls_match.start()
        depth = 0
        i = start
        while i < len(content):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        ls_block = content[start:i + 1]

        # Find top-level symbols (contain ":" like "Device:R") and extract their blocks
        # Support both quoted "lib:id" and unquoted lib:id formats
        lines = ls_block.split('\n')
        li = 0
        while li < len(lines):
            line = lines[li].strip()
            top_match = re.match(r'\(symbol\s+"([^"]*:[^"]*)"', line)
            if not top_match:
                # Fallback: unquoted format (symbol lib:id ...)
                top_match = re.match(r'\(symbol\s+([^\s(]+:[^\s(]+)', line)
            if top_match:
                lib_id = top_match.group(1)
                # Extract full block for this top-level symbol
                sym_lines = []
                depth = 0
                j = li
                while j < len(lines):
                    cur = lines[j]
                    depth += cur.count('(') - cur.count(')')
                    sym_lines.append(cur)
                    if depth == 0 and len(sym_lines) > 1:
                        break
                    j += 1
                    if j - li > MAX_SYMBOL_BLOCK_LINES:
                        break
                sym_block = '\n'.join(sym_lines)

                # Extract pins from the entire symbol block (including sub-symbols)
                # Pin format: (pin <elec_type> <graphic> ... (name "X") (number "N"))
                pin_pattern = re.compile(
                    r'\(pin\s+(\w+)\s+\w+\s[\s\S]*?'
                    r'\(name\s+"([^"]*)"[\s\S]*?\)'
                    r'\s*\(number\s+"([^"]*)"',
                )
                pins = {}
                for pin_match in pin_pattern.finditer(sym_block):
                    elec_type = pin_match.group(1)
                    name = pin_match.group(2)
                    number = pin_match.group(3)
                    pins[number] = {
                        "name": name,
                        "electrical_type": elec_type,
                    }
                if pins:
                    result[lib_id] = pins

                li = j + 1
            else:
                li += 1

        return result

    def _parse_title_block(self, content: str) -> dict[str, str]:
        """Parse title block from schematic."""
        title_block = {
            "title": "",
            "date": "",
            "rev": "",
            "company": "",
            "comment": "",
        }

        # Extract title block values using regex
        patterns = {
            "title": r'title\s+"([^"]*)"',
            "date": r'date\s+"([^"]*)"',
            "rev": r'rev\s+"([^"]*)"',
            "company": r'company\s+"([^"]*)"',
            "comment": r'comment\s+\d+\s+"([^"]*)"',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                title_block[key] = match.group(1)

        return title_block

    def _parse_components(
        self,
        content: str,
        lib_symbols_lookup: Optional[dict[str, dict[str, dict[str, str]]]] = None,
    ) -> list[dict[str, Any]]:
        """Parse components from schematic."""
        components = []
        lib_symbols_lookup = lib_symbols_lookup or {}

        for block_text in self._extract_balanced_blocks(content, "(symbol", exclude_prefixes=('(symbol "',)):
            lib_id_match = re.search(r'\(lib_id\s+"([^"]+)"', block_text)
            if not lib_id_match:
                continue

            lib_id = lib_id_match.group(1)

            at_match = re.search(r'^\s*\(at\s+([\d.]+)\s+([\d.]+)(?:\s+(\d+))?\)', block_text, re.MULTILINE)
            if at_match:
                x = float(at_match.group(1))
                y = float(at_match.group(2))
            else:
                x, y = 0.0, 0.0

            ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block_text)
            reference = ref_match.group(1) if ref_match else ""

            value_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block_text)
            value = value_match.group(1) if value_match else ""

            fp_match = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', block_text)
            footprint = fp_match.group(1) if fp_match else None

            pins = []
            lib_pin_data = lib_symbols_lookup.get(lib_id, {})
            for pin_match in re.finditer(r'\(pin\s+"([^"]+)"', block_text):
                pin_num = pin_match.group(1)
                pin_info = lib_pin_data.get(pin_num, {})
                pins.append({
                    "number": pin_num,
                    "name": pin_info.get("name", ""),
                    "electrical_type": pin_info.get("electrical_type", ""),
                })

            flags = dict(KICAD_FLAG_DEFAULTS)
            for flag in KICAD_SYMBOL_FLAGS:
                if f"({flag} yes)" in block_text:
                    flags[flag] = True
                elif f"({flag} no)" in block_text:
                    flags[flag] = False

            if reference and not reference.startswith("#"):
                properties = [
                    {"key": "Reference", "value": reference},
                    {"key": "Value", "value": value},
                ]
                if footprint:
                    properties.append({"key": "Footprint", "value": footprint})

                components.append({
                    "lib_id": lib_id,
                    "reference": reference,
                    "value": value,
                    "properties": properties,
                    "at": {"x": x, "y": y},
                    "pins": pins,
                    "flags": flags,
                })

        return components

    def _parse_nets(self, content: str) -> list[dict[str, Any]]:
        """Parse nets from schematic."""
        nets = {}

        # KiCad 9.0 uses global_label, label, and wire to define nets
        # Extract global labels
        global_label_pattern = r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'
        for match in re.finditer(global_label_pattern, content):
            name = match.group(1)
            x = float(match.group(2))
            y = float(match.group(3))
            nets[name] = {
                "name": name,
                "code": len(nets),
                "type": "global",
                "position": (x, y),
            }

        # Extract local labels
        label_pattern = r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'
        for match in re.finditer(label_pattern, content):
            name = match.group(1)
            if name not in nets:  # Avoid duplicates
                x = float(match.group(2))
                y = float(match.group(3))
                nets[name] = {
                    "name": name,
                    "code": len(nets),
                    "type": "local",
                    "position": (x, y),
                }

        # Extract hierarchical labels (connections to parent/child sheets)
        h_label_pattern = r'\(hierarchical_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'
        for match in re.finditer(h_label_pattern, content):
            name = match.group(1)
            if name not in nets:  # Avoid duplicates
                x = float(match.group(2))
                y = float(match.group(3))
                nets[name] = {
                    "name": name,
                    "code": len(nets),
                    "type": "hierarchical",
                    "position": (x, y),
                }

        # Extract power port labels (like +3V3, GND, etc.)
        power_pattern = r'\(symbol\s+\(lib_id\s+"power:([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)'
        for match in re.finditer(power_pattern, content):
            name = match.group(1)
            if name not in nets:  # Avoid duplicates
                x = float(match.group(2))
                y = float(match.group(3))
                nets[name] = {
                    "name": name,
                    "code": len(nets),
                    "type": "power",
                    "position": (x, y),
                }

        return list(nets.values())

    def _parse_sheet_blocks(self, content: str) -> list[dict[str, str]]:
        """Parse raw sheet blocks with file/name/uuid metadata."""
        sheets: list[dict[str, str]] = []
        for block_text in self._extract_balanced_blocks(content, "(sheet", exclude_prefixes=("(sheet_instances",)):
            name_match = re.search(r'\(property\s+"Sheetname"\s+"([^"]+)"', block_text)
            file_match = re.search(r'\(property\s+"Sheetfile"\s+"([^"]+)"', block_text)
            uuid_match = re.search(r'\(uuid\s+"([^"]+)"', block_text)
            if not name_match or not file_match or not uuid_match:
                continue

            sheets.append({
                "name": name_match.group(1),
                "file": file_match.group(1),
                "uuid": uuid_match.group(1),
            })

        return sheets

    def _parse_label_records(self, content: str) -> list[dict[str, Any]]:
        """Parse positioned page labels from one schematic page."""
        records: list[dict[str, Any]] = []
        patterns = (
            ("global", r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'),
            ("local", r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'),
            ("hierarchical", r'\(hierarchical_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)'),
        )
        for kind, pattern in patterns:
            for match in re.finditer(pattern, content):
                records.append(
                    {
                        "kind": kind,
                        "name": match.group(1),
                        "position": (float(match.group(2)), float(match.group(3))),
                    }
                )
        return records

    def _parse_sheet_pin_records(self, content: str) -> list[dict[str, Any]]:
        """Parse positioned sheet-pin records from one schematic page."""
        records: list[dict[str, Any]] = []
        for block_text in self._extract_balanced_blocks(content, "(sheet", exclude_prefixes=("(sheet_instances",)):
            name_match = re.search(r'\(property\s+"Sheetname"\s+"([^"]+)"', block_text)
            file_match = re.search(r'\(property\s+"Sheetfile"\s+"([^"]+)"', block_text)
            sheet_name = name_match.group(1) if name_match else ""
            sheet_file = file_match.group(1) if file_match else ""
            for pin_match in re.finditer(
                r'\(pin\s+"([^"]+)"\s+([^\s\)]+)[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)[^\)]*\)',
                block_text,
            ):
                records.append(
                    {
                        "kind": "sheet_pin",
                        "name": pin_match.group(1),
                        "pin_type": pin_match.group(2),
                        "position": (float(pin_match.group(3)), float(pin_match.group(4))),
                        "sheet_name": sheet_name,
                        "sheet_file": sheet_file,
                    }
                )
        return records

    def _parse_wire_segments(self, content: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        """Parse page wire segments as endpoint pairs."""
        segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
        pattern = r'\(wire\s+\(pts\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\s+\(xy\s+([\d.]+)\s+([\d.]+)\)'
        for match in re.finditer(pattern, content):
            segments.append(
                (
                    (float(match.group(1)), float(match.group(2))),
                    (float(match.group(3)), float(match.group(4))),
                )
            )
        return segments

    def _point_on_segment(
        self,
        point: tuple[float, float],
        segment: tuple[tuple[float, float], tuple[float, float]],
        *,
        tolerance: float = POINT_ON_SEGMENT_TOLERANCE,
    ) -> bool:
        """Return whether a point lies on a wire segment within a small tolerance."""
        (x, y) = point
        (x1, y1), (x2, y2) = segment
        cross = abs((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))
        if cross > tolerance:
            return False
        min_x, max_x = sorted((x1, x2))
        min_y, max_y = sorted((y1, y2))
        return (min_x - tolerance) <= x <= (max_x + tolerance) and (min_y - tolerance) <= y <= (max_y + tolerance)

    def find_connected_entities(self, anchor_names: set[str]) -> list[dict[str, Any]]:
        """Find labels and sheet pins connected by wire to any anchor label on this page."""
        content = _read_file_with_encoding_fallback(self.file_path.resolve())
        labels = self._parse_label_records(content)
        sheet_pins = self._parse_sheet_pin_records(content)
        segments = self._parse_wire_segments(content)
        if not segments:
            return []

        adjacency: dict[tuple[float, float], set[tuple[float, float]]] = {}
        for point_a, point_b in segments:
            adjacency.setdefault(point_a, set()).add(point_b)
            adjacency.setdefault(point_b, set()).add(point_a)

        component_segments: set[tuple[tuple[float, float], tuple[float, float]]] = set()
        for label in labels:
            if label["name"] not in anchor_names:
                continue
            touching_segments = [segment for segment in segments if self._point_on_segment(label["position"], segment)]
            if not touching_segments:
                continue
            stack = [point for segment in touching_segments for point in segment]
            visited: set[tuple[float, float]] = set()
            while stack:
                point = stack.pop()
                if point in visited:
                    continue
                visited.add(point)
                stack.extend(adjacency.get(point, ()))
            for segment in segments:
                if segment[0] in visited and segment[1] in visited:
                    component_segments.add(segment)

        if not component_segments:
            return []

        connected: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        for entity in [*labels, *sheet_pins]:
            if any(self._point_on_segment(entity["position"], segment) for segment in component_segments):
                key = (
                    entity.get("kind"),
                    entity.get("name"),
                    entity.get("position"),
                    entity.get("sheet_name"),
                )
                if key in seen:
                    continue
                seen.add(key)
                connected.append(entity)
        return connected

    def get_page_connectivity_entities(self) -> list[dict[str, Any]]:
        """Return positioned labels and sheet pins for one schematic page."""
        content = _read_file_with_encoding_fallback(self.file_path.resolve())
        return [*self._parse_label_records(content), *self._parse_sheet_pin_records(content)]

    def _parse_sheets(self, content: str) -> list[dict[str, str]]:
        """Parse hierarchical sheets."""
        return [
            {
                "name": sheet["name"],
                "file": sheet["file"],
            }
            for sheet in self._parse_sheet_blocks(content)
        ]

    def _dedupe_components(self, components: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate multi-unit and hierarchical components by reference."""
        deduped: dict[str, dict[str, Any]] = {}

        for component in components:
            reference = component.get("reference", "")
            if not reference:
                continue

            if reference not in deduped:
                deduped[reference] = deepcopy(component)
                continue

            existing = deduped[reference]

            if not existing.get("value") and component.get("value"):
                existing["value"] = component["value"]
            if not existing.get("lib_id") and component.get("lib_id"):
                existing["lib_id"] = component["lib_id"]
            if not existing.get("at") and component.get("at"):
                existing["at"] = deepcopy(component["at"])

            existing_properties = {prop.get("key"): prop.get("value") for prop in existing.get("properties", []) if prop.get("key")}
            for prop in component.get("properties", []):
                key = prop.get("key")
                value = prop.get("value")
                if key and value and key not in existing_properties:
                    existing.setdefault("properties", []).append({"key": key, "value": value})
                    existing_properties[key] = value

            if not existing.get("footprint") and component.get("footprint"):
                existing["footprint"] = component["footprint"]

            pins_by_number = {pin.get("number"): pin for pin in existing.get("pins", []) if pin.get("number")}
            for pin in component.get("pins", []):
                number = pin.get("number")
                if number and number not in pins_by_number:
                    existing.setdefault("pins", []).append(deepcopy(pin))
                    pins_by_number[number] = pin

            existing_flags = existing.setdefault("flags", dict(KICAD_FLAG_DEFAULTS))
            for flag in KICAD_SYMBOL_FLAGS:
                if flag in component.get("flags", {}):
                    existing_flags[flag] = component["flags"][flag]

        return list(deduped.values())

    def _dedupe_nets(self, nets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate nets by name while preserving first-seen metadata."""
        deduped: dict[str, dict[str, Any]] = {}

        for net in nets:
            name = net.get("name", "")
            if name and name not in deduped:
                deduped[name] = deepcopy(net)

        return list(deduped.values())

    def _dedupe_sheets(self, sheets: list[dict[str, str]]) -> list[dict[str, str]]:
        """Deduplicate sheets by name/file pair."""
        deduped = []
        seen: set[tuple[str, str]] = set()

        for sheet in sheets:
            key = (sheet.get("name", ""), sheet.get("file", ""))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(sheet)

        return deduped

    def get_components(self) -> list[SchematicComponent]:
        """Return populated components only.

        DNP (do-not-populate) components are filtered out so downstream
        analysis reflects the populated board, not the schematic drawing.
        Use get_dnp_count() to report how many were excluded.
        """
        data = self._parse_file()
        components = [SchematicComponent.from_kicad_skip(c) for c in data["components"]]
        return [c for c in components if not c.flags.get("dnp", False)]

    def get_dnp_count(self) -> int:
        """Return the number of DNP components excluded by get_components()."""
        data = self._parse_file()
        return sum(
            1 for c in data["components"]
            if c.get("flags", {}).get("dnp", False)
        )

    def get_nets(self) -> list[SchematicNet]:
        """Get all nets from schematic.

        Returns:
            List of nets
        """
        data = self._parse_file()
        return [SchematicNet.from_kicad_skip(n) for n in data["nets"]]

    def get_title_block(self) -> dict[str, str]:
        """Get title block information.

        Returns:
            Dictionary with title, date, rev, company, comment
        """
        data = self._parse_file()
        return data["title_block"]

    def get_sheets(self) -> list[dict[str, str]]:
        """Get hierarchical sheets.

        Returns:
            List of sheet information
        """
        data = self._parse_file()
        return data["sheets"]

    def get_sheet_instances(self) -> list[str]:
        """Get recursive human-readable sheet instance paths.

        Returns:
            List of sheet instance paths beginning with `/`
        """
        if self._sheet_instances is None:
            instances = ["/"]
            instances.extend(record["sheet_name_path"] for record in self.get_sheet_instance_records())
            seen: set[str] = set()
            ordered_instances: list[str] = []
            for sheet_path in instances:
                if sheet_path in seen:
                    continue
                seen.add(sheet_path)
                ordered_instances.append(sheet_path)
            self._sheet_instances = ordered_instances

        return list(self._sheet_instances)

    def get_sheet_instance_records(self) -> list[dict[str, str]]:
        """Get authoritative sheet instance records keyed by sheet UUID path."""
        if self._sheet_instance_records is None:
            records = self._collect_sheet_instance_records(
                schematic_file=self.file_path.resolve(),
                parent_name_path="/",
                parent_uuid_path="/",
                active_files={self.file_path.resolve()},
            )
            self._sheet_instance_records = [
                {
                    "sheet_name": record.sheet_name,
                    "sheet_file": record.sheet_file,
                    "sheet_uuid": record.sheet_uuid,
                    "sheet_uuid_path": record.sheet_uuid_path,
                    "sheet_name_path": record.sheet_name_path,
                    "source_schematic": record.source_schematic,
                }
                for record in records
            ]

        return [dict(record) for record in self._sheet_instance_records]

    def _collect_sheet_instance_records(
        self,
        schematic_file: Path,
        parent_name_path: str,
        parent_uuid_path: str,
        active_files: set[Path],
    ) -> list[SheetInstanceRecord]:
        parser = SchematicParser(str(schematic_file), include_child_sheets=False)
        content = _read_file_with_encoding_fallback(schematic_file)
        records: list[SheetInstanceRecord] = []

        for sheet in parser._parse_sheet_blocks(content):
            sheet_name = sheet.get("name", "").strip()
            sheet_file = sheet.get("file", "").strip()
            sheet_uuid = sheet.get("uuid", "").strip()
            if not sheet_name or not sheet_file or not sheet_uuid:
                continue

            child_file = (schematic_file.parent / sheet_file).resolve()
            if not child_file.exists():
                continue

            name_path = self._join_sheet_path(parent_name_path, sheet_name)
            uuid_path = self._join_sheet_path(parent_uuid_path, sheet_uuid)
            records.append(
                SheetInstanceRecord(
                    sheet_name=sheet_name,
                    sheet_file=sheet_file,
                    sheet_uuid=sheet_uuid,
                    sheet_uuid_path=uuid_path,
                    sheet_name_path=name_path,
                    source_schematic=str(schematic_file.resolve()),
                )
            )

            if child_file in active_files:
                continue

            records.extend(
                self._collect_sheet_instance_records(
                    schematic_file=child_file,
                    parent_name_path=name_path,
                    parent_uuid_path=uuid_path,
                    active_files=active_files | {child_file},
                )
            )

        return records

    def _join_sheet_path(self, parent_path: str, segment: str) -> str:
        if parent_path in {"", "/"}:
            return f"/{segment}"
        return f"{parent_path}/{segment}"

    def get_component_by_reference(self, reference: str) -> Optional[SchematicComponent]:
        """Get a component by its reference designator.

        Args:
            reference: Component reference (e.g., "R1", "U1")

        Returns:
            Component if found, None otherwise
        """
        for component in self.get_components():
            if component.reference == reference:
                return component
        return None

    def search_components(self, pattern: str) -> list[SchematicComponent]:
        """Search for components by pattern.

        Args:
            pattern: Search pattern (matches reference, value, or library_id)

        Returns:
            List of matching components
        """
        import re

        regex = re.compile(pattern, re.IGNORECASE)
        results = []

        for component in self.get_components():
            if (
                regex.search(component.reference)
                or regex.search(component.value)
                or regex.search(component.library_id)
            ):
                results.append(component)

        return results

    def get_component_connections(self, reference: str) -> dict[str, Any]:
        """Get all network connections for a component.

        Args:
            reference: Component reference (e.g., "R16")

        Returns:
            Dictionary with connection information:
            {
                "nets": ["net_name1", "net_name2"],
                "labels": ["label1", "label2"],
                "connected_components": ["comp1", "comp2"]
            }
        """
        content = _read_file_with_encoding_fallback(self.file_path)

        # Find the component instance
        comp_pattern = rf'\(symbol\s+[\s\S]*?\(property\s+"Reference"\s+"{re.escape(reference)}"'
        comp_match = re.search(comp_pattern, content, re.DOTALL)

        if not comp_match:
            return {"error": f"Component {reference} not found"}

        # Extract the component block (from symbol to closing paren)
        start = comp_match.start()
        depth = 0
        i = start
        while i < len(content):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1

        comp_block = content[start:i]

        # Find all pins in this component
        pins = []
        for pin_match in re.finditer(r'\(pin\s+"([^"]+)"', comp_block):
            pins.append(pin_match.group(1))

        # Search for connections by finding wires near the component position
        comp = self.get_component_by_reference(reference)
        if not comp:
            return {"error": f"Component {reference} not found"}

        cx, cy = comp.position

        # Find all labels and global labels
        labels = []
        for label_match in re.finditer(r'\((?:global_)?label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)', content):
            label_name = label_match.group(1)
            lx, ly = float(label_match.group(2)), float(label_match.group(3))
            dist = ((lx - cx)**2 + (ly - cy)**2)**0.5
            labels.append({"name": label_name, "position": (lx, ly), "distance": dist})

        # Find hierarchical labels
        for label_match in re.finditer(r'\(hierarchical_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)', content):
            label_name = label_match.group(1)
            lx, ly = float(label_match.group(2)), float(label_match.group(3))
            dist = ((lx - cx)**2 + (ly - cy)**2)**0.5
            labels.append({"name": label_name, "position": (lx, ly), "distance": dist})

        # Filter to nearby labels (within 20mm)
        nearby_labels = [l for l in labels if l["distance"] < NEARBY_LABEL_DISTANCE_MM]

        # Find nearby components (within 15mm)
        components = self.get_components()
        nearby_comps = []
        for c in components:
            if c.reference == reference:
                continue
            dist = ((c.position[0] - cx)**2 + (c.position[1] - cy)**2)**0.5
            if dist < NEARBY_COMPONENT_DISTANCE_MM:
                nearby_comps.append({
                    "reference": c.reference,
                    "value": c.value,
                    "distance": dist,
                    "position": c.position
                })

        return {
            "component": reference,
            "position": comp.position,
            "pins": pins,
            "nearby_labels": nearby_labels[:NEARBY_RESULTS_LIMIT],
            "nearby_components": nearby_comps[:NEARBY_RESULTS_LIMIT],
        }

    def trace_net(self, reference: str, pin_number: Optional[str] = None) -> dict[str, Any]:
        """Trace network connections from a component pin.

        Args:
            reference: Component reference (e.g., "R16")
            pin_number: Optional pin number to trace (if None, trace all pins)

        Returns:
            Network trace information
        """
        connections = self.get_component_connections(reference)

        if "error" in connections:
            return connections

        # Analyze the nearby data to infer network connections
        inferred_nets = []

        # Check for hierarchical labels that indicate function
        for label in connections["nearby_labels"]:
            label_name = label["name"]
            if any(keyword in label_name.upper() for keyword in
                   ["I2C", "SCL", "SDA", "SMBUS", "PMIC", "GPIO", "EN", "INT"]):
                inferred_nets.append({
                    "name": label_name,
                    "type": "signal",
                    "distance": label["distance"]
                })

        return {
            "component": reference,
            "position": connections["position"],
            "inferred_connections": inferred_nets,
            "nearby_components": connections["nearby_components"][:NEARBY_RESULTS_LIMIT],
        }

    def build_wire_network(self) -> dict[tuple[float, float], list[tuple[float, float]]]:
        """Build a graph of wire connections.

        Returns:
            Dictionary mapping each point to its connected neighbors
        """
        import re

        content = _read_file_with_encoding_fallback(self.file_path)

        # Find all wire segments
        wire_pattern = r'\(wire\s+\(pts\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\s+\(xy\s+([\d.]+)\s+([\d.]+)\)'

        network = {}

        for match in re.finditer(wire_pattern, content):
            x1, y1 = float(match.group(1)), float(match.group(2))
            x2, y2 = float(match.group(3)), float(match.group(4))

            p1 = (x1, y1)
            p2 = (x2, y2)

            if p1 not in network:
                network[p1] = []
            if p2 not in network:
                network[p2] = []

            network[p1].append(p2)
            network[p2].append(p1)

        # Find junctions and merge connections
        junction_pattern = r'\(junction\s+\(at\s+([\d.]+)\s+([\d.]+)'
        for match in re.finditer(junction_pattern, content):
            jx, jy = float(match.group(1)), float(match.group(2))
            jpos = (jx, jy)

            # For a junction, all wires meeting at this point should be connected
            # Find all wire endpoints at this position (with small tolerance)
            tolerance = JUNCTION_MATCH_TOLERANCE
            connected_points = [p for p in network if
                               abs(p[0] - jx) < tolerance and abs(p[1] - jy) < tolerance]

            # Merge all connections at junction
            all_neighbors = set()
            for p in connected_points:
                all_neighbors.update(network[p])

            for p in connected_points:
                network[p] = list(all_neighbors)

        return network

    def trace_wire_network(self, reference: str, max_depth: int = BFS_TRACE_MAX_DEPTH) -> dict[str, Any]:
        """Trace wire connections from a component.

        Args:
            reference: Component reference (e.g., "R16")
            max_depth: Maximum connection depth to trace

        Returns:
            Dictionary with traced connections and labels
        """
        import re

        # Get component position
        comp = self.get_component_by_reference(reference)
        if not comp:
            return {"error": f"Component {reference} not found"}

        cx, cy = comp.position

        # Build wire network
        network = self.build_wire_network()

        # Find all labels
        content = _read_file_with_encoding_fallback(self.file_path)

        # Find hierarchical labels
        h_labels = []
        for label_match in re.finditer(
            r'\(hierarchical_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)',
            content
        ):
            name = label_match.group(1)
            lx, ly = float(label_match.group(2)), float(label_match.group(3))
            h_labels.append({"name": name, "position": (lx, ly)})

        # Find global labels
        g_labels = []
        for label_match in re.finditer(
            r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)',
            content
        ):
            name = label_match.group(1)
            lx, ly = float(label_match.group(2)), float(label_match.group(3))
            g_labels.append({"name": name, "position": (lx, ly)})

        all_labels = h_labels + g_labels

        # Start from component position and trace
        max_tolerance = WIRE_TRACE_MAX_TOLERANCE_MM  # for components with pin offset
        start_point = None
        min_dist = float('inf')

        # Find the nearest wire endpoint to component
        for point in network:
            dist = ((point[0] - cx)**2 + (point[1] - cy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                start_point = point

        # Only proceed if the nearest point is within tolerance
        if min_dist > max_tolerance:
            return {
                "component": reference,
                "position": comp.position,
                "connected_labels": [],
                "trace_path": [],
                "error": f"No wire found within {max_tolerance}mm (nearest: {min_dist:.2f}mm)",
            }

        # BFS trace through network
        visited = set()
        queue = [start_point]
        trace_path = []
        connected_labels = []

        while queue and len(visited) < max_depth:
            point = queue.pop(0)
            if point in visited:
                continue
            visited.add(point)

            trace_path.append(point)

            # Check if this point is near a label
            label_tolerance = LABEL_MATCH_TOLERANCE_MM
            for label in all_labels:
                lx, ly = label["position"]
                dist = ((point[0] - lx)**2 + (point[1] - ly)**2)**0.5
                if dist < label_tolerance and not any(l["name"] == label["name"] for l in connected_labels):
                    connected_labels.append({
                        "name": label["name"],
                        "position": label["position"],
                        "distance": dist,
                    })

            # Add neighbors to queue
            if point in network:
                for neighbor in network[point]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        # Find nearby power symbols
        power_tolerance = POWER_SYMBOL_TOLERANCE_MM
        power_pattern = r'\(symbol\s+\(lib_id\s+"power:([^"]+)"[\s\S]*?\(at\s+([\d.]+)\s+([\d.]+)'
        for match in re.finditer(power_pattern, content):
            power_name = match.group(1)
            px, py = float(match.group(2)), float(match.group(3))
            dist = ((px - cx)**2 + (py - cy)**2)**0.5
            if dist < power_tolerance:
                connected_labels.append({
                    "name": f"POWER:{power_name}",
                    "position": (px, py),
                    "distance": dist,
                })

        return {
            "component": reference,
            "position": comp.position,
            "connected_labels": connected_labels,
            "trace_path": trace_path,
        }
