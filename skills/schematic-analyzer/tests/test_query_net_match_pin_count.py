import sys
from pathlib import Path


SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from analyzer import SchematicAnalyzer


def _build_analyzer(candidates):
    analyzer = object.__new__(SchematicAnalyzer)
    analyzer._searchable_net_match_candidates = lambda: candidates
    analyzer._truncate_items = lambda items, include_all=False: (items, False)
    return analyzer


def test_query_net_match_derives_pin_count_from_pins_when_missing() -> None:
    analyzer = _build_analyzer(
        [
            {
                "name": "VCC_LED",
                "kind": "net",
                "occurrence_count": 1,
                "pages": ["SCH_TOP"],
                "mapped_to_net": True,
                "pins": [["R6", "2"], ["U2", "4"]],
            }
        ]
    )

    payload = analyzer.query_net_match("VCC")

    assert payload["matches"][0]["pin_count"] == 2


def test_query_net_match_tolerates_missing_pin_count_without_pins() -> None:
    analyzer = _build_analyzer(
        [
            {
                "name": "LEDSTROBE",
                "kind": "local_label",
                "occurrence_count": 1,
                "pages": ["FLASH"],
                "mapped_to_net": False,
            }
        ]
    )

    payload = analyzer.query_net_match("LED")

    assert "pin_count" not in payload["matches"][0]
