"""Main schematic analyzer orchestrator.

Coordinates the analysis workflow:
Phase 1: Netlist semantic parsing
Phase 0: Core component detection
Phase 2: Component role identification
Phase 3: Topology extraction
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from collections import Counter

# Ensure scripts directory is in path for imports
_SCRIPTS_DIR = Path(__file__).parent.resolve()
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from cache_manager import CacheManager
from tools.connectivity_builder import ConnectivityBuilder
from tools.core_ranker import rank_core_candidates
from tools.overlay_interpreter import OverlayInterpreter
from tools.project_indexer import ProjectIndexer
from tools.scope_resolver import ScopeResolver
from tools.synthesis import SynthesisEngine


@dataclass
class AnalysisResult:
    """Complete analysis result."""

    meta: dict[str, Any]
    core_components: list[dict[str, Any]]
    components: list[dict[str, Any]]
    nets: list[dict[str, Any]]
    subsystems: list[dict[str, Any]]
    hierarchy: list[dict[str, Any]]
    statistics: dict[str, Any]
    component_nets: dict[str, Any] = field(default_factory=dict)  # ref -> {pin: net_name}


class SchematicAnalyzer:
    """Main analyzer class for KiCad schematics."""

    DEFAULT_QUERY_LIMIT = 10

    def __init__(
        self,
        schematic_path: str,
        rule_paths: Optional[list[str] | tuple[str, ...]] = None,
        pattern_sources: Optional[list[str] | tuple[str, ...]] = None,
    ):
        """Initialize analyzer.

        Args:
            schematic_path: Path to .kicad_sch file
            rule_paths: Runtime component rule YAML overlays
            pattern_sources: Runtime subsystem pattern YAML files/directories
        """
        self.schematic_path = Path(schematic_path)
        self.project_path = self.schematic_path.parent
        self.cache = CacheManager(str(self.project_path))
        self.rule_paths = tuple(str(Path(path).resolve()) for path in (rule_paths or ()))
        self.pattern_sources = tuple(str(Path(path).resolve()) for path in (pattern_sources or ()))
        self.structural_context_signature = self._compute_structural_context_signature()
        self.yaml_signature = self._compute_yaml_signature()
        self.context_signature = self._compute_context_signature()

        # Lazy load parser
        self._parser = None
        self._local_parsers: dict[Path, Any] = {}
        self._scope = None
        self._project_index = None
        self._overlay_interpreter = None
        self._synthesis_engine = None
        self._components = []
        self._nets = []
        self._hierarchy = []
        self.last_execution: dict[str, Any] = {}

    @property
    def parser(self):
        """Lazy load the schematic parser."""
        if self._parser is None:
            from tools.parser_factory import get_schematic_parser
            self._parser = get_schematic_parser(str(self.schematic_path))
        return self._parser

    @property
    def scope(self):
        """Lazy load resolved project scope."""
        if self._scope is None:
            self._scope = ScopeResolver.resolve(self.schematic_path)
        return self._scope

    @property
    def project_index(self):
        """Lazy load the project index."""
        if self._project_index is None:
            self._project_index = ProjectIndexer().build(self.schematic_path)
        return self._project_index

    @property
    def overlay_interpreter(self) -> OverlayInterpreter:
        """Lazy load the explicit-only pattern interpreter for analyzer paths."""
        if self._overlay_interpreter is None:
            self._overlay_interpreter = self._build_overlay_interpreter(pattern_sources=self.pattern_sources)
        return self._overlay_interpreter

    @property
    def synthesis_engine(self) -> SynthesisEngine:
        """Lazy load the final synthesis layer."""
        if self._synthesis_engine is None:
            self._synthesis_engine = SynthesisEngine(
                root_schematic=self.schematic_path,
                analysis_schematic_paths=self._get_analysis_schematic_paths(),
                local_parser_factory=self._get_local_parser,
            )
        return self._synthesis_engine

    def _get_local_parser(self, schematic_file: Path):
        """Get a non-recursive parser for a single schematic page."""
        resolved = schematic_file.resolve()
        if resolved not in self._local_parsers:
            from tools.parser_factory import get_schematic_parser
            self._local_parsers[resolved] = get_schematic_parser(str(resolved), include_child_sheets=False)
        return self._local_parsers[resolved]

    def _get_referenced_schematic_paths(self) -> list[Path]:
        """Return the root schematic and all hierarchy-referenced sheet files."""
        return [self.scope.root_schematic, *self.scope.referenced_sheets]

    def _get_analysis_schematic_paths(self) -> list[Path]:
        """Return every schematic file that should participate in this analysis."""
        return list(self._get_referenced_schematic_paths())

    def analyze(
        self,
        force: bool = False,
        phases: Optional[list[int]] = None,
        focus: Optional[str] = None,
        reuse_cache: str = "none",
    ) -> AnalysisResult:
        """Run full analysis.

        Args:
            force: Force re-analysis ignoring cache
            phases: Specific phases to run (default: all)
            focus: Focus on specific subsystem
            reuse_cache: Reuse structural cache layers: none, index, or structural

        Returns:
            AnalysisResult with all analysis data
        """
        if phases is None:
            phases = [0, 1, 2, 3]
        if reuse_cache not in {"none", "index", "structural"}:
            raise ValueError(f"Unsupported reuse_cache mode: {reuse_cache}")

        if reuse_cache == "none":
            need_refresh, _reason, cached_hash = self.cache.should_refresh(
                str(self.schematic_path),
                force=force,
                context_signature=self.context_signature,
            )

            if not need_refresh and cached_hash:
                cached = self.cache.get_cached_analysis(cached_hash)
                if cached:
                    result = AnalysisResult(**cached)
                    if focus:
                        result = self._apply_focus(result, focus)
                    self.last_execution = {
                        "mode": "analyze",
                        "force": force,
                        "focus": focus,
                        "reuse_cache": reuse_cache,
                        "final_cache": "hit",
                        "structural_phase_1_cache": False,
                        "structural_phase_0_cache": False,
                        "analysis_cache_key": cached_hash,
                        "structural_cache_key": self._structural_cache_key(),
                        "loaded_patterns": list(result.meta.get("loaded_patterns", [])),
                        "matched_patterns": list(result.meta.get("matched_patterns", [])),
                    }
                    return result

        schematic_hash = self.cache.compute_schematic_hash(self.schematic_path)
        structural_cache_key = self._structural_cache_key()
        analysis_cache_key = self._analysis_cache_key()
        phase_1_from_cache = False
        phase_0_from_cache = False

        if 1 in phases and reuse_cache in {"index", "structural"} and not force:
            phase_1_result = self._load_phase_result(1, structural_cache_key)
            phase_1_from_cache = phase_1_result is not None
        elif 1 in phases:
            phase_1_result = self._run_phase_1()
            self.cache.save_phase_result(structural_cache_key, 1, phase_1_result)
        else:
            phase_1_result = self._load_phase_result(1, analysis_cache_key, structural_cache_key)

        if 0 in phases and not phase_1_result:
            phase_1_result = self._run_phase_1()
            self.cache.save_phase_result(structural_cache_key, 1, phase_1_result)

        if 0 in phases and reuse_cache == "structural" and not force:
            phase_0_result = self._load_phase_result(0, structural_cache_key)
            phase_0_from_cache = phase_0_result is not None
        elif 0 in phases:
            phase_0_result = self._run_phase_0(phase_1_result)
            self.cache.save_phase_result(structural_cache_key, 0, phase_0_result)
        else:
            phase_0_result = self._load_phase_result(0, analysis_cache_key, structural_cache_key)

        if 0 in phases and not phase_0_result:
            phase_0_result = self._run_phase_0(phase_1_result)
            self.cache.save_phase_result(structural_cache_key, 0, phase_0_result)

        if 2 in phases:
            phase_2_result = self._run_phase_2(phase_0_result, phase_1_result)
            self.cache.save_phase_result(analysis_cache_key, 2, phase_2_result)
        else:
            phase_2_result = self._load_phase_result(2, analysis_cache_key)

        if 3 in phases:
            phase_3_result = self._run_phase_3(phase_0_result, phase_1_result, phase_2_result)
            self.cache.save_phase_result(analysis_cache_key, 3, phase_3_result)
        else:
            phase_3_result = self._load_phase_result(3, analysis_cache_key)

        result = self._combine_results(
            phase_0_result,
            phase_1_result,
            phase_2_result,
            phase_3_result,
            schematic_hash,
        )

        self.cache.save_analysis(
            str(self.schematic_path),
            asdict(result),
            phases,
            context_signature=self.context_signature,
        )

        # Apply focus filter if specified
        if focus:
            result = self._apply_focus(result, focus)

        self.last_execution = {
            "mode": "analyze",
            "force": force,
            "focus": focus,
            "reuse_cache": reuse_cache,
            "final_cache": "bypassed" if force else "miss",
            "structural_phase_1_cache": phase_1_from_cache,
            "structural_phase_0_cache": phase_0_from_cache,
            "analysis_cache_key": analysis_cache_key,
            "structural_cache_key": structural_cache_key,
            "loaded_patterns": list(phase_3_result.get("loaded_patterns", [])),
            "matched_patterns": list(phase_3_result.get("matched_patterns", [])),
        }

        return result

    def interpret(
        self,
        force: bool = False,
        focus: Optional[str] = None,
    ) -> AnalysisResult:
        """Re-run interpretation layers using cached structural phases."""
        structural_cache_key = self._structural_cache_key()
        analysis_cache_key = self._analysis_cache_key()

        if not force:
            need_refresh, _reason, cached_hash = self.cache.should_refresh(
                str(self.schematic_path),
                force=False,
                context_signature=self.context_signature,
            )
            if not need_refresh and cached_hash:
                cached = self.cache.get_cached_analysis(cached_hash)
                if cached:
                    result = AnalysisResult(**cached)
                    if focus:
                        result = self._apply_focus(result, focus)
                    self.last_execution = {
                        "mode": "interpret",
                        "force": force,
                        "focus": focus,
                        "reuse_cache": "structural",
                        "final_cache": "hit",
                        "structural_phase_1_cache": True,
                        "structural_phase_0_cache": True,
                        "analysis_cache_key": cached_hash,
                        "structural_cache_key": structural_cache_key,
                        "loaded_patterns": list(result.meta.get("loaded_patterns", [])),
                        "matched_patterns": list(result.meta.get("matched_patterns", [])),
                    }
                    return result

        if force:
            phase_1_result = self._run_phase_1()
            self.cache.save_phase_result(structural_cache_key, 1, phase_1_result)
            phase_0_result = self._run_phase_0(phase_1_result)
            self.cache.save_phase_result(structural_cache_key, 0, phase_0_result)
        else:
            phase_1_result = self._load_phase_result(1, structural_cache_key)
            phase_0_result = self._load_phase_result(0, structural_cache_key)
            if not phase_1_result or not phase_0_result:
                raise RuntimeError("No cached structural index found. Run 'analyze' first.")

        phase_2_result = self._run_phase_2(phase_0_result, phase_1_result)
        self.cache.save_phase_result(analysis_cache_key, 2, phase_2_result)
        phase_3_result = self._run_phase_3(phase_0_result, phase_1_result, phase_2_result)
        self.cache.save_phase_result(analysis_cache_key, 3, phase_3_result)

        schematic_hash = self.cache.compute_schematic_hash(self.schematic_path)
        result = self._combine_results(
            phase_0_result,
            phase_1_result,
            phase_2_result,
            phase_3_result,
            schematic_hash,
        )
        self.cache.save_analysis(
            str(self.schematic_path),
            asdict(result),
            [0, 1, 2, 3],
            context_signature=self.context_signature,
        )

        if focus:
            result = self._apply_focus(result, focus)

        self.last_execution = {
            "mode": "interpret",
            "force": force,
            "focus": focus,
            "reuse_cache": "structural",
            "final_cache": "bypassed" if force else "miss",
            "structural_phase_1_cache": not force,
            "structural_phase_0_cache": not force,
            "analysis_cache_key": analysis_cache_key,
            "structural_cache_key": structural_cache_key,
            "loaded_patterns": list(phase_3_result.get("loaded_patterns", [])),
            "matched_patterns": list(phase_3_result.get("matched_patterns", [])),
        }

        return result

    def export_raw(self) -> AnalysisResult:
        """Export raw parsed schematic structure without inference."""
        phase_1_result = self._run_phase_1()
        components = self._serialize_components(phase_1_result.get("component_nets", {}))
        schematic_hash = self.cache.compute_schematic_hash(self.schematic_path)

        return AnalysisResult(
            meta={
                "project_name": self.scope.project_name,
                "project_id": self.project_path.name,
                "resolved_project_name": self.scope.project_name,
                "schematic_path": str(self.schematic_path),
                "analyzed_at": datetime.now().isoformat(),
                "schematic_hash": schematic_hash,
                "version": CacheManager.CACHE_VERSION,
                "netlist_available": phase_1_result.get("netlist_available", False),
                "export_mode": "raw",
            },
            core_components=[],
            components=components,
            nets=phase_1_result.get("nets", []),
            subsystems=[],
            hierarchy=phase_1_result.get("hierarchy", []),
            statistics={
                "total_components": len(components),
                "total_nets": len(phase_1_result.get("nets", [])),
                "subsystem_count": 0,
                "core_component_count": 0,
            },
            component_nets=phase_1_result.get("component_nets", {}),
        )

    def _update_signature_from_source(self, sha256: Any, raw_source: str) -> None:
        """Feed a file or directory source into a hash accumulator."""
        source = Path(raw_source)
        sha256.update(str(source).encode("utf-8"))
        if source.is_file():
            sha256.update(source.read_bytes())
            return
        if source.is_dir():
            for child in sorted(source.glob("*.yaml")):
                sha256.update(str(child.relative_to(source)).encode("utf-8"))
                sha256.update(child.read_bytes())

    def _compute_structural_context_signature(self) -> str:
        """Compute a stable signature for structural-only inputs."""
        return ""

    def _compute_yaml_signature(self) -> str:
        """Compute a stable signature for runtime rule and pattern inputs."""
        import hashlib

        sha256 = hashlib.sha256()
        for rule_path in self.rule_paths:
            self._update_signature_from_source(sha256, rule_path)
        for pattern_source in self.pattern_sources:
            self._update_signature_from_source(sha256, pattern_source)

        return sha256.hexdigest()[:16] if self.rule_paths or self.pattern_sources else ""

    def _compute_context_signature(self) -> str:
        """Compute the combined signature for final interpreted analysis cache."""
        import hashlib

        if not self.structural_context_signature and not self.yaml_signature:
            return ""

        sha256 = hashlib.sha256()
        sha256.update(self.structural_context_signature.encode("utf-8"))
        sha256.update(b":")
        sha256.update(self.yaml_signature.encode("utf-8"))
        return sha256.hexdigest()[:16]

    def _structural_cache_key(self) -> str:
        """Cache key for structural phases reusable by interpret/analyze."""
        return self.cache.compute_cache_key(self.schematic_path, self.structural_context_signature)

    def _analysis_cache_key(self) -> str:
        """Cache key for full interpreted analysis."""
        return self.cache.compute_cache_key(self.schematic_path, self.context_signature)

    def _load_phase_result(self, phase: int, *cache_keys: str) -> dict[str, Any]:
        """Load the first available phase result across candidate cache keys."""
        for cache_key in cache_keys:
            if not cache_key:
                continue
            cached = self.cache.get_phase_result(cache_key, phase)
            if cached:
                return cached
        return {}

    def _run_phase_0(self, phase_1: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Phase 0: Core component detection."""
        component_nets = (phase_1 or {}).get("component_nets", {})
        comp_dicts = self._serialize_components(component_nets)

        core = rank_core_candidates(comp_dicts, rule_paths=self.rule_paths)
        main_ctrl_dict = None
        if core:
            main_ctrl_dict = {
                "reference": core[0].reference,
                "instance_id": core[0].instance_id,
                "sheet_instance_path": core[0].sheet_instance_path,
            }

        return {
            "components": comp_dicts,
            "core_components": [asdict(c) for c in core],
            "main_controller": main_ctrl_dict,
        }

    def build_overview(self) -> dict[str, Any]:
        """Build the structural project overview used by the light-refactor CLI."""
        phase_1 = self._run_phase_1()
        phase_0 = self._run_phase_0(phase_1)
        components = phase_0["components"]
        component_nets = phase_1["component_nets"]

        page_navigation: list[dict[str, Any]] = []
        page_index_by_path: dict[str, int] = {}
        for index, sheet in enumerate(self.project_index.hierarchy, start=1):
            entry = {
                "page_index": index,
                "page_name": sheet.sheet_name,
                "page_source_file": sheet.sheet_file,
                "page_type": sheet.sheet_type,
                "symbol_count": sheet.component_count,
            }
            page_navigation.append(entry)
            page_index_by_path[sheet.sheet_path] = index

        core_component_candidates: list[dict[str, Any]] = []
        component_by_ref = {component["reference"]: component for component in components}
        for candidate_index, candidate in enumerate(phase_0["core_components"], start=1):
            component = component_by_ref.get(candidate["reference"])
            if component is None:
                continue
            core_component_candidates.append(
                {
                    "candidate_index": candidate_index,
                    "reference": candidate["reference"],
                    "value": candidate["value"],
                    "page_index": page_index_by_path.get(component.get("sheet_instance_path", "/"), 1),
                    "page_name": self._sheet_name_from_path(component.get("sheet_instance_path", "/")),
                    "connected_net_count": candidate["net_count"],
                    "neighboring_symbol_count": self._neighbor_count(candidate["reference"], component_nets),
                }
            )

        core_component_candidates.sort(
            key=lambda candidate: (
                candidate["connected_net_count"],
                candidate["neighboring_symbol_count"],
                candidate["reference"],
            ),
            reverse=True,
        )
        for candidate_index, candidate in enumerate(core_component_candidates, start=1):
            candidate["candidate_index"] = candidate_index

        return {
            "project_overview": {
                "project_page_count": len(page_navigation),
                "project_component_count": len(self.project_index.components),
                "project_dnp_count": self.project_index.statistics.dnp_filtered,
                "project_net_count": len(phase_1["nets"]),
                "root_schematic_filename": self.scope.root_schematic.name,
                "referenced_page_count": len(self.scope.referenced_sheets),
            },
            "page_navigation": page_navigation,
            "core_component_candidates": core_component_candidates,
        }

    def query_page(self, page_index: int) -> dict[str, Any]:
        """Return one page inspection payload."""
        if page_index < 1 or page_index > len(self.project_index.hierarchy):
            raise LookupError(f"Unknown page index: {page_index}")

        phase_1 = self._run_phase_1()
        sheet = self.project_index.hierarchy[page_index - 1]
        components = [
            self._component_summary(component)
            for component in self.project_index.components.values()
            if component.sheet_path == sheet.sheet_path
        ]
        nets = self._page_nets(sheet.sheet_path, phase_1["component_nets"])
        return {
            "query_type": "page",
            "index": page_index,
            "name": sheet.sheet_name,
            "file": sheet.sheet_file,
            "type": sheet.sheet_type,
            "component_count": len(components),
            "net_count": len(nets),
            "components": components,
            "nets": nets,
        }

    def query_component(self, reference: str, *, include_full: bool = False) -> dict[str, Any]:
        """Return one component inspection payload."""
        phase_1 = self._run_phase_1()
        ref = reference.upper()
        component = self.project_index.components.get(ref)
        if component is None:
            suggestion = self._suggest_closest_ref(ref)
            msg = f"Component '{ref}' not found"
            if suggestion:
                msg += f". Did you mean '{suggestion}'?"
            raise LookupError(msg)

        # Use page info from component_nets (from pstxprt.dat) if available
        comp_nets = phase_1["component_nets"].get(ref, {})
        sheet_path = comp_nets.get("sheet_path", component.sheet_path)

        # Try to find page_index from hierarchy
        page_index = 1
        try:
            page_index = next(
                index for index, sheet in enumerate(self.project_index.hierarchy, start=1)
                if sheet.sheet_path == sheet_path
            )
        except StopIteration:
            # For Cadence with pstxprt.dat, extract page number from sheet_path
            page_index = self._extract_page_index(sheet_path)

        nets: list[dict[str, str]] = []
        seen_net_pairs: set[tuple[str, str]] = set()
        comp_pin_map = phase_1["component_nets"].get(ref, {}).get("pin_number_map", {})
        for pin_number, net_name in sorted(phase_1["component_nets"].get(ref, {}).get("pins", {}).items()):
            if not include_full and str(net_name).startswith("unconnected-"):
                continue
            is_dat = phase_1["component_nets"].get(ref, {}).get("dat_source", False)
            pin_name = self._pin_name(component, pin_number, dat_source=is_dat)
            pair = (str(net_name), pin_name)
            if pair in seen_net_pairs:
                continue
            seen_net_pairs.add(pair)
            entry: dict[str, str] = {
                "name": pair[0],
                "pin": pair[1],
            }
            # Add physical pin number from pstchip.dat
            phys_pin = comp_pin_map.get(pin_name)
            if phys_pin:
                entry["pin_number"] = phys_pin
            # Annotate GPIO ball-name pins with their signal function
            if (
                is_dat
                and pin_name.startswith("GPIO")
                and not re.match(r"^N\d+$", pair[0])
            ):
                entry["pin_function"] = pair[0]
            nets.append(entry)

        # Merge multi-pad same-net pins in compact mode (e.g. VBUS×4)
        if not include_full:
            nets = self._merge_multipad_pins(nets)

        # Merge same-net entries into one (e.g. GND pins "2,3,6,7")
        nets = self._merge_same_net_pins(nets)
        mpn = self._component_mpn(component)

        payload = {
            "query_type": "component",
            "ref": component.reference,
            "value": component.value,
            "mpn": mpn,
            "page_index": page_index,
            "page_name": self._sheet_name_from_path(sheet_path),
            "properties": self._dedup_properties(component, mpn),
            "nets": nets,
            "neighbors": self._build_neighbors_payload(
                ref,
                phase_1["component_nets"],
                sheet_path,
            ),
        }
        return payload

    def query_component_match(self, text: str, *, include_all: bool = False) -> dict[str, Any]:
        """Search components by text (supports regex)."""
        matches = []
        # Try regex first, fallback to substring if regex is invalid
        try:
            pattern = re.compile(text, re.IGNORECASE)
            use_regex = True
        except re.error:
            wanted = text.lower()
            use_regex = False

        for component in self.project_index.components.values():
            haystack = " ".join(
                [
                    component.reference,
                    component.value,
                    component.properties.get("MPN", ""),
                    component.lib_id,
                ]
            )
            if use_regex:
                if not pattern.search(haystack):
                    continue
            else:
                if wanted not in haystack.lower():
                    continue
            mpn = self._component_mpn(component)
            match_entry = {
                "ref": component.reference,
                "value": component.value,
            }
            if mpn:
                match_entry["mpn"] = mpn
            matches.append(match_entry)
        shown, truncated = self._truncate_items(matches, include_all=include_all)
        return {
            "query_type": "component",
            "search": text,
            "matches": shown,
            "truncated": truncated,
            "shown": len(shown),
            "total": len(matches),
        }

    def query_net(self, net_name: str) -> dict[str, Any]:
        """Return one exact-net inspection payload."""
        graph = ConnectivityBuilder().build(self.project_index, self.schematic_path)
        if net_name not in graph.all_nets:
            # Try case-insensitive match
            net_lower = net_name.lower()
            for existing in graph.all_nets:
                if existing.lower() == net_lower:
                    net_name = existing
                    break
            else:
                raise LookupError(f"Net '{net_name}' not found")
        net = graph.all_nets[net_name]
        pin_entries = net.connected_pins
        pages = []
        pins = []
        component_sheet_paths: set[str] = set()
        for ref, pin_number, _pin_type in pin_entries:
            component = self.project_index.components.get(ref)
            if component is None:
                continue

            # Use page info from component_nets (from pstxprt.dat) if available
            comp_nets = graph.component_nets.get(ref, {})
            sheet_path = comp_nets.get("sheet_path", component.sheet_path)

            page_name = self._sheet_name_from_path(sheet_path)
            component_sheet_paths.add(sheet_path)
            if page_name not in pages:
                pages.append(page_name)
            is_dat = comp_nets.get("dat_source", False)
            pin_nm = self._pin_name(component, pin_number, dat_source=is_dat)
            pin_entry: dict[str, str] = {
                "ref": ref,
                "pin": pin_nm,
                "page": page_name,
            }
            # Add physical pin number from pstchip.dat
            comp_pin_map = comp_nets.get("pin_number_map", {})
            phys_pin = comp_pin_map.get(pin_nm)
            if phys_pin:
                pin_entry["pin_number"] = phys_pin
            if (
                is_dat
                and pin_nm.startswith("GPIO")
                and not re.match(r"^N\d+$", net_name)
            ):
                pin_entry["pin_function"] = net_name
            pins.append(pin_entry)
        label_buckets = self._collect_net_labels(net_name, component_sheet_paths)
        return {
            "query_type": "net",
            "name": net_name,
            "hierarchical_labels": label_buckets["hierarchical"],
            "global_labels": label_buckets["global"],
            "local_labels": label_buckets["local"],
            "pages": pages,
            "pins": pins,
        }

    def _collect_net_labels(self, net_name: str, component_sheet_paths: set[str]) -> dict[str, list[str]]:
        """Collect exact page labels reachable for one root net through sheet-pin aliasing."""
        buckets: dict[str, set[str]] = {
            "hierarchical": set(),
            "global": set(),
            "local": set(),
        }
        terminal = net_name.rsplit("/", 1)[-1]
        alias_names_by_page: dict[str, set[str]] = {}
        pending_pages: list[str] = []

        def add_alias(page_path: str, alias_name: str) -> None:
            if not page_path or not alias_name:
                return
            aliases = alias_names_by_page.setdefault(page_path, set())
            if alias_name in aliases:
                return
            aliases.add(alias_name)
            pending_pages.append(page_path)

        leaf_sheet_path = self._net_sheet_path(net_name)
        for page_path in component_sheet_paths:
            add_alias(page_path, terminal)
        if leaf_sheet_path:
            for page_path in self._ancestor_sheet_paths(leaf_sheet_path):
                add_alias(page_path, terminal)

        processed_aliases_by_page: dict[str, set[str]] = {}
        while pending_pages:
            page_path = pending_pages.pop()
            parser = self._local_parser_for_sheet_path(page_path)
            if parser is None:
                continue
            page_aliases = alias_names_by_page.get(page_path, set())
            processed_aliases = processed_aliases_by_page.setdefault(page_path, set())
            new_aliases = page_aliases - processed_aliases
            if not new_aliases:
                continue
            processed_aliases.update(new_aliases)

            for entity in parser.find_connected_entities(new_aliases):
                kind = entity.get("kind", "")
                name = entity.get("name", "")
                if kind in buckets and name:
                    buckets[kind].add(name)
                    add_alias(page_path, name)
                    continue
                if kind != "sheet_pin" or not name:
                    continue
                child_path = self._resolve_child_sheet_path(page_path, entity.get("sheet_name", ""))
                if child_path is None:
                    continue
                for child_entity in self._matching_page_label_entities(child_path, name):
                    child_kind = child_entity.get("kind", "")
                    child_name = child_entity.get("name", "")
                    if child_kind in buckets and child_name:
                        buckets[child_kind].add(child_name)
                        add_alias(child_path, child_name)

        return {bucket: sorted(values) for bucket, values in buckets.items()}

    def _net_sheet_path(self, net_name: str) -> Optional[str]:
        """Return the leaf sheet path implied by a hierarchical root net name."""
        if not net_name.startswith("/") or "/" not in net_name[1:]:
            return None
        return net_name.rsplit("/", 1)[0]

    def _ancestor_sheet_paths(self, sheet_path: str) -> list[str]:
        """Return one sheet path and its ancestors up to root."""
        paths: list[str] = []
        current = sheet_path
        while current:
            paths.append(current)
            if current == "/":
                break
            current = current.rsplit("/", 1)[0] or "/"
        return paths

    def _local_parser_for_sheet_path(self, sheet_path: str):
        """Return a single-page parser for one sheet path."""
        sheet_file_path = self._sheet_file_path(sheet_path)
        if sheet_file_path is None:
            return None
        parser = self._local_parsers.get(sheet_file_path)
        if parser is None:
            from tools.parser_factory import get_schematic_parser

            parser = get_schematic_parser(str(sheet_file_path), include_child_sheets=False)
            self._local_parsers[sheet_file_path] = parser
        return parser

    def _sheet_file_path(self, sheet_path: str) -> Optional[Path]:
        """Resolve one sheet path to its local schematic file."""
        if sheet_path == "/":
            return self.scope.root_schematic.resolve()
        for sheet in self.project_index.hierarchy:
            if sheet.sheet_path == sheet_path:
                return (self.scope.root_schematic.parent / sheet.sheet_file).resolve()
        return None

    def _resolve_child_sheet_path(self, parent_path: str, sheet_name: str) -> Optional[str]:
        """Resolve a child sheet name from one parent path to a unique sheet path."""
        if not sheet_name:
            return None
        wanted = f"/{sheet_name}" if parent_path == "/" else f"{parent_path}/{sheet_name}"
        for sheet in self.project_index.hierarchy:
            if sheet.sheet_path == wanted:
                return wanted
        return None

    def _matching_page_label_entities(self, sheet_path: str, label_name: str) -> list[dict[str, Any]]:
        """Return exact-matching labels on one page by name."""
        parser = self._local_parser_for_sheet_path(sheet_path)
        if parser is None:
            return []
        return [
            entity
            for entity in parser.get_page_connectivity_entities()
            if entity.get("kind") in {"local", "global", "hierarchical"} and entity.get("name") == label_name
        ]

    def query_net_match(self, text: str, *, include_all: bool = False) -> dict[str, Any]:
        """Search nets by text (supports regex)."""
        matches = []

        # Try regex first, fallback to substring if regex is invalid
        try:
            pattern = re.compile(text, re.IGNORECASE)
            use_regex = True
        except re.error:
            wanted = text.lower()
            use_regex = False

        for candidate in self._searchable_net_match_candidates():
            net_name = candidate["name"]
            if use_regex:
                if not pattern.search(net_name):
                    continue
            else:
                if wanted not in net_name.lower():
                    continue
            match = {
                "name": net_name,
                "kind": candidate["kind"],
                "occurrence_count": candidate["occurrence_count"],
                "pages": candidate["pages"],
                "mapped_to_net": candidate["mapped_to_net"],
            }
            pin_count = candidate.get("pin_count")
            if pin_count is None:
                pins = candidate.get("pins")
                if isinstance(pins, list):
                    pin_count = len(pins)
            if pin_count is not None:
                match["pin_count"] = pin_count
            matches.append(match)
        shown, truncated = self._truncate_items(matches, include_all=include_all)
        return {
            "query_type": "net",
            "search": text,
            "matches": shown,
            "truncated": truncated,
            "shown": len(shown),
            "total": len(matches),
        }

    def _searchable_net_match_candidates(self) -> list[dict[str, Any]]:
        """Return searchable net-like names with exact metadata for matching output."""
        graph = ConnectivityBuilder().build(self.project_index, self.schematic_path)
        candidates: list[dict[str, Any]] = []

        for net_name, connection in graph.all_nets.items():
            pages = sorted(
                {
                    self._sheet_name_from_path(component.sheet_path)
                    for ref, _pin_number, _pin_type in connection.connected_pins
                    for component in [self.project_index.components.get(ref)]
                    if component is not None
                }
            )
            candidates.append(
                {
                    "name": net_name,
                    "kind": "net",
                    "occurrence_count": 1,
                    "pages": pages,
                    "mapped_to_net": True,
                    "pin_count": len(connection.connected_pins),
                }
            )

        net_names_in_graph: set[str] = set(graph.all_nets.keys())
        entity_buckets: dict[tuple[str, str], dict[str, Any]] = {}
        for schematic_file in self._get_analysis_schematic_paths():
            parser = self._get_local_parser(schematic_file)
            page_name = self._sheet_name_for_schematic_file(schematic_file)
            for entity in parser.get_page_connectivity_entities():
                kind = self._net_match_kind(entity.get("kind", ""))
                if kind is None:
                    continue
                entity_name = str(entity.get("name", "")).strip()
                if not entity_name:
                    continue
                # Skip label entities whose name already exists as a net —
                # the net entry already carries complete pin/page information.
                if entity_name in net_names_in_graph:
                    continue
                key = (entity_name, kind)
                bucket = entity_buckets.setdefault(
                    key,
                    {
                        "name": entity_name,
                        "kind": kind,
                        "occurrence_count": 0,
                        "pages": set(),
                        "mapped_to_net": entity_name in graph.all_nets,
                        "pin_count": len(graph.all_nets[entity_name].connected_pins) if entity_name in graph.all_nets else None,
                    },
                )
                bucket["occurrence_count"] += 1
                bucket["pages"].add(page_name)

        for bucket in entity_buckets.values():
            candidates.append(
                {
                    "name": bucket["name"],
                    "kind": bucket["kind"],
                    "occurrence_count": bucket["occurrence_count"],
                    "pages": sorted(bucket["pages"]),
                    "mapped_to_net": bucket["mapped_to_net"],
                    "pin_count": bucket["pin_count"],
                }
            )

        candidates.sort(
            key=lambda item: (
                -self._net_match_naming_value(item["name"]),
                -int(item["occurrence_count"]),
                self._net_match_kind_rank(item["kind"]),
                item["name"],
                ",".join(item["pages"]),
            )
        )
        return candidates

    def _net_match_kind(self, raw_kind: str) -> Optional[str]:
        return {
            "local": "local_label",
            "global": "global_label",
            "hierarchical": "hierarchical_label",
            "sheet_pin": "sheet_pin",
        }.get(raw_kind)

    def _net_match_kind_rank(self, kind: str) -> int:
        return {
            "hierarchical_label": 0,
            "sheet_pin": 1,
            "global_label": 2,
            "local_label": 3,
            "net": 4,
        }.get(kind, 99)

    def _net_match_naming_value(self, name: str) -> int:
        tokens = [token for token in re.split(r"[_:/\-.]+", name) if token]
        separator_count = len(re.findall(r"[_:/\-.]+", name))
        has_mixed_case_or_digits = int(any(char.isdigit() for char in name) or any(char.islower() for char in name))
        return (separator_count * 10) + (len(tokens) * 5) + has_mixed_case_or_digits

    def _sheet_name_for_schematic_file(self, schematic_file: Path) -> str:
        resolved = schematic_file.resolve()
        if resolved == self.scope.root_schematic.resolve():
            return self.scope.project_name
        for sheet in self.project_index.hierarchy:
            candidate = (self.scope.root_schematic.parent / sheet.sheet_file).resolve()
            if candidate == resolved:
                return sheet.sheet_name
        return resolved.stem

    def query_property(self, key: str, *, include_all: bool = False) -> dict[str, Any]:
        """Return one property aggregation payload."""
        grouped: dict[Any, list[str]] = {}
        for component in self.project_index.components.values():
            value = component.properties.get(key)
            grouped.setdefault(value, []).append(component.reference)
        values = [
            {"mpn" if key == "MPN" else "value": value, "refs": sorted(refs)}
            for value, refs in sorted(grouped.items(), key=lambda item: (item[0] is None, str(item[0])))
        ]
        shown_values, truncated = self._truncate_items(values, include_all=include_all)
        with_value = sum(len(refs) for value, refs in grouped.items() if value is not None)
        missing = sum(len(refs) for value, refs in grouped.items() if value is None)
        return {
            "query_type": "property",
            "key": key,
            "values": shown_values,
            "total": len(self.project_index.components),
            "with_value": with_value,
            "missing": missing,
            "truncated": truncated,
            "shown": len(shown_values),
            "total_values": len(values),
        }

    def query_pattern(self, pattern_sources: list[str] | tuple[str, ...]) -> dict[str, Any]:
        """Return pattern matches for explicit pattern sources only.

        The query contract is: use exactly the YAML file or directory the
        caller requested.
        """
        phase_1 = self._run_phase_1()
        components = self._serialize_components(phase_1["component_nets"])
        nets = phase_1["nets"]
        interpreter = self._build_overlay_interpreter(pattern_sources=pattern_sources)
        core_ref = None
        phase_0 = self._run_phase_0(phase_1)
        if phase_0["core_components"]:
            core_ref = phase_0["core_components"][0]["reference"]
        matches = interpreter.interpret_subsystems(components=components, nets=nets, core_ref=core_ref)
        return {
            "query_type": "pattern",
            "pattern_file": str(pattern_sources[0]),
            "matches": [
                {
                    "role": match.category,
                    "ref": match.controller.get("ref") if match.controller else None,
                    "confidence": match.confidence,
                    "name": match.name,
                }
                for match in matches
            ],
        }

    def _component_summary(self, component) -> dict[str, Any]:
        entry = {
            "ref": component.reference,
            "value": component.value,
        }
        mpn = self._component_mpn(component)
        if mpn:
            entry["mpn"] = mpn
        return entry

    def _component_mpn(self, component) -> str | None:
        properties = getattr(component, "properties", {}) or {}
        value = getattr(component, "value", "") or ""
        for key in ("MPN", "LCSC Part", "Manufacturer Part Number", "Part Number"):
            candidate = properties.get(key)
            if candidate:
                return str(candidate)
        if value:
            return str(value)
        return None

    def _dedup_properties(self, component, top_mpn: str | None) -> dict[str, Any]:
        """Remove redundant MPN fields from properties that duplicate top-level mpn or value."""
        props = dict(getattr(component, "properties", {}) or {})
        if not top_mpn:
            return props
        # Remove MPN/Manufacturer Part Number from properties if it matches top-level mpn
        for key in ("MPN", "Manufacturer Part Number"):
            if key in props and str(props[key]) == top_mpn:
                del props[key]
        return props

    def _truncate_items(self, items: list[dict[str, Any]], *, include_all: bool) -> tuple[list[dict[str, Any]], bool]:
        if include_all or len(items) <= self.DEFAULT_QUERY_LIMIT:
            return items, False
        return items[: self.DEFAULT_QUERY_LIMIT], True

    def _build_overlay_interpreter(
        self,
        *,
        pattern_sources: tuple[str, ...] | list[str],
    ) -> OverlayInterpreter:
        """Build an interpreter that only uses explicit pattern sources."""
        return OverlayInterpreter(
            project_path=None,
            rule_paths=self.rule_paths,
            pattern_sources=pattern_sources,
        )

    def _page_nets(self, sheet_path: str, component_nets: dict[str, Any]) -> list[dict[str, Any]]:
        counts: Counter[str] = Counter()
        for reference, entry in component_nets.items():
            component = self.project_index.components.get(reference)
            if component is None or component.sheet_path != sheet_path:
                continue
            for net_name in entry.get("pins", {}).values():
                counts[str(net_name)] += 1
        return [
            {"name": name, "pin_count": counts[name]}
            for name in sorted(counts)
        ]

    def _neighbor_count(self, reference: str, component_nets: dict[str, Any]) -> int:
        pins = component_nets.get(reference, {}).get("pins", {})
        if not pins:
            return 0
        target_nets = {str(net_name) for net_name in pins.values() if str(net_name)}
        neighbors = set()
        for other_ref, entry in component_nets.items():
            if other_ref == reference:
                continue
            other_nets = {str(net_name) for net_name in entry.get("pins", {}).values() if str(net_name)}
            if target_nets.intersection(other_nets):
                neighbors.add(other_ref)
        return len(neighbors)

    def _build_neighbors_payload(
        self,
        reference: str,
        component_nets: dict[str, Any],
        component_sheet_path: str,
    ) -> dict[str, Any]:
        pins = component_nets.get(reference, {}).get("pins", {})
        if not pins:
            return {
                "shared_nets": [],
            }

        target_nets = sorted({str(net_name) for net_name in pins.values() if str(net_name)})
        shared_nets: list[dict[str, Any]] = []

        for net_name in target_nets:
            connected_refs = sorted(
                {
                    other_ref
                    for other_ref, entry in component_nets.items()
                    if net_name in {str(value) for value in entry.get("pins", {}).values() if str(value)}
                    and other_ref in self.project_index.components
                }
            )
            peer_refs = [other_ref for other_ref in connected_refs if other_ref != reference]
            pages = {
                self.project_index.components[other_ref].sheet_path
                for other_ref in connected_refs
            }
            local_connected_refs = [
                other_ref
                for other_ref in peer_refs
                if self.project_index.components[other_ref].sheet_path == component_sheet_path
            ]
            entry: dict[str, Any] = {
                "net": net_name,
                "fanout": len(connected_refs),
                "cross_page": len(pages) > 1,
                "local_refs": local_connected_refs[: self.DEFAULT_QUERY_LIMIT],
            }
            if len(peer_refs) > self.DEFAULT_QUERY_LIMIT:
                entry["connected_refs_sample"] = peer_refs[: self.DEFAULT_QUERY_LIMIT]
                entry["truncated"] = True
            else:
                entry["connected_refs"] = peer_refs
            shared_nets.append(entry)

        shared_nets.sort(key=lambda item: (item["fanout"], item["net"]))

        return {
            "shared_nets": shared_nets,
        }

    def _sheet_name_from_path(self, sheet_path: str) -> str:
        # First try to find in hierarchy (for KiCad multi-page)
        for sheet in self.project_index.hierarchy:
            if sheet.sheet_path == sheet_path:
                return sheet.sheet_name

        # For Cadence with pstxprt.dat, sheet_path may be like "page9", "page30"
        # In this case, return the page name directly
        if sheet_path.startswith("page") and sheet_path != "/":
            return sheet_path

        # Fallback to project name (root schematic)
        return self.scope.project_name

    @staticmethod
    def _merge_multipad_pins(nets: list[dict[str, str]]) -> list[dict[str, str]]:
        """Merge multi-pad pins sharing the same net (e.g. VBUS#a4..#b9 → VBUS ×4)."""
        from collections import OrderedDict

        grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
        for entry in nets:
            grouped.setdefault(entry["name"], []).append(entry)

        merged: list[dict[str, str]] = []
        for net_name, entries in grouped.items():
            if len(entries) <= 1:
                merged.extend(entries)
                continue
            # Check if all pins differ only by pad suffix (#xx)
            base_names = set()
            for e in entries:
                base = re.sub(r"#\w+$", "", e["pin"])
                base_names.add(base)
            if len(base_names) == 1:
                base = base_names.pop()
                result = {"name": net_name, "pin": f"{base} ×{len(entries)}"}
                # Preserve pin_number if all entries share the same one
                pin_nums = {e.get("pin_number") for e in entries if "pin_number" in e}
                if len(pin_nums) == 1:
                    result["pin_number"] = pin_nums.pop()
                merged.append(result)
            else:
                merged.extend(entries)
        return merged

    @staticmethod
    def _merge_same_net_pins(nets: list[dict[str, str]]) -> list[dict[str, str]]:
        """Merge entries sharing the same net name into one with comma-separated pins."""
        if not nets:
            return nets
        merged: list[dict[str, str]] = []
        groups: dict[str, list[dict[str, str]]] = {}
        order: list[str] = []
        for entry in nets:
            name = entry["name"]
            if name not in groups:
                groups[name] = []
                order.append(name)
            groups[name].append(entry)
        for name in order:
            entries = groups[name]
            if len(entries) == 1:
                merged.append(entries[0])
            else:
                pins = ",".join(e["pin"] for e in entries)
                result: dict[str, str] = {"name": name, "pin": pins}
                # Preserve pin_number as comma-separated if present
                pin_nums = [e["pin_number"] for e in entries if "pin_number" in e]
                if pin_nums:
                    result["pin_number"] = ",".join(pin_nums)
                merged.append(result)
        return merged

    def _pin_name(self, component, pin_number: str, dat_source: bool = False) -> str:
        if dat_source:
            # DAT source (pstxnet.dat): pin_number is a physical pin identifier
            # that corresponds to the XML parser's pin "name" attribute,
            # NOT the "number" attribute (which is a 0-based position index).
            # For CDS_PINID names (e.g. "GPIO0"), they are already functional —
            # no remap needed. For numeric pin ids, try remap via pin "name".
            name = str(pin_number)
            for pin in component.pins:
                pin_name = str(pin.get("name", ""))
                if pin_name == name:
                    # Found exact match — return the pin name as-is
                    # (it's already the meaningful identifier)
                    return pin_name
            return name
        for pin in component.pins:
            if str(pin.get("number", "")) == str(pin_number):
                return str(pin.get("name", "") or pin_number)
        return str(pin_number)

    @staticmethod
    def _extract_page_index(sheet_path: str) -> int:
        """Extract page index from various sheet_path formats.

        Supports:
        - "pageN" (pstxprt.dat P_PATH)
        - "page_N" / "PAGE.N" (alternative naming)
        - "/N" (simple numeric path)
        - "/Page_Name" (named path — returns 1)
        """
        import re as _re
        if not sheet_path or sheet_path == "/":
            return 1

        # "pageN" or "PageN"
        m = _re.search(r'[Pp][Aa][Gg][Ee][_\.]?(\d+)', sheet_path)
        if m:
            return int(m.group(1))

        # Pure numeric path like "/3"
        m = _re.search(r'^/(\d+)$', sheet_path)
        if m:
            return int(m.group(1))

        return 1

    def _suggest_closest_ref(self, ref: str) -> str | None:
        """Find closest component reference by prefix match."""
        prefix = re.match(r"^[A-Z]+", ref)
        if not prefix:
            return None
        pfx = prefix.group()
        candidates = [r for r in self.project_index.components if r.startswith(pfx)]
        if not candidates:
            return None
        # Sort by numeric suffix distance
        ref_num = re.search(r"\d+", ref)
        if ref_num:
            target = int(ref_num.group())
            candidates.sort(key=lambda r: abs(int(m.group()) - target) if (m := re.search(r"\d+", r)) else 999)
        return candidates[0] if candidates else None

    def _serialize_components(self, component_nets: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Serialize parsed components into analysis/export dictionaries."""
        comp_dicts: list[dict[str, Any]] = []
        for component in self.project_index.components.values():
            connected_nets = []
            if component_nets and component.instance_id in component_nets:
                connected_nets = sorted(
                    {
                        str(net_name).strip()
                        for net_name in component_nets[component.instance_id].get("pins", {}).values()
                        if str(net_name).strip()
                    }
                    | {
                        str(net_name).strip()
                        for net_name in component_nets[component.instance_id].get("aliases", [])
                        if str(net_name).strip()
                    }
                )

            comp_dict = {
                "instance_id": component.instance_id,
                "reference": component.reference,
                "value": component.value,
                "lib_id": component.lib_id,
                "footprint": component.footprint,
                "pins": list(component.pins),
                "nets": connected_nets,
                "flags": dict(component.flags),
                "source_schematic": component.source_schematic.name,
                "sheet_instance_path": component.sheet_instance_path,
                "sheet_type": component.sheet_type,
                "properties": dict(component.properties),
            }
            comp_dicts.append(comp_dict)

        return comp_dicts

    def _run_phase_1(self) -> dict[str, Any]:
        """Phase 1: Netlist semantic parsing.

        Uses kicad-cli to export netlist and parse for accurate pin-level connectivity.
        """
        graph = ConnectivityBuilder().build(self.project_index, self.schematic_path)

        net_dicts = []
        for net_name in sorted(graph.all_nets):
            net = graph.all_nets[net_name]
            net_dicts.append(
                {
                    "name": net.net_name,
                    "code": net.net_code,
                    "type": net.net_type,
                    "connected_pins": [(ref, pin) for ref, pin, _pin_type in net.connected_pins],
                    "component_count": len(net.connected_refs),
                }
            )

        comp_nets = dict(graph.component_nets)

        sheets = [
            {
                "name": sheet.sheet_name,
                "file": sheet.sheet_file,
                "sheet_instance_path": sheet.sheet_path,
                "sheet_type": sheet.sheet_type,
                "component_count": sheet.component_count,
            }
            for sheet in self.project_index.hierarchy
        ]

        return {
            "nets": net_dicts,
            "hierarchy": sheets,
            "component_nets": comp_nets,
            "netlist_available": graph.netlist_available,
            "connectivity_warnings": list(graph.warnings),
        }

    def _export_netlist(self) -> Optional[Path]:
        """Export netlist using kicad-cli.

        Returns:
            Path to exported netlist or None if failed
        """
        import subprocess
        import tempfile

        try:
            # Create temp file for netlist
            fd, temp_path = tempfile.mkstemp(suffix=".xml")
            os.close(fd)

            # Run kicad-cli to export netlist
            result = subprocess.run(
                [
                    "kicad-cli", "sch", "export", "netlist",
                    "--format", "kicadxml",
                    "-o", temp_path,
                    str(self.schematic_path)
                ],
                capture_output=True,
                timeout=60,
            )

            if result.returncode == 0:
                return Path(temp_path)
            else:
                print(f"kicad-cli netlist export failed: {result.stderr}", file=sys.stderr)
                return None

        except FileNotFoundError:
            print("kicad-cli not found, skipping netlist export", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Netlist export error: {e}", file=sys.stderr)
            return None

    def _run_phase_2(
        self,
        phase_0: dict[str, Any],
        phase_1: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 2 is a structural passthrough in the light-refactor design."""
        del phase_1
        return {
            "components": list(phase_0.get("components", [])),
        }

    def _run_phase_3(
        self,
        phase_0: dict[str, Any],
        phase_1: dict[str, Any],
        phase_2: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Phase 3: Subsystem detection using patterns."""
        if not self.pattern_sources:
            return {
                "subsystems": [],
                "loaded_patterns": [],
                "matched_patterns": [],
            }

        components = (phase_2 or {}).get("components", phase_0.get("components", []))
        nets = phase_1.get("nets", [])
        core = phase_0.get("core_components", [])

        main_controller = core[0].get("reference", "") if core else None

        signal_subsystems = self.overlay_interpreter.interpret_subsystems(
            components=components,
            nets=nets,
            core_ref=main_controller,
        )
        loaded_patterns_getter = getattr(self.overlay_interpreter, "loaded_pattern_names", None)
        loaded_patterns = loaded_patterns_getter() if callable(loaded_patterns_getter) else []
        subsystems = self.synthesis_engine.synthesize(
            core_components=core,
            components=components,
            hierarchy=phase_1.get("hierarchy", []),
            interpreted_subsystems=signal_subsystems,
            main_controller=main_controller,
        )

        return {
            "subsystems": subsystems,
            "loaded_patterns": loaded_patterns,
            "matched_patterns": [pattern.pattern_name for pattern in signal_subsystems],
        }

    def _decorate_core_components(
        self,
        core_components: list[dict[str, Any]],
        components: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Return structural core candidates without attaching inferred roles."""
        del components
        return [dict(core) for core in core_components]

    def _combine_results(
        self,
        phase_0: dict[str, Any],
        phase_1: dict[str, Any],
        phase_2: dict[str, Any],
        phase_3: dict[str, Any],
        schematic_hash: str,
    ) -> AnalysisResult:
        """Combine phase results into final result."""
        components = phase_2.get("components", phase_0.get("components", []))
        core_components = self._decorate_core_components(phase_0.get("core_components", []), components)

        return AnalysisResult(
            meta={
                "project_name": self.scope.project_name,
                "project_id": self.project_path.name,
                "resolved_project_name": self.scope.project_name,
                "schematic_path": str(self.schematic_path),
                "analyzed_at": datetime.now().isoformat(),
                "schematic_hash": schematic_hash,
                "version": CacheManager.CACHE_VERSION,
                "netlist_available": phase_1.get("netlist_available", False),
                "context_signature": self.context_signature,
                "rule_paths": list(self.rule_paths),
                "pattern_sources": list(self.pattern_sources),
                "loaded_patterns": list(phase_3.get("loaded_patterns", [])),
                "matched_patterns": list(phase_3.get("matched_patterns", [])),
            },
            core_components=core_components,
            components=components,
            nets=phase_1.get("nets", []),
            subsystems=phase_3.get("subsystems", []),
            hierarchy=phase_1.get("hierarchy", []),
            statistics={
                "total_components": len(components),
                "total_nets": len(phase_1.get("nets", [])),
                "subsystem_count": len(phase_3.get("subsystems", [])),
                "core_component_count": len(core_components),
            },
            component_nets=phase_1.get("component_nets", {}),
        )

    def _apply_focus(self, result: AnalysisResult, focus: str) -> AnalysisResult:
        """Apply focus filter to result.

        Args:
            result: Full analysis result
            focus: Subsystem to focus on

        Returns:
            Filtered result focused on specified subsystem
        """
        focus_lower = focus.lower()

        # Filter subsystems by type or name
        focused_subsystems = []
        participant_refs = set()

        for sub in result.subsystems:
            sub_type = sub.get("type", "").lower()
            sub_name = sub.get("name", "").lower()
            sub_category = sub.get("category", "").lower()

            if focus_lower in sub_type or focus_lower in sub_name or focus_lower in sub_category:
                focused_subsystems.append(sub)
                # Collect participant refs
                for p in sub.get("participants", []):
                    ref = p.get("ref", "")
                    if ref:
                        participant_refs.add(ref)
                # Collect controller ref
                ctrl = sub.get("controller", {})
                if ctrl and ctrl.get("ref"):
                    participant_refs.add(ctrl.get("ref"))

        # Filter components to those in focused subsystems
        if participant_refs:
            result.components = [
                c for c in result.components
                if c.get("reference") in participant_refs
            ]
            result.core_components = [
                c for c in result.core_components
                if c.get("reference") in participant_refs
            ]
            result.component_nets = {
                key: value
                for key, value in result.component_nets.items()
                if value.get("reference", "").upper() in participant_refs
            }
        else:
            result.components = []
            result.core_components = []
            result.component_nets = {}

        result.subsystems = focused_subsystems
        result.statistics["total_components"] = len(result.components)
        result.statistics["subsystem_count"] = len(focused_subsystems)
        result.statistics["core_component_count"] = len(result.core_components)
        result.meta["focus_filter"] = {
            "query": focus,
            "matched_subsystems": len(focused_subsystems),
            "matched_components": len(result.components),
        }

        return result

    def generate_markdown_report(self, result: AnalysisResult) -> str:
        """Generate Markdown report from analysis result."""
        return self.synthesis_engine.generate_markdown_report(result)
