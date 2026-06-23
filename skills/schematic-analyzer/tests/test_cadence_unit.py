"""Unit tests for Cadence XML parser core functions.

Tests coordinate transforms, format detection, and symbol connection point
calculations without requiring large XML test data files.
"""

import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tools.cadence.connectivity import CadenceConnectivityBuilder
from tools.cadence.xml_parser import (
    CadenceXMLParser,
    _transform_pin_coords,
    _get_symbol_connection_point_static,
    is_cadence_xml,
)
from tools.kicad.schematic_parser import SchematicComponent
from tools.project_indexer import ComponentInstance, ProjectIndexer


def _component_instance(reference: str) -> ComponentInstance:
    return ComponentInstance(
        reference=reference,
        instance_id=reference,
        value="10k",
        lib_id="Device:R",
        footprint=None,
        source_schematic=Path("/tmp/design.xml"),
        sheet_path="/",
        sheet_type="root",
        pins=[],
        properties={},
        flags={"dnp": False},
    )


class TestTransformPinCoords:
    """Test _transform_pin_coords — absolute pin coordinate calculation."""

    def test_no_transform(self):
        """Pin at part origin with no offset."""
        assert _transform_pin_coords(100, 200, 0, 0, 0, 0) == (100, 200)

    def test_offset_only(self):
        """Pin with hotpoint offset, no rotation/mirror."""
        assert _transform_pin_coords(100, 200, 10, 20, 0, 0) == (110, 220)

    def test_negative_offset(self):
        """Pin with negative offset."""
        assert _transform_pin_coords(100, 200, -5, -10, 0, 0) == (95, 190)


class TestGetSymbolConnectionPoint:
    """Test connection point calculation with rotation and mirror."""

    def test_no_rotation_no_mirror(self):
        """Default orientation — pin offset applied directly."""
        # pin_offset = (10, 0), loc = (100, 200)
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 0, 0)
        assert (x, y) == (110, 200)

    def test_rotation_90(self):
        """90° rotation: dx,dy = -dy,dx → (10,0) becomes (0,10)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 1, 0)
        assert (x, y) == (100, 210)

    def test_rotation_180(self):
        """180° rotation: dx,dy = -dx,-dy → (10,0) becomes (-10,0)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 2, 0)
        assert (x, y) == (90, 200)

    def test_rotation_270(self):
        """270° rotation: dx,dy = dy,-dx → (10,0) becomes (0,-10)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 3, 0)
        assert (x, y) == (100, 190)

    def test_mirror_no_rotation(self):
        """Mirror flips X: (10,0) becomes (-10,0)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 0, 1)
        assert (x, y) == (90, 200)

    def test_mirror_with_rotation_90(self):
        """Mirror + 90°: (10,0) → mirror → (-10,0) → rot90 → (0,-10)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 1, 1)
        assert (x, y) == (100, 190)

    def test_mirror_with_rotation_180(self):
        """Mirror + 180°: (10,0) → mirror → (-10,0) → rot180 → (10,0)."""
        x, y = _get_symbol_connection_point_static(100, 200, (10, 0), 2, 1)
        assert (x, y) == (110, 200)


class TestIsCadenceXml:
    """Test Cadence XML format detection."""

    def test_valid_cadence_xml(self):
        """File with dsn.xsd and <Design should be detected."""
        content = '<?xml version="1.0"?>\n<Design xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="dsn.xsd">'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(content)
            f.flush()
            assert is_cadence_xml(f.name) is True

    def test_non_cadence_xml(self):
        """Generic XML should not be detected."""
        content = '<?xml version="1.0"?>\n<root><item>test</item></root>'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(content)
            f.flush()
            assert is_cadence_xml(f.name) is False

    def test_nonexistent_file(self):
        """Missing file should return False."""
        assert is_cadence_xml("/nonexistent/file.xml") is False


class TestCadenceDnpFiltering:
    """DNP filtering stays at the parser/index boundary."""

    def test_component_lookup_hides_dnp_components(self):
        parser = object.__new__(CadenceXMLParser)
        parser._components = [
            SchematicComponent(
                reference="R1",
                value="10k",
                library_id="Device:R",
                flags={"dnp": False},
            ),
            SchematicComponent(
                reference="R2",
                value="DNP",
                library_id="Device:R",
                flags={"dnp": True},
            ),
        ]
        parser._pin_net_map = {"R1": {"1": "NET_A"}, "R2": {"1": "NET_A"}}
        parser._ensure_parsed = lambda: None

        assert parser.get_component_by_reference("R1").reference == "R1"
        assert parser.get_component_by_reference("R2") is None
        assert parser.get_component_connections("R2") == {"error": "Component R2 not found"}

    def test_connectivity_ignores_refs_filtered_from_project_index(self):
        builder = CadenceConnectivityBuilder()
        builder._get_pin_net_map = lambda root: (
            {"R1": {"1": "NET_A"}, "R2": {"1": "NET_A"}},
            "xml_coordinate",
            None,
            None,
        )
        project_index = SimpleNamespace(
            components={"R1": _component_instance("R1")},
            resolver=None,
        )

        graph = builder.build(project_index, Path("/tmp/design.xml"))

        assert set(graph.component_nets) == {"R1"}
        assert graph.all_nets["NET_A"].connected_refs == ["R1"]
        assert graph.all_nets["NET_A"].connected_pins == [("R1", "1", "")]

    def test_cadence_page_counts_use_filtered_components(self, tmp_path, monkeypatch):
        import tools.cadence.netlist_dat_parser as netlist_dat_parser
        import tools.parser_factory as parser_factory

        (tmp_path / "pstxprt.dat").write_text("", encoding="utf-8")
        monkeypatch.setattr(netlist_dat_parser, "find_netlist_dir", lambda root: tmp_path)
        monkeypatch.setattr(
            netlist_dat_parser,
            "parse_pstxprt",
            lambda path: {
                "R1": {"page": "page1"},
                "R2": {"page": "page1"},
                "C1": {"page": "page2"},
            },
        )
        monkeypatch.setattr(
            parser_factory,
            "get_schematic_parser",
            lambda *args, **kwargs: SimpleNamespace(get_page_names=lambda: ["Power", "IO"]),
        )

        components = {
            "R1": _component_instance("R1"),
            "C1": _component_instance("C1"),
        }
        scope = SimpleNamespace(root_schematic=tmp_path / "design.xml")

        enriched = ProjectIndexer._enrich_cadence_pages(scope, components, [], {})

        assert enriched is not None
        _components, hierarchy, _sheet_names = enriched
        assert {sheet.sheet_path: sheet.component_count for sheet in hierarchy} == {
            "/page1": 1,
            "/page2": 1,
        }


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
