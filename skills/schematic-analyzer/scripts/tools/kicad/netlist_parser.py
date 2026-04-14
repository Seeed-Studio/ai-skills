"""KiCad netlist parser for accurate component network tracking."""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..utils.file_handlers import validate_kicad_file


@dataclass
class NetlistComponent:
    """Component from netlist file."""

    reference: str
    value: str
    library: str
    sheet_instance_path: str
    footprint: Optional[str] = None
    pins: dict[str, str] = field(default_factory=dict)  # pin_number -> net_name
    units: list[str] = field(default_factory=list)


@dataclass
class NetlistNet:
    """Net from netlist file."""

    name: str
    code: int
    pins: list[tuple[str, str]] = field(default_factory=list)  # (reference, pin_number)


class NetlistParser:
    """Parser for KiCad netlist files (.xml)."""

    def __init__(self, file_path: str) -> None:
        """Initialize parser with netlist file.

        Args:
            file_path: Path to .xml netlist file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a .xml file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Netlist file not found: {file_path}")

        if self.file_path.suffix != ".xml":
            raise ValueError(f"Netlist file must be .xml, got: {self.file_path.suffix}")

        self._data: Optional[dict[str, Any]] = None

    def _normalize_sheet_instance_path(self, raw_path: Optional[str]) -> str:
        normalized = (raw_path or "").rstrip("/")
        if not normalized:
            return "/"
        return normalized

    def _resolve_component_key(self, reference: str) -> Optional[str]:
        ref_key = reference.upper()
        return ref_key if ref_key in self.get_components() else None

    def _parse_file(self) -> dict[str, Any]:
        """Parse the netlist XML file.

        Returns:
            Parsed data structure
        """
        if self._data is not None:
            return self._data

        try:
            tree = ET.parse(self.file_path)
        except ET.ParseError as exc:
            raise ValueError(
                f"Failed to parse KiCad netlist file '{self.file_path}': {exc}"
            ) from exc
        root = tree.getroot()

        # Parse components (KiCad 9.0 uses <comp> not <component>)
        components: dict[str, NetlistComponent] = {}
        for comp in root.findall(".//comp"):
            ref = (comp.get("ref") or "").upper()
            value = comp.findtext("value", "")
            libsource = comp.find("libsource")
            lib_name = libsource.get("lib", "") if libsource is not None else ""
            part_name = libsource.get("part", "") if libsource is not None else ""
            library = f"{lib_name}:{part_name}" if lib_name and part_name else part_name or lib_name
            footprint = comp.findtext("footprint") or None
            sheetpath_elem = comp.find("sheetpath")
            sheet_instance_path = self._normalize_sheet_instance_path(
                sheetpath_elem.get("names") if sheetpath_elem is not None else None
            )
            units = [
                unit.get("name", "")
                for unit in comp.findall("units/unit")
                if unit.get("name")
            ]

            # Pins will be populated from nets later
            components[ref] = NetlistComponent(
                reference=ref,
                value=value,
                library=library,
                sheet_instance_path=sheet_instance_path,
                footprint=footprint,
                pins={},  # Empty initially, will populate from nets
                units=units,
            )

        # Parse nets and populate component pins
        nets: dict[str, NetlistNet] = {}
        warnings: list[str] = []
        for net in root.findall(".//net"):
            try:
                code = int(net.get("code", "0"))
            except (ValueError, TypeError):
                code = 0
            name = net.get("name")
            if not name:
                continue

            pins_list = []
            for node in net.findall("node"):
                ref = (node.get("ref") or "").upper()
                pin_num = node.get("pin")
                if ref and pin_num:
                    pins_list.append((ref, pin_num))

                    # Populate component pins
                    if ref in components:
                        components[ref].pins[pin_num] = name

            nets[name] = NetlistNet(name=name, code=code, pins=pins_list)

        self._data = {
            "components": components,
            "nets": nets,
            "ref_to_instances": {ref: [ref] for ref in sorted(components)},
            "warnings": warnings,
        }

        return self._data

    def get_components(self) -> dict[str, NetlistComponent]:
        """Get all components from netlist.

        Returns:
            Dictionary mapping instance_id to component
        """
        data = self._parse_file()
        return data["components"]

    def get_nets(self) -> dict[str, NetlistNet]:
        """Get all nets from netlist.

        Returns:
            Dictionary mapping net name to net
        """
        data = self._parse_file()
        return data["nets"]

    def get_component_nets(self, reference: str) -> dict[str, list[str]]:
        """Get all networks for a component.

        Args:
            reference: Component reference (e.g., "R16")

        Returns:
            Dictionary mapping net name to list of connected pins
        """
        components = self.get_components()
        component_key = self._resolve_component_key(reference)
        if component_key is None or component_key not in components:
            return {}

        comp = components[component_key]
        net_pins = {}

        for pin_num, net_name in comp.pins.items():
            if net_name not in net_pins:
                net_pins[net_name] = []
            net_pins[net_name].append(pin_num)

        return net_pins

    def get_net_components(self, net_name: str) -> list[tuple[str, str]]:
        """Get all components connected to a net.

        Args:
            net_name: Net name (e.g., "PMIC_I2C_SCL")

        Returns:
            List of (reference, pin_number) tuples
        """
        nets = self.get_nets()
        if net_name not in nets:
            return []

        return nets[net_name].pins

    def get_ref_to_instances(self) -> dict[str, list[str]]:
        """Get reference-to-instance mapping for identity disambiguation."""
        data = self._parse_file()
        return data["ref_to_instances"]

    def trace_connection(self, reference: str, pin_number: Optional[str] = None) -> dict[str, Any]:
        """Trace connections from a component pin.

        Args:
            reference: Component reference
            pin_number: Optional pin number (if None, trace all pins)

        Returns:
            Connection information
        """
        components = self.get_components()
        component_key = self._resolve_component_key(reference)
        if component_key is None or component_key not in components:
            return {"error": f"Component {reference} not found in netlist"}

        comp = components[component_key]

        if pin_number:
            # Trace specific pin
            if pin_number not in comp.pins:
                return {"error": f"Pin {pin_number} not found in component {reference}"}

            net_name = comp.pins[pin_number]
            nets = self.get_nets()
            connected = nets[net_name].pins if net_name in nets else []

            return {
                "component": comp.reference,
                "instance_id": comp.reference,
                "pin": pin_number,
                "net": net_name,
                "connected_to": [(ref, pin) for ref, pin in connected if ref != comp.reference],
            }

        else:
            # Trace all pins
            net_connections = {}
            for pin_num, net_name in comp.pins.items():
                nets = self.get_nets()
                connected = nets[net_name].pins if net_name in nets else []
                net_connections[net_name] = {
                    "pin": pin_num,
                    "connected_to": [(ref, pin) for ref, pin in connected if ref != reference],
                }

            return {
                "component": comp.reference,
                "instance_id": comp.reference,
                "nets": net_connections,
            }
