# Armbian Hardware Skill

- Owner: armbian-platform-maintainers (knowledge ownership metadata).
- Version: see version.json and the generated manifest.json.
- Status: development preview.
- Users: application/system engineers and beginners developing on Armbian.
- Scope: capability explanations, existing-project integration, deployment and diagnosis.
- Requirements: Python 3.9+ standard library for optional offline tools; project-native tools and authorized target access only when the task needs them. The offline helpers need no API key, MCP or control daemon; the chosen coding CLI requires its normal model access.
- Outputs: explanations, project code/configuration, deployment/recovery steps and scoped evidence; search/match/explain return JSON.
- Limits: reference matching is not hardware availability; unknown carrier/revision cannot inherit another board's pins; static tests cannot certify electrical effects or execution backends.
- Side effects: offline commands read local knowledge only; optional probe collects bounded target metadata; actual application changes follow user scope and project conventions.
- Provenance: release lock and package manifest trace files, source commit, dirty state and knowledge version. Digests detect changes relative to the manifest; they do not authenticate a publisher.
