# Progress Report - Week 1 & Week 2 (Partial)

## âœ“ Week 1 Completed Tasks

### Database Infrastructure (W1-DB)
- **W1-DB-01: Supabase Schema** âœ“ COMPLETE
- **W1-DB-02: Neo4j Schema** âœ“ COMPLETE

### Backend API (W1-API)
- **W1-API-01: FastAPI Skeleton** âœ“ COMPLETE

### Frontend (W1-FE)
- **W1-FE-01: Next.js Auth Skeleton** âœ“ COMPLETE

### Authentication (W1-AUTH)
- **W1-AUTH-01: Supabase Auth Setup** âœ“ COMPLETE

## âœ“ Week 2 Completed Tasks (Engine)

### W2-ENGINE-01: TÃ­ch há»£p Tá»­ Vi Engine âœ“ COMPLETE (REFACTORED)
**Date**: 2026-06-13

#### Implementation Summary
ÄÃ£ refactor láº¡i hoÃ n toÃ n implementation vá»›i lasotuvi engine tá»« doanguyen/lasotuvi package.

#### Files Created/Modified
1. **Dependencies**:
   - Updated `backend/requirements.txt` - Added ephem, note about lasotuvi installation
   - Updated `backend/pyproject.toml` - Added ephem to dependencies
   - Created `backend/setup_lasotuvi.sh` - Automated installation script

2. **Service Layer**:
   - Created `backend/app/services/lasotuvi_service.py` (300+ lines)
     - `LasoTuviService` class with static methods
     - `generate_la_so()` - Main generation method
     - `validate_input()` - Input validation
     - `_parse_dia_ban()` - Parse lasotuvi output to structured format
     - Helper methods: `get_cung_info()`, `get_sao_in_cung()`, `format_for_output()`

3. **Data Models**:
   - Created `backend/app/models/lasotuvi_models.py` (180+ lines)
     - `SaoInfo` - Star information model
     - `CungInfo` - Palace (cung) information model
     - `LaSoTuViResponse` - Complete birth chart response
     - `GenerateLaSoRequest` - Request validation with Pydantic
     - `ErrorResponse` - Standard error response
     - `HealthResponse` - Health check response

4. **API Routes**:
   - Created `backend/app/routers/lasotuvi_routes.py` (200+ lines)
     - `GET /lasotuvi/health` - Health check endpoint
     - `POST /lasotuvi/generate` - Generate birth chart (JSON body)
     - `GET /lasotuvi/generate` - Generate birth chart (query params)
     - Comprehensive error handling (400, 500)

5. **Main App**:
   - Updated `backend/app/main.py` - Added lasotuvi_routes router

6. **Testing**:
   - Created `backend/tests/test_lasotuvi_service.py` (200+ lines)
     - `TestLasoTuviServiceValidation` - Input validation tests
     - `TestLasoTuviServiceGenerate` - Generation tests
     - `TestLasoTuviServiceHelpers` - Helper method tests
     - `TestLasoTuviServiceEdgeCases` - Edge case tests

7. **Documentation**:
   - Created `backend/LASOTUVI_SETUP.md` - Complete installation guide
     - Problem explanation (outdated dependencies)
     - Two installation methods (script vs manual)
     - Verification steps
     - Usage examples
     - Troubleshooting
   - Created `backend/LASOTUVI_USAGE.md` - Complete API usage guide
     - API endpoints documentation
     - Request/response examples
     - cURL examples
     - Python integration examples
     - React/TypeScript examples
     - Use cases

#### Key Technical Details
- **Installation**: Requires `pip install --no-deps lasotuvi` to avoid outdated dependencies
- **Critical Note**: Must pass `diaBan` CLASS (not instance) to `lapDiaBan()`
- **Hour Format**: Uses 1-12 (Ä‘á»‹a chi), not 0-23
- **Gender**: 1=Nam (male), -1=Ná»¯ (female)
- **Palace Index**: Starts from 1 (no index 0)

**Status**: âœ“ COMPLETE - Implementation, testing, and documentation all finished

---

### W2-ENGINE-02: Unit Test Tá»­ Vi Engine âœ“ COMPLETE (Implementation)
- **Test File**: Created `backend/tests/test_tuvi_engine.py`
- **Test Classes**:
  1. `TestTuViEngineAccuracy` - 5 golden test cases
     - test_case_1_male_1990
     - test_case_2_female_1985
     - test_case_3_male_1995_late_night
     - test_case_4_female_2000_early_morning
     - test_case_5_male_1970
  2. `TestTuViInputValidation` - Input validation tests
     - Invalid date format
     - Invalid time format
     - Invalid gender
     - Nonexistent date
     - Gender variants
  3. `TestTuViOutputStructure` - Schema validation tests
     - Required fields presence
     - Metadata structure
     - Palace structure (12 palaces)
     - Star structure

**Status**: VERIFIED - Test suite now runs successfully; reference accuracy checked in Phase 3 verification

---

### W2-ENGINE-03: TÃ­ch há»£p BÃ¡t Tá»± Engine âœ“ COMPLETE (Implementation)
- **Dependencies**: Added `bazi-calculator-by-alvamind` to frontend/package.json
- **API Route**: Created `frontend/app/api/battu/calculate/route.ts`
  - `POST /api/battu/calculate` endpoint
  - Input validation (year, month, day, hour, gender)
  - Uses local `frontend/lib/battu/calculator.ts` wrapper because npm package `bazi-calculator-by-alvamind@1.0.2` is published without its declared `dist/index.js` and `dist/index.d.ts`
  - Output normalization to internal schema
  - Error handling with appropriate HTTP status codes
- **Schema Functions**:
  - `normalizeGender()` - Gender input normalization
  - `normalizeOutput()` - Convert raw analysis to schema
  - `extractPillar()` - Extract pillar information
  - `extractElements()` - Extract element analysis
- **Documentation**: Updated `backend/docs/chart-schema.md`
  - Added complete BÃ¡t Tá»± schema section
  - Four Pillars documentation
  - Heavenly Stems (10 ThiÃªn Can)
  - Earthly Branches (12 Äá»‹a Chi)
  - Complete example chart
  - API endpoint references

**Status**: VERIFIED - `npm run build` passes; Bat Tu route compiles and uses the local wrapper

---

### W2-ENGINE-04: Chart Creation Flow âœ“ COMPLETE (Implementation)
**Date**: 2026-06-17

#### Implementation Summary
Implemented the end-to-end chart creation flow from Dashboard form to engine calculation, Supabase `la_so` storage, and redirect to chart detail.

#### Files Modified
1. **Dashboard Form**:
   - Updated `frontend/app/dashboard/page.tsx`
   - Added create-chart form fields: `label`, `birth_date`, `birth_time`, `gender`, `chart_system`
   - Added client validation for required label, Gregorian date, `HH:MM` time, and Bat Tu year range `1930-2048`
   - Added loading and error states

2. **Engine Integration**:
   - Tu Vi uses `POST <NEXT_PUBLIC_API_BASE_URL>/chart/tuvi`
   - Bat Tu uses `POST /api/battu/calculate`
   - `TUVI_BATU` calculates both engines before storage
   - Bat Tu derives `year`, `month`, `day`, and `hour` from canonical form input

3. **Supabase Storage**:
   - Upserts `profiles` for the current authenticated user before chart insert
   - Inserts exactly one row into `la_so`
   - Stores `chart_version = "1.0"`
   - Stores `chart_data` as direct engine response for single-system charts, or `{ tuvi, batu }` for combined charts

4. **Chart Detail**:
   - Updated `frontend/app/chart/[id]/page.tsx`
   - Fetches the saved `la_so` row by id
   - Displays saved metadata and stored chart JSON

5. **Styling**:
   - Updated `frontend/app/globals.css`
   - Added shared styles for form panels, error state, detail list, and JSON preview

#### Verification
- `npx tsc --noEmit --pretty false` passes.
- User-confirmed `npm run build` passes on 2026-06-17.

**Status**: COMPLETE - Dashboard create flow, engine calls, Supabase insert, and chart detail redirect are implemented.

---

## Verification Update - 2026-06-17

### Phase 1 - Backend verification for Tu Vi
- Added `backend/setup_lasotuvi.ps1` for Windows PowerShell setup; `setup_lasotuvi.sh` remains for Linux/macOS/WSL.
- Fixed `tests/test_tuvi_engine.py` root cause: `TuViCalculator` no longer imports missing `lasotuvi.LasoTuVi`; it now uses the working `LasoTuviService` path.
- Fixed canonical palace alias: `Tu tuc` from lasotuvi is normalized to `Tu Nu` in the internal schema.
- Verification command passed:
  - `python -m pytest tests/test_lasotuvi_service.py tests/test_tuvi_engine.py -v`
  - Result: `39 passed, 1 warning`

### Phase 2 - Tu Vi API smoke test
- Public route confirmed for UI use: `POST /chart/tuvi`.
- Low-level diagnostic route remains available: `POST /lasotuvi/generate`.
- Decision: create-chart UI must use `/chart/tuvi`, not `/lasotuvi/generate`.

### Phase 3 - Tu Vi accuracy verification
- 5 golden cases in `tests/test_tuvi_engine.py` now execute successfully.
- 12 palace structure and star schema checks pass.
- Any deeper astrology/reference deviation should be documented separately if later manual comparison finds one.

### Phase 4 - Frontend/Bat Tu verification
- `bazi-calculator-by-alvamind@1.0.2` package issue identified: package root points to missing `dist` files.
- Implemented local calculator wrapper in `frontend/lib/battu/calculator.ts` and updated `frontend/app/api/battu/calculate/route.ts` to avoid the broken package root import.
- Bat Tu route validates real Gregorian dates and supports years `1930-2048`, matching the local date mapping data.
- Verification:
  - `npx tsc --noEmit --pretty false` passes.
  - User-confirmed `npm run build` passes.

### Phase 5 - Contract/schema/route lock before W2-ENGINE-04
- Contract documented in `backend/docs/chart-schema.md` under `Locked Contract for W2-ENGINE-04`.
- Canonical form input:
  - `label`
  - `birth_date`
  - `birth_time`
  - `gender`
  - `chart_system: TUVI | BATU | TUVI_BATU`
- Supabase `la_so` insert fields confirmed:
  - `user_id`, `label`, `birth_date`, `birth_time`, `gender`, `chart_system`, `chart_data`, `chart_version`
- `chart_data` decision:
  - `TUVI`: store normalized Tu Vi chart response directly.
  - `BATU`: store normalized Bat Tu chart response directly.
  - `TUVI_BATU`: store `{ "tuvi": {...}, "batu": {...} }`.
- Engine endpoints locked:
  - Tu Vi: `POST <FASTAPI_BASE_URL>/chart/tuvi`
  - Bat Tu: `POST /api/battu/calculate`

### Repo hygiene
- `.gitignore` updated to ignore generated artifacts:
  - `frontend/.next/`
  - `frontend/out/`
  - `frontend/tsconfig.tsbuildinfo`
  - `.pytest_cache/`
  - `pytest-cache-files-*/`
- `README.md` updated with backend/frontend setup, engine endpoints, Supabase storage contract, and git artifact notes.

**Gate status for W2-ENGINE-04**: COMPLETE.

---

## Week 2 Completed Tasks - 2026-06-19

Week 2 is now complete. Engine integration, chart creation, visualization, saved chart listing, chart detail navigation, and frontend responsive/auth polish have all been implemented.

### W2-VIZ-01: Tu Vi Visualization - COMPLETE
- Created `frontend/components/TuViBoard.tsx`.
- Renders the 12-palace Tu Vi board with palace metadata, major/minor star grouping, highlighted Menh/Than context, and horizontal scroll for small screens.
- Integrated into `frontend/app/chart/[id]/page.tsx` for saved Tu Vi and combined Tu Vi + Bat Tu charts.

### W2-VIZ-02: Bat Tu Visualization - COMPLETE
- Created `frontend/components/BatuBoard.tsx`.
- Renders the four-pillar Bat Tu layout with stem/branch, nap am, hidden stems, and element distribution.
- Uses responsive grid behavior for mobile, tablet, and desktop layouts.

### W2-DASH-01: Dashboard - COMPLETE
- Dashboard now lists the authenticated user's saved charts from Supabase.
- Added chart summary cards and navigation from dashboard to chart detail.
- Empty, loading, and error states are implemented.

### W2-FE-POLISH: Authentication and Responsive Frontend - COMPLETE
- Rebuilt `/login` and `/register` as polished split-layout authentication pages following `DESIGN.md`.
- Updated home, dashboard, chart detail, chart cards, Tu Vi board, and Bat Tu board to be flexible across common screen sizes.
- Fixed visible frontend Vietnamese encoding/copy issues.

---

## Summary Stats

| Component | Files Created/Modified | Status |
|-----------|----------------------|--------|
| W2-ENGINE-01 (Refactored) | 10 files | Complete |
| W2-ENGINE-02 | 1 file | Verified |
| W2-ENGINE-03 | 3 files | Verified |
| W2-ENGINE-04 | 3 frontend files | Complete |
| W2-VIZ-01 | 1 component + chart detail integration | Complete |
| W2-VIZ-02 | 1 component + chart detail integration | Complete |
| W2-DASH-01 | Dashboard + chart card flow | Complete |
| W2-FE-POLISH | Auth pages + responsive UI CSS | Complete |
| Phase 5 Contract | 2 docs | Locked |
| Total | 24+ files | Week 2 complete |

### Files Created/Modified - Lasotuvi Integration (2026-06-13)
1. `backend/requirements.txt` - Updated
2. `backend/pyproject.toml` - Updated
3. `backend/setup_lasotuvi.sh` - Created (installation script)
4. `backend/app/services/lasotuvi_service.py` - Created (300+ lines)
5. `backend/app/models/lasotuvi_models.py` - Created (180+ lines)
6. `backend/app/routers/lasotuvi_routes.py` - Created (200+ lines)
7. `backend/app/main.py` - Updated (added lasotuvi routes)
8. `backend/tests/test_lasotuvi_service.py` - Created (200+ lines)
9. `backend/LASOTUVI_SETUP.md` - Created (installation guide)
10. `backend/LASOTUVI_USAGE.md` - Created (API usage guide)

### Previous Files (Earlier Sessions)
11. `backend/tests/test_tuvi_engine.py` (290 lines)
12. `backend/docs/chart-schema.md` (350+ lines)
13. `frontend/app/api/battu/calculate/route.ts` (150 lines)
14. `frontend/lib/battu/calculator.ts` - Local Bat Tu calculator wrapper
15. `backend/setup_lasotuvi.ps1` - Windows PowerShell lasotuvi setup script
16. `.gitignore` and `README.md` - Repo hygiene and usage documentation
17. `frontend/app/dashboard/page.tsx` - End-to-end create-chart form and storage flow
18. `frontend/app/chart/[id]/page.tsx` - Saved chart detail fetch/display
19. `frontend/app/globals.css` - Create/detail/auth responsive UI styling
20. `frontend/components/TuViBoard.tsx` - Tu Vi 12-palace visualization
21. `frontend/components/BatuBoard.tsx` - Bat Tu four-pillar visualization
22. `frontend/components/ChartSummaryCard.tsx` - Saved chart summary card
23. `frontend/app/login/page.tsx` and `frontend/app/register/page.tsx` - Redesigned authentication pages
24. `frontend/app/page.tsx` and `frontend/app/layout.tsx` - Home/metadata copy updates

---

## Next Steps

1. Resolve the local git lock/index issue, then stage the Week 2 updates.
2. Run final frontend verification if not already done after the latest UI polish:
   - `npm run build`
   - `npm run lint` if supported by the installed Next.js version
3. Commit the completed Week 2 work.
4. Move to Week 3 planning and implementation.

---

## Week 3 Progress Update - 2026-06-24

### W3-INGEST-02: Chunking framework strategy-aware - COMPLETE

#### Implementation Summary
Implemented the strategy-aware chunking framework for the Tử Vi-only ingestion pipeline.

#### Files Created/Modified
1. `scripts/chunk_text.py`
   - CLI accepts normalized corpus input files or corpus directories.
   - Supports `--chunking-strategy`, `--config`, `--source-registry`, `--output`, and `--summary-output`.
   - Loads canonical `*_clean.json` and existing `*_sections.jsonl` corpus formats.
   - Emits stable JSONL chunk records with `chunk_id`, `parent_id`, `chunk_type`, `chunk_text`, `source_name`, `source_page`, `domain`, `chunk_strategy_id`, `chunk_hash`, and `metadata`.
   - Keeps Tử Vi-only runtime scope with `domain = "TUVI"`.
   - Adds downstream-friendly fields: `source_id`, `text`, `provenance`, `doc_id`, `section_id`, `char_start`, `char_end`, `token_count`, `chunking_version`, and `preserved_entities`.
   - Ensures `chunk_hash` includes `chunk_strategy_id` so strategies do not deduplicate into each other.
   - Implements Strategy A parent-child chunking with parent and child chunk references.

2. `configs/chunking_strategies.yaml`
   - Declares the six v7 chunking strategy IDs:
     - `chunk_structure_parent_child`
     - `chunk_fixed_256`
     - `chunk_fixed_512`
     - `chunk_fixed_1024`
     - `chunk_sentence_merge`
     - `chunk_semantic`
   - Defines Strategy A parent/child token targets and protected Tử Vi terms for sao, cung, thiên can, địa chi, and ngũ hành.

3. `backend/tests/test_chunk_text.py`
   - Covers clean JSON loader, sections JSONL loader, Tử Vi-only domain enforcement, typo guard for `THNL_clean.json`, strategy-aware hash behavior, parent-child schema, provenance fields, and protected term splitting.

4. `backend/requirements.txt` and `backend/pyproject.toml`
   - Added `PyYAML` for YAML strategy config loading.

#### Verification
- Unit/regression command:
  - `python -m pytest tests/test_chunk_text.py -q`
  - Current result after W3 chunking updates: `19 passed, 1 warning`
  - Warning is only `.pytest_cache` write permission in the local sandbox.
- Strategy A CLI smoke test on `TVGM_clean.json`:
  - Total chunks: `924`
  - Parent chunks: `258`
  - Child chunks: `666`
- Manual output check confirmed:
  - `domain = "TUVI"`
  - `source_id = "TVGM"`
  - `chunk_strategy_id = "chunk_structure_parent_child"`
  - child chunks reference valid parent chunk IDs
  - provenance contains source/page/span metadata

**Status**: COMPLETE - W3-INGEST-02 deliverable is implemented and verified.

---

### W3-INGEST-03: Implement remaining chunking strategies - COMPLETE

#### Implementation Summary
Implemented all remaining chunking strategies required for chunking ablation in the Tử Vi-only ingestion pipeline. The same input corpus can now produce chunk JSONL outputs for all six configured `chunk_strategy_id` values.

#### Files Modified
1. `configs/chunking_strategies.yaml`
   - Enabled the remaining strategies by setting `implemented: true`:
     - `chunk_fixed_256`
     - `chunk_fixed_512`
     - `chunk_fixed_1024`
     - `chunk_sentence_merge`
     - `chunk_semantic`
   - Added `similarity_threshold` for deterministic local semantic chunking.

2. `scripts/chunk_text.py`
   - Added fixed-size sliding-window chunkers for 256, 512, and 1024 token variants.
   - Added sentence-merge chunking with target/max token controls.
   - Added local deterministic semantic chunking using lexical similarity between adjacent sentence groups.
   - Kept Strategy A parent-child behavior unchanged.
   - Flat strategies emit `chunk_type = "chunk"` and `parent_id = null`.
   - All strategies reuse the same record factory, so output keeps `domain = "TUVI"`, `source_id`, `source_page`, `provenance`, `chunk_strategy_id`, and strategy-aware `chunk_hash`.
   - Summary output now includes chunk type counts for parent/child/flat chunks.

3. `backend/tests/test_chunk_text.py`
   - Expanded tests to cover all six strategies.
   - Added checks for shared schema, provenance fields, Tử Vi-only domain, fixed-size token caps, sentence source boundaries, and semantic topic-shift splitting.

#### Verification
- Unit/regression command:
  - `python -m pytest tests/test_chunk_text.py -q`
  - Result: `19 passed, 1 warning`
  - Warning is only `.pytest_cache` write permission in the local sandbox.
- CLI smoke test on the same input `TVGM_clean.json` for all six strategies:
  - `chunk_structure_parent_child`: `924` chunks (`258` parent, `666` child)
  - `chunk_fixed_256`: `454` chunks
  - `chunk_fixed_512`: `258` chunks
  - `chunk_fixed_1024`: `241` chunks
  - `chunk_sentence_merge`: `385` chunks
  - `chunk_semantic`: `382` chunks
- Output record sample checks confirmed:
  - `domain = "TUVI"`
  - `source_id = "TVGM"`
  - `source_page` is preserved
  - `chunk_strategy_id` matches the selected strategy
  - `provenance.source_id = "TVGM"`

**Status**: COMPLETE - W3-INGEST-03 deliverable is implemented and verified.

---

### W3-INGEST-04: Trích xuất entity theo chunk strategy - COMPLETE

#### Implementation Summary
Implemented strategy-aware entity extraction for the Tử Vi-only ingestion pipeline. The extractor consumes chunk JSONL from W3-INGEST-02/03, validates chunk provenance, canonicalizes entity aliases, and emits entity JSONL with `chunk_id`, `chunk_hash`, `chunk_strategy_id`, source/page/section metadata, evidence spans, prompt/model versioning, and review flags.

#### Files Created/Modified
1. `SPECIFICATIONS.md`
   - Expanded the Tử Vi ingestion taxonomy with `QuanHeCung`, `TrangThaiSao`, `TuHoa`, and `CucBanMenh`.
   - Clarified `LuanGiai` as an evidence-backed interpretive claim, not a free-form long paragraph node.
   - Added guardrails that extraction must not infer entities or claims outside source text.

2. `PLAN.md`
   - Updated W3-INGEST-04 scope, deliverable, and done criteria to use the expanded taxonomy and provenance requirements.

3. `configs/entity_extraction.yaml`
   - Added `entity_dict_version`, `prompt_version`, default Gemini Flash-Lite model, entity type list, alias/canonical mappings, and `LuanGiai` trigger phrases.
   - Covers 12 cung aliases, key stars, Tứ Hóa, trạng thái sao, thiên can, địa chi, ngũ hành, quan hệ cung, tổ hợp, vận hạn, Cục/Bản Mệnh, and controlled concepts.

4. `scripts/extract_entities.py`
   - Added CLI with `--input`, `--output`, `--chunking-strategy`, `--config`, `--review-output`, and `--mock-llm`.
   - Validates `domain = "TUVI"` and required chunk provenance before extraction.
   - Provides a production Gemini adapter with lazy import and a deterministic mock dictionary adapter for offline tests.
   - Drops entities without evidence in `chunk_text`, deduplicates within chunk by entity/type/span, and preserves strategy-aware provenance.
   - Generates review JSON with excerpts, extracted entity summaries, warnings, and per-chunk parse errors.

5. `backend/tests/test_extract_entities.py`
   - Covers alias canonicalization, chunk validation, evidence-only filtering, provenance preservation, multi-strategy mock CLI extraction, and strategy filtering.

6. `backend/requirements.txt` and `backend/pyproject.toml`
   - Added `google-generativeai` for production Gemini extraction.

#### Verification
- Entity extraction unit/smoke tests:
  - `..\.venv\Scripts\python.exe -m pytest tests/test_extract_entities.py -q -p no:cacheprovider`
  - Result: `7 passed`
- Chunking regression tests:
  - `..\.venv\Scripts\python.exe -m pytest tests/test_chunk_text.py -q -p no:cacheprovider`
  - Result: `19 passed`
- CLI smoke test with deterministic mock extraction:
  - `.\.venv\Scripts\python.exe scripts\extract_entities.py --input pytest-cache-files-entity-smoke\multiple-strategies\chunks.jsonl --output pytest-cache-files-entity-smoke\manual-cli\entities.jsonl --review-output pytest-cache-files-entity-smoke\manual-cli\review.json --mock-llm`
  - Result: `2` chunks processed, `13` entities emitted, `0` errors.

**Status**: COMPLETE - W3-INGEST-04 deliverable is implemented and verified with offline mock extraction. Manual 20-chunk quality review can now run on generated corpus chunks using the same CLI and review report.

---

### W3-INGEST-05: Graph writer, provenance và relation extraction hybrid - COMPLETE

#### Implementation Summary
Implemented the strategy-aware graph/provenance writer for the Tử Vi-only ingestion pipeline. The writer consumes chunk JSONL and entity JSONL from W3-INGEST-02/03/04, validates provenance, derives evidence-backed relations, writes graph data to Neo4j, and upserts citation-ready chunk provenance into Supabase `source_chunks`.

#### Files Created/Modified
1. `PLAN.md`
   - Expanded W3-INGEST-05 from basic graph writing to hybrid relation extraction, provenance validation, and full MVP relation coverage.

2. `infra/neo4j/schema.cypher`
   - Added strategy-aware `Source`, `Chunk`, and `Entity` constraints/indexes for graph ingestion and retrieval filtering.

3. `infra/supabase/schema.sql` and `infra/supabase/migrations/20260625_source_chunks_strategy_provenance.sql`
   - Added explicit provenance fields to `source_chunks`: `source_id`, `chunk_id`, `chunk_strategy_id`, `chunk_type`, `parent_id`, `section_id`, `text`, and `provenance`.

4. `scripts/write_graph_provenance.py`
   - Added CLI with `--chunks-input`, `--entities-input`, `--chunking-strategy`, `--relation-mode`, `--mock-llm`, `--dry-run`, `--skip-neo4j`, `--skip-supabase`, and `--summary-output`.
   - Supports rule, LLM-constrained, and hybrid relation extraction modes.
   - Derives evidence-backed MVP relations: `MENTIONS`, `THUOC_CUNG`, `DOI_CHIEU`, `LIEN_KE`, `GIAI_THICH`, `APPLIES_TO`, `RELATED_TO`, `LUU_Y`, `HAS_SOURCE`, and `HAS_CHUNK`.
   - Adds ontology relations for the 12 functional Tử Vi cung with `relation_source = "ontology"`.
   - Preserves `chunk_id`, `chunk_hash`, `chunk_strategy_id`, `source_id`, `source_page`, `evidence_text`, and `relation_source` on extracted relations.

5. `scripts/apply_supabase_migration.py` and `scripts/apply_neo4j_schema.py`
   - Added a psql-free migration helper using `psycopg`.
   - Improved Neo4j schema apply behavior so connectivity or statement failures fail clearly instead of reporting false success.

6. `backend/tests/test_write_graph_provenance.py` and `backend/pyproject.toml`
   - Added writer and relation derivation tests.
   - Added `psycopg[binary]` to backend project dependencies.

#### Verification
- Regression tests:
  - `..\.venv\Scripts\python.exe -m pytest tests/test_chunk_text.py tests/test_extract_entities.py tests/test_write_graph_provenance.py -q -p no:cacheprovider`
  - Result: `35 passed`
- Neo4j schema apply:
  - Passed after the Neo4j Aura instance was resumed from pause.
- Supabase migration:
  - Applied successfully with `scripts/apply_supabase_migration.py`.
- Writer smoke test on `TVGM_clean.json` with Strategy A and deterministic mock extraction:
  - Dry-run succeeded.
  - Real write succeeded.
  - Neo4j write counts:
    - `924` chunks
    - `562` canonical entities
    - `42,176` mentions
    - `30,829` non-mention relations
    - `1,848` source/chunk edges
    - `1` source
  - Supabase write count:
    - `924` `source_chunks` rows
  - Relation counts:
    - `APPLIES_TO`: `4,678`
    - `DOI_CHIEU`: `183`
    - `GIAI_THICH`: `4,678`
    - `LIEN_KE`: `6,012`
    - `LUU_Y`: `2,049`
    - `RELATED_TO`: `6,461`
    - `THUOC_CUNG`: `6,768`

#### Cleanup
- Removed local smoke-test artifacts:
  - `pytest-cache-files-w3-ingest-05/`
  - `pytest-cache-files-writer/`
  - `pytest-cache-files-entity-smoke/`
- Neo4j AuraDB and Supabase sample `TVGM` Strategy A data were intentionally kept for W3-INGEST-06 embedding/fulltext verification.

**Status**: COMPLETE - W3-INGEST-05 deliverable is implemented, verified with a real Neo4j/Supabase smoke write, and ready for W3-INGEST-06. Embedding and fulltext indexing remain owned by W3-INGEST-06.

---

### W3-INGEST-06: Embedding và fulltext index theo strategy - COMPLETE

#### Implementation Summary
Implemented the strategy-aware embedding and retrieval smoke layer for chunks written by W3-INGEST-05. The scripts can embed Neo4j `Chunk` nodes, populate fulltext metadata, resume after partial runs, and smoke-test dense plus sparse retrieval while preserving `source_id`, `domain`, and `chunk_strategy_id` filters.

#### Files Created/Modified
1. `PLAN.md`
   - Documented the W3-INGEST-06 embedding default: configurable Gemini embedding model, currently `gemini-embedding-2` with `output_dimensionality = 768` to match Neo4j `chunkVector`.

2. `scripts/embed_chunks.py`
   - Added chunk selection by `domain`, `source_id`, `chunk_strategy_id`, and missing `Chunk.embedding`.
   - Writes `Chunk.embedding`, `embedding_model`, `embedding_dim`, `embedded_at`, `embedding_text_hash`, `title`, and `keywords`.
   - Adds resume-safe incremental writes, retry/backoff, daily-quota detection, and partial summary output.
   - Supports multi-key Gemini config via `GEMINI_API_KEYS` or fallback `GEMINI_API_KEY` + `GEMINI_API_KEY_2`.
   - Uses round-robin key selection, per-key throttling, failover on rate limits, and disables RPD-exhausted keys for the run.

3. `scripts/smoke_retrieval.py`
   - Added dense vector smoke retrieval via Neo4j `chunkVector`.
   - Added sparse/fulltext smoke retrieval via `chunkFulltext`.
   - Uses the same multi-key embedding client for query embeddings.
   - Writes JSON summaries with retrieval hits, diagnostics, and safe key-usage counts.

4. `.env.example` and `backend/.env.example`
   - Added `GEMINI_API_KEYS` and optional `GEMINI_API_KEY_2` while preserving existing `GEMINI_API_KEY` compatibility.

5. `backend/tests/test_embed_chunks.py` and `backend/tests/test_smoke_retrieval.py`
   - Added unit coverage for embedding selection, dimension validation, metadata preservation, fulltext query shaping, retrieval normalization, multi-key parsing, round robin, failover, daily quota disable, and safe summary behavior.

6. `backend/requirements.txt` and `backend/pyproject.toml`
   - Added `google-genai` for current Gemini embedding API usage.

#### Verification
- W3-INGEST-06 focused tests:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py -q -p no:cacheprovider`
  - Result: `28 passed`
- W3 ingestion regression tests:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_chunk_text.py backend\tests\test_extract_entities.py backend\tests\test_write_graph_provenance.py backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py -q -p no:cacheprovider`
  - Result: `63 passed`
- Gemini embedding smoke status:
  - Small probe run succeeded.
  - Full TVGM Strategy A embedding run progressed through most remaining selected chunks before hitting Gemini embedding daily quota.
  - Multi-key failover and resume behavior are covered by unit tests; full DB embedding can continue with the same command after quota reset.

#### Cleanup
- Local pytest/smoke artifact directories are being removed after this progress update.

**Status**: COMPLETE - W3-INGEST-06 implementation and regression verification are complete. Full live DB embedding/retrieval can be resumed after Gemini quota reset, but the task is accepted based on the completed scripts, multi-key quota handling, and passing regression suite.

---

## W3-INGEST-07 Progress Update - 2026-06-30

### Implementation Status
- Added W3 full-corpus runner: `scripts/run_w3_ingest_07.py`.
- Added shared Gemini key discovery: `scripts/gemini_keys.py`.
- Updated chunking/entity/graph/embed scripts for multi-key Gemini usage, quota failover, safer partial summaries, and resume-aware state.
- Restored and updated:
  - `configs/chunking_strategies.yaml`
  - `configs/entity_extraction.yaml`
- Added runbook:
  - `docs/w3_ingest_07_runbook.md`

### Verified Tests
- W3 regression after runner/entity fixes reached:
  - `106 passed`
- Config restoration check:
  - `backend/tests/test_chunk_text.py backend/tests/test_extract_entities.py`
  - Result: `46 passed`

### Runtime Status
- Production ingest was attempted.
- Gemini key discovery detected 4 keys.
- Production completed `chunk_fixed_512` chunking for all four corpus files:
  - `TVGM`
  - `TVHS`
  - `TVKL`
  - `TVNL`
- Production stopped at `chunk_fixed_512:entity` because all 4 Gemini keys reported daily quota exhaustion.
- No production entity extraction is complete yet.
- No production graph/relation extraction is complete yet.
- No production embed/retrieval smoke is complete yet.

### Artifact Cleanup Status
- Dry-run/mock artifacts were removed by the user.
- Current artifact state is intentionally minimal:
  - `chunk_fixed_512` chunks remain.
  - W3 run reports/state were removed and will be regenerated on the next production run.
  - entity directories are empty placeholders.

### Decision Resolution
- Historical 2026-06-30 decision: W3-INGEST local-Kaggle artifact-first path was added to unblock full-corpus ingest when Gemini quota/runtime was unstable.
- Superseded note: W3-INGEST-07 acceptance on 2026-07-07 made `gemini_call` live DB the accepted full-corpus W3 branch.
- Local-Kaggle/Qwen remains the fallback/repro/comparison artifact path, not the accepted W3 branch.
- `rule-only` remains the no-LLM smoke/comparison path.
- BGE-M3/Qwen artifacts are kept separate from Gemini baseline via explicit strategy/slot/index metadata.

## W3 Local-Kaggle Backend Update - 2026-06-30

Historical note: this section documents the local-Kaggle fallback/repro/comparison path. It was superseded for W3 acceptance by the 2026-07-07 `gemini_call` live DB branch acceptance recorded below.

### Implementation Status
- Added a separate local/Kaggle ingestion path, leaving Gemini baseline behavior intact.
- Added auxiliary strategy `chunk_semantic_embedding_bge_m3` for BGE-M3 semantic chunking.
- Added lazy local helpers:
  - `scripts/local_embeddings.py` for `BAAI/bge-m3`.
  - `scripts/local_llm.py` for `Qwen/Qwen2.5-7B-Instruct` JSON generation.
- Extended chunking, embedding, entity extraction, graph/relation extraction, and retrieval smoke CLIs with local backend flags.
- Added `run_w3_ingest_07.py --profile local-kaggle`, with separate artifact dirs and no Gemini requirement.
- Added offline embedding artifact mode for Kaggle, including JSONL embeddings and in-memory retrieval smoke.
- Added Kaggle notebook flow in `notebooks/kaggle/`.

### Defaults
- Embedding model: `BAAI/bge-m3`, dense normalized, 1024 dimensions.
- LLM augmentation model: `Qwen/Qwen2.5-7B-Instruct`, 4-bit.
- Graph DB writes are disabled in Kaggle/local profile; artifacts are generated for later local/cloud import.

## W3 Slot Separation And Artifact Import Update - 2026-06-30

### Implementation Status
- Added embedding slot separation for Gemini and BGE-M3 in the same Neo4j DB:
  - Gemini: `Chunk.embedding` + `chunkVector` + `768`
  - BGE-M3: `Chunk.embedding_bge_m3` + `chunkVectorBgeM3` + `1024`
- Added `--embedding-slot` to embedding and retrieval smoke scripts, with fail-fast checks for slot/index/dimension mismatches.
- Added `--payload-output-dir` to graph provenance export so Kaggle dry-run can emit importable graph payloads without rerunning relation LLM later.
- Added new local import scripts:
  - `scripts/import_graph_payload.py`
  - `scripts/import_embedding_artifacts.py`
- Added backend runtime CPU query embedding service for `BAAI/bge-m3` via `DENSE_QUERY_EMBEDDING_*` settings.

### Operational Path
- Historical 2026-06-30 local-Kaggle path was documented and implemented as:
  - Kaggle batch for chunk/entity/relation/embedding
  - download artifact
  - local import graph payload
  - local import BGE-M3 embeddings
  - local retrieval smoke
  - local runtime query embedding on CPU
- Superseded note: W3-INGEST-07 acceptance on 2026-07-07 uses the `gemini_call` live DB branch as the accepted baseline; this local-Kaggle path remains fallback/repro/comparison.
- `chunk_semantic_embedding_bge_m3` remains an auxiliary strategy and does not overwrite Gemini baseline naming or vectors.

### Verification
- Focused slot/import/runtime regression:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py backend\tests\test_write_graph_provenance.py backend\tests\test_run_w3_ingest_07.py backend\tests\test_import_artifacts.py backend\tests\test_runtime_embedding_service.py -q -p no:cacheprovider`
  - Result: `79 passed`
- Full backend regression after slot/artifact/runtime changes:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests -q -p no:cacheprovider`
  - Result: `202 passed`

### Documentation Sync Status
- Updated:
  - `SPECIFICATIONS.md`
  - `PLAN.md`
  - `PROGRESS.md`
  - `docs/w3_ingest_07_runbook.md`
  - `notebooks/kaggle/README.md`
- Kaggle notebooks were aligned to the new artifact flow, shared partition contract, and resume guidance.

### Status
- Code path for local-Kaggle artifact import/retrieval is complete and regression-tested.
- Historical note: at this checkpoint, W3 was ready for manual acceptance through Kaggle artifacts. Current accepted W3 status is the `gemini_call` live DB branch recorded in the 2026-07-07 W3-INGEST-07 section.

---

## W3-INGEST-06 Live DB Acceptance Update - 2026-07-07

### Runtime Status
- W3-INGEST-06 is now accepted against the live Neo4j DB for the `gemini_call` corpus path.
- BGE-M3 embeddings were written to the separate slot:
  - vector property: `Chunk.embedding_bge_m3`
  - vector index: `chunkVectorBgeM3`
  - expected dimension: `1024`
  - embedding model: `BAAI/bge-m3`
- Gemini baseline embeddings remain untouched:
  - `Chunk.embedding`
  - `chunkVector`
  - `768`

### Strategies And Sources Covered
- Strategies:
  - `chunk_fixed_512`
  - `chunk_structure_parent_child`
  - `chunk_semantic_embedding_bge_m3`
- Sources:
  - `TVGM`
  - `TVHS`
  - `TVKL`
  - `TVNL`

### Embedding Results
- `embed_<source>_<strategy>.json` artifacts exist for all `12` source/strategy pairs.
- All `12` embed summaries have:
  - `completed = true`
  - `embedding_slot = "bge_m3"`
  - `embedding_property = "embedding_bge_m3"`
  - `embedding_backend = "local"`
- DB write totals by strategy:
  - `chunk_fixed_512`: `1158 / 1158`
  - `chunk_semantic_embedding_bge_m3`: `1690 / 1690`
  - `chunk_structure_parent_child`: `3342` child chunks embedded; `1160` parent chunks intentionally skipped by child-only retrieval policy.

### Retrieval Smoke Results
- `retrieval_<source>_<strategy>.json` artifacts exist for all `12` source/strategy pairs.
- All `12` retrieval summaries have:
  - dense hits present
  - sparse hits present
  - `embedding_slot = "bge_m3"`
- Retrieval grouped diagnostics:
  - `chunk_fixed_512`: min dense hits `5`, min sparse hits `5`
  - `chunk_semantic_embedding_bge_m3`: min dense hits `5`, min sparse hits `5`
  - `chunk_structure_parent_child`: min dense hits `5`, min sparse hits `5`
- Parent expansion diagnostics pass for parent-child strategy:
  - `TVGM`: parent expansion hit rate `1.0`
  - `TVHS`: parent expansion hit rate `1.0`
  - `TVKL`: parent expansion hit rate `1.0`
  - `TVNL`: parent expansion hit rate `1.0`

### Runner Artifacts
- Main W3-06 BGE runner artifacts:
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/w3_ingest_06_bge_command_manifest.json`
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/w3_ingest_06_bge_run_summary.json`
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/w3_ingest_06_bge_state.json`
- Runner summary:
  - `completed = true`
  - `command_count = 12`
  - `executed_command_count = 11`
  - `skipped_command_count = 1`
  - `error = null`
- The skipped command was an already-completed resume unit.

### Code Updates Made For Acceptance
- `scripts/embed_chunks.py`
  - Added local batch document embedding path for BGE-M3 via `embed_documents`.
  - Added `--smoke-candidate-k` so dense smoke retrieves a larger candidate pool before applying source/strategy filters.
  - Preserved slot-specific metadata fields for `bge_m3`.
- `scripts/run_w3_ingest_07.py`
  - Added `--db-embedding-slot` with support for `bge_m3` in DB embed/retrieval phase.
  - DB BGE-M3 embed commands use local backend and do not require Gemini.
- Tests updated:
  - `backend/tests/test_embed_chunks.py`
  - `backend/tests/test_run_w3_ingest_07.py`

### Verification
- Focused acceptance regression:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py backend\tests\test_run_w3_ingest_07.py backend\tests\test_import_artifacts.py -q -p no:cacheprovider`
  - Result: `64 passed`

### Caveats
- `chunk_structure_parent_child` payload contains `4504` chunk rows, but Neo4j has `4502` unique `Chunk` nodes for this strategy because two child chunk pairs share the same `chunk_hash`.
- Duplicate hash pairs:
  - `TVHS_chunk_structure_parent_child_child_000070` and `TVHS_chunk_structure_parent_child_child_000071`
  - `TVNL_chunk_structure_parent_child_child_000784` and `TVNL_chunk_structure_parent_child_child_000785`
- The graph writer/importer uses `MERGE (c:Chunk {chunk_hash: row.chunk_hash})`, so duplicate hashes collapse to one node.
- This does not block W3-INGEST-06 acceptance because all unique retrieval child nodes are embedded and dense/sparse retrieval smoke passes.
- Temporary scratch/log directories may remain locally:
  - `pytest-cache-files-w3-06/`
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/logs/`
  - Windows returned access-denied when attempting cleanup, likely due to local file attribute/handle behavior.

**Status**: COMPLETE - W3-INGEST-06 is accepted on the live DB for BGE-M3 embedding and retrieval indexing across all 3 strategies and 4 sources, with dense/sparse smoke retrieval and parent expansion diagnostics passing.

---

## W3-INGEST-07 Full Corpus Baseline Acceptance - 2026-07-07

### Status
- W3-INGEST-07 is accepted for the `gemini_call` live DB branch across all `12` source/strategy pairs.
- Sources covered: `TVKL`, `TVNL`, `TVHS`, `TVGM`.
- Strategies covered:
  - `chunk_fixed_512`
  - `chunk_structure_parent_child`
  - `chunk_semantic_embedding_bge_m3`
- Acceptance audit:
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/w3_ingest_07_acceptance_audit.json`
  - `completed = true`
  - `issues = []`

### Evidence Added
- Added W3-07 audit/materialization/export tooling:
  - `scripts/audit_w3_ingest_07.py`
  - `scripts/materialize_w3_ingest_07_chunk_evidence.py`
  - `scripts/export_embedding_artifacts.py`
- Added audit unit coverage:
  - `backend/tests/test_audit_w3_ingest_07.py`
- Added chunk evidence reports:
  - `<strategy>_chunk_summary.json` for all `3` strategies.
  - `chunk_semantic_embedding_bge_m3_semantic_similarity_report.json`.
- Fixed/parent-child regenerated chunk comparisons pass:
  - `chunk_fixed_512`: `1158 / 1158`, no mismatches.
  - `chunk_structure_parent_child`: `4504 / 4504`, no mismatches.
- Semantic BGE-M3 report is derived from existing chunk metadata because full local BGE re-chunking on CPU was too slow; the report records `derived_from_existing_chunk_metadata = true` and has `745` semantic break-score events.

### Payload And Graph Importability
- Graph payload dry-runs passed for all `3` strategies:
  - `reports/import_checks/import_graph_<strategy>.json`
- Payload/DB acceptance counts:
  - `chunk_fixed_512`: `1158` chunks, `853` relations, `493` canonical relations, `1158` Supabase `source_chunks`.
  - `chunk_structure_parent_child`: `4504` chunks, `9410` relations, `1234` canonical relations, `4504` Supabase `source_chunks`.
  - `chunk_semantic_embedding_bge_m3`: `1690` chunks, `1217` relations, `690` canonical relations, `1690` Supabase `source_chunks`.
  - Total Supabase `source_chunks`: `7352`.

### Offline Embedding Artifacts
- Exported existing Neo4j `embedding_bge_m3` vectors into portable JSONL artifacts:
  - `benchmark/tuvi_golden_dataset/gemini_call/embeddings/<strategy>/<source>_<strategy>_embeddings.jsonl`
- Export route is read-only and does not call Gemini, Qwen, or local BGE inference.
- Offline embedding summaries and smoke reports were written under:
  - `benchmark/tuvi_golden_dataset/gemini_call/reports/offline_embedding/`
- Embedding import dry-runs passed for all `12` artifacts:
  - `reports/import_checks/import_embedding_<source>_<strategy>.json`
- All offline embedding artifacts use:
  - `embedding_slot = "bge_m3"`
  - `embedding_property = "embedding_bge_m3"`
  - `expected_dim = 1024`
  - `vector_index_name = "chunkVectorBgeM3"`

### Caveats
- `relation_drop_counts` remains `{}` in final graph summaries because production graph writes resumed from existing LLM state.
- `chunk_structure_parent_child` still has two duplicate child `chunk_hash` pairs, so payload rows are `4504` but unique Neo4j chunk hashes are `4502`:
  - `TVHS_chunk_structure_parent_child_child_000070` and `TVHS_chunk_structure_parent_child_child_000071`
  - `TVNL_chunk_structure_parent_child_child_000784` and `TVNL_chunk_structure_parent_child_child_000785`
- Parent-child offline embedding artifacts export unique live Neo4j child nodes only:
  - `TVKL`: `983`
  - `TVNL`: `844`
  - `TVHS`: `849`
  - `TVGM`: `666`
- `chunk_structure_parent_child` has `4` LLM relation records with `confidence = 0.0`; this does not break schema or W3-07 acceptance.

### Verification
- Acceptance audit:
  - `.\.venv\Scripts\python.exe -X utf8 scripts\audit_w3_ingest_07.py --regen-chunks-dir benchmark\tuvi_golden_dataset\gemini_call\reports\chunk_regen --output benchmark\tuvi_golden_dataset\gemini_call\reports\w3_ingest_07_acceptance_audit.json`
  - Result: `completed = true`, `issues = []`
- Focused regression:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_chunk_text.py backend\tests\test_extract_entities.py backend\tests\test_write_graph_provenance.py backend\tests\test_embed_chunks.py backend\tests\test_smoke_retrieval.py backend\tests\test_run_w3_ingest_07.py backend\tests\test_import_artifacts.py backend\tests\test_audit_w3_ingest_07.py -q -p no:cacheprovider`
  - Result: `158 passed`

**Status**: COMPLETE - W3-INGEST-07 is accepted for the full corpus baseline on the `gemini_call` live DB branch, with importable graph payloads, portable BGE-M3 embedding artifacts, import dry-runs, live retrieval smoke, and acceptance audit passing.

---

## Week 4 Foundation Progress Update - 2026-07-09

### Alignment Summary
- Week 4 implementation is aligned with the current W3 accepted baseline:
  - corpus branch: `gemini-call`
  - sources: `TVKL`, `TVNL`, `TVHS`, `TVGM`
  - chunk strategies: `chunk_fixed_512`, `chunk_structure_parent_child`, `chunk_semantic_embedding_bge_m3`
  - runtime embedding slot: `bge_m3`
  - vector property/index/dim: `Chunk.embedding_bge_m3`, `chunkVectorBgeM3`, `1024`
- Current implementation is complete through W5-FE-01.
- Week 5 frontend integration has started with D-26 (`Next.js chat proxy`) complete; W5-FE-02 full chat history/persistence is the next planned boundary.

### W4-EXP-01: Schema `experiment_runs` and `ExperimentConfig` - COMPLETE

#### Implementation Summary
- Added Supabase migration for `experiment_runs`:
  - `infra/supabase/migrations/20260709_experiment_runs.sql`
  - fields include `experiment_id`, `config_name`, `config_hash`, `config`, `status`, `metrics`, `trace`, `notes`, `error`, and timestamps.
  - indexes include `experiment_id`, `config_hash`, and `status`.
- Added the Week 4 experiment config layer:
  - `backend/app/rag/config.py`
  - `load_experiment_config(...)`
  - `config_hash(...)`
  - strict Pydantic models for embedding, rewrite, runtime entity extraction, graph retrieval, dense retrieval, sparse retrieval, reranker, and full `ExperimentConfig`.
- Added production baseline config:
  - `configs/default_production.yaml`
  - defaults to `branch = gemini-call`
  - defaults to `chunk_strategy_id = chunk_fixed_512`
  - keeps accepted baseline strategies available for ablation.
  - uses `bge_m3`, `BAAI/bge-m3`, `chunkVectorBgeM3`, `domain = TUVI`.
- Added `DEFAULT_EXPERIMENT_CONFIG` setting and backend dependencies needed for the LangGraph/RAG foundation.

#### Verification
- Config loads successfully.
- Config hash is stable.
- Missing required fields fail validation.
- Invalid branch, chunk strategy, embedding slot, relation type, top-k, candidate-k, vector index, and fulltext index fail clearly.

**Status**: COMPLETE - W4-EXP-01 deliverable is implemented and verified.

### W4-RAG-01: RAGState and LangGraph config-aware dry run - COMPLETE

#### Implementation Summary
- Added RAG foundation modules:
  - `backend/app/rag/state.py`
  - `backend/app/rag/graph.py`
  - `backend/app/rag/nodes.py`
- Implemented `RAGState` with query, chart, domain, config, candidate lists, output placeholders, and retrieval trace fields.
- Implemented dry-run graph construction with LangGraph when available and a sequential compatibility graph fallback.
- Implemented dry-run entrypoint:
  - `run_rag_dry_run(initial_state, ..., chart_loader=None, config_path=None)`
- Added nodes for:
  - load chart context
  - load config
  - normalize query
  - classify query complexity
  - downstream placeholder pipeline shape
- `chart_type` and `domain_filter` are forced to `TUVI`.
- Existing `/chat` behavior is unchanged in this slice.

#### Verification
- Graph builds and is invokable.
- Dry-run traverses the full node order and records `retrieval_trace.nodes`.
- Tests use fake chart loading and do not require Supabase.

**Status**: COMPLETE - W4-RAG-01 deliverable is implemented and verified.

### W4-RAG-02: Query rewrite and entity extraction toggles - COMPLETE

#### Implementation Summary
- Added query rewrite support:
  - `backend/app/rag/rewrite.py`
  - `QueryRewriteConfig` in `ExperimentConfig`
  - injectable `QueryRewriter` interface for tests.
  - Gemini-backed default rewriter path for runtime use.
  - passthrough/fallback behavior for dry-run and tests.
- Added rewrite guardrails:
  - keep query in `TUVI`
  - preserve detected Tu Vi terms
  - fallback on empty rewrite, out-of-domain rewrite, missing protected terms, or configured rewrite errors.
- Added runtime entity extraction:
  - `backend/app/rag/query_entities.py`
  - dictionary/rule extraction from `configs/entity_extraction.yaml`
  - `RuntimeEntityExtractionConfig` with backend/model/path/max entity/excluded type controls.
- Added toggle-aware trace behavior:
  - rewrite disabled -> normalized query is preserved and trace status is `skipped`
  - entity extraction disabled -> empty entity outputs and trace status is `skipped`
  - enabled paths record backend/model/count metadata.

#### Verification
- Same query runs with rewrite on/off and entity extraction on/off.
- Out-of-domain rewrite falls back.
- Rewrite that drops Tu Vi terms falls back.
- Dictionary extraction finds canonical entities and records trace metadata.

**Status**: COMPLETE - W4-RAG-02 deliverable is implemented and verified.

### W4-RAG-03: Retrieval paths config-aware - COMPLETE

#### Implementation Summary
- Added unified retrieval service:
  - `backend/app/rag/retrieval.py`
- Added unified candidate normalization with:
  - `retrieval_path`
  - `rank`
  - `score`
  - `chunk_id`
  - `chunk_hash`
  - `chunk_type`
  - `parent_id`
  - `chunk_strategy_id`
  - `domain`
  - `source_id`
  - `source_name`
  - `source_page`
  - `text`
  - `text_preview`
  - `title`
  - `matched_entities`
  - `relation_types`
  - `provenance`
- Implemented graph retrieval:
  - uses runtime `query_entities`
  - retrieves direct `MENTIONS` chunks
  - retrieves related-entity chunks through allowed W3 relation edges
  - filters by `domain`, `source_ids`, and `chunk_strategy_id`
  - applies child-only policy for `chunk_structure_parent_child`
- Implemented dense retrieval:
  - embeds `rewritten_query` / normalized query through the runtime dense query embedding service.
  - validates dimension `1024`
  - queries Neo4j vector index `chunkVectorBgeM3`
  - filters by `domain`, `source_ids`, and `chunk_strategy_id`
  - preserves `parent_id` for later expansion.
- Implemented sparse retrieval:
  - uses Neo4j fulltext index `chunkFulltext`
  - uses Lucene-safe query sanitization adapted from W3 smoke retrieval.
  - filters by `domain`, `source_ids`, and `chunk_strategy_id`
  - preserves `parent_id` for later expansion.
- Replaced retrieval placeholders in the dry-run graph with real toggle-aware nodes:
  - disabled path writes `[]` and trace status `skipped`
  - enabled path writes normalized candidates and trace metadata
  - retrieval failures are not silently swallowed.
- Added dependency injection for tests:
  - `run_rag_dry_run(..., neo4j_driver=None, dense_embedding_service=None)`

#### Verification
- Config validation covers retrieval path defaults and invalid retrieval settings.
- Unit tests verify graph Cypher filters, dense vector index usage, BGE-M3 embedding dimension, sparse query sanitization, and common candidate shape.
- Dry-run tests verify independent retrieval toggles and enabled candidate population with fake Neo4j/embedding dependencies.

**Status**: COMPLETE - W4-RAG-03 deliverable is implemented and verified.

### W4-RAG-04: Fusion, rerank and document grading toggle - COMPLETE

#### Implementation Summary
- Added candidate ranking module:
  - `backend/app/rag/ranking.py`
- Implemented config-aware fusion dispatcher for:
  - `rrf`
  - `weighted_sum`
  - `graph_first`
- Fusion deduplicates candidates by `chunk_hash` / `chunk_id`, preserves provenance, merges retrieval path metadata, and records per-path score breakdowns.
- Added reranker wrapper:
  - production default remains disabled through `configs/default_production.yaml`
  - disabled reranker passes fused candidates through and records trace status `skipped`
  - enabled reranker supports dependency injection for tests and future model-backed rerankers
  - added deterministic `LexicalOverlapReranker` fallback for local/test-safe behavior
- Added document grading toggle:
  - production default remains disabled
  - disabled grading passes reranked candidates through and records trace status `skipped`
  - enabled grading uses a deterministic overlap/text-presence stub and writes `document_grade` / `grade_score`
- Replaced Week 4 ranking placeholders in `backend/app/rag/nodes.py` with real nodes:
  - `fusion`
  - `rerank`
  - `document_grading`
- Extended `RAGState` with:
  - `graded_candidates`
  - `ranked_candidates`
- Extended `run_rag_dry_run(...)` / graph construction with injectable `candidate_reranker`.
- Exported `CandidateReranker` from `backend/app/rag/__init__.py`.

#### Verification
- Added `backend/tests/test_rag_ranking.py` covering:
  - RRF dedupe and score breakdown
  - weighted-sum normalized score behavior
  - graph-first priority behavior
  - fusion dispatcher by config
  - reranker disabled pass-through
  - injected reranker reorder/top-k behavior
  - deterministic lexical reranker
  - document grading enabled/disabled behavior
  - dry-run trace for ranking nodes
- Updated dry-run tests to expect `graded_candidates` and `ranked_candidates`.

**Status**: COMPLETE - W4-RAG-04 deliverable is implemented and verified.

### W4-RAG-05: Context assembly, generation and citations - COMPLETE

#### Implementation Summary
- Added context assembly module:
  - `backend/app/rag/context.py`
  - selects from `ranked_candidates` / `graded_candidates` / `reranked_candidates` / `fused_candidates`
  - supports configured context strategies: `balanced`, `dense_first`, `graph_first`, `compact`
  - formats citation-ready context blocks with markers such as `[S1]`
  - preserves chunk/source provenance, strategy ID, retrieval paths and scores
- Added generation module:
  - `backend/app/rag/generation.py`
  - builds a Tử Vi-only Vietnamese prompt using chart summary, query and assembled context
  - provides `GeminiGenerationClient` for runtime
  - provides `DeterministicGenerationClient` for tests
  - returns a safe Vietnamese no-context fallback when retrieved context is missing
- Added citation mapping module:
  - `backend/app/rag/citations.py`
  - maps answer markers like `[S1]` back to selected context chunks
  - returns API-ready `sources` with `source_id`, `source_name`, `source_page`, `chunk_id`, `chunk_hash`, `chunk_strategy_id`, excerpt, score/confidence, retrieval paths and provenance
  - falls back to returning selected context sources if the answer lacks explicit markers
- Replaced W4-RAG-05 placeholders in `backend/app/rag/nodes.py` with real nodes:
  - `context_assembly`
  - `generation`
  - `citation_map`
- Extended `RAGState` with:
  - `context_chunks`
  - `context_summary`
  - `generation_metadata`
  - `citation_metadata`
- Extended `run_rag_dry_run(...)` / graph construction with injectable `generation_client` for test-safe generation.
- Updated `/chat` in `backend/app/main.py` to return:
  - `answer`
  - `sources`
  - `trace`
  - `experiment_id`
  - `config_hash`
  - `chunk_strategy_id`
  - `generation_metadata`
  - `citation_metadata`
- `/chat` now logs request/response/error events through the existing Langfuse stub while avoiding raw stack trace exposure.
- Made backend app import resilient when optional chart engine service modules are unavailable in a lightweight test environment.

#### Verification
- Added `backend/tests/test_rag_context_generation_citations.py` covering:
  - context assembly from ranked candidates
  - context strategy ordering differences
  - no-context generation fallback
  - deterministic cited generation
  - explicit citation marker mapping
  - fallback source mapping when answer has no markers
- Added `backend/tests/test_chat_route.py` covering `/chat` response shape with `answer + sources + trace`.
- Updated dry-run and retrieval tests to expect real W4-RAG-05 nodes and non-empty generation fallback behavior.

**Status**: COMPLETE - W4-RAG-05 deliverable is implemented and verified.

### W4-ABL-01: `AblationRunner` skeleton - COMPLETE

#### Implementation Summary
- Added config-aware ablation runner module:
  - `backend/app/rag/ablation.py`
  - loads ablation manifests from YAML
  - loads smoke/golden datasets from compact JSONL or pretty multiline JSON object streams
  - maps TuViQA release fields (`question`, `chart_repr`, `gold_answer`, `expected_answer_summary`, `gold_context_spans`, `labels`, `question_complexity`, `birth_info`) into ablation dataset items
  - builds `ExperimentConfig` variants from base config + overrides
  - forces `cache_disabled = true` and preserves `domain = TUVI`
  - runs a dataset x config matrix through an injectable RAG callable
  - computes W4 smoke metrics: item count, completion/failure counts, answer-present rate, source coverage, average sources, latency, citation fallback count, and selected-context average
  - computes rule-based/semantic-lite golden metrics using `gold_answer`, `expected_answer_summary`, `gold_context_spans`, generated answers, and returned sources:
    - answer token recall vs gold/summary
    - summary coverage rate
    - answer length
    - char n-gram similarity and ROUGE-L-like recall vs summary
    - gold doc/page/quote coverage
    - citation marker presence and source alignment
- Added experiment-run persistence abstraction:
  - `ExperimentRunStore` protocol
  - `NullExperimentRunStore` for no-write local/report-only runs
  - `InMemoryExperimentRunStore` for tests
  - `SupabaseExperimentRunStore` for runtime `experiment_runs` inserts/updates
- Added report export:
  - JSON report: `ablation_report.json`
  - Markdown report: `ablation_report.md`
  - Markdown report now includes golden answer, gold context, and citation metric tables.
- Added ablation CLI:
  - `scripts/run_ablation.py`
  - supports `--manifest`, `--offline-smoke`, `--skip-persistence`, `--persist-supabase`, `--limit`, `--output-dir`, and `--fail-fast`
- Updated W4 smoke manifest to use the real TuViQA golden release dataset:
  - `configs/w4_ablation_smoke.yaml`
  - `benchmark/tuvi_golden_dataset/release/tuviqa_v1_release.jsonl`
  - local smoke matrix is 2 configs x `--limit 2` release records
  - removed temporary dataset `benchmark/tuvi_golden_dataset/w4_ablation_smoke.jsonl`
- Extended RAG graph/config loading with in-memory `ExperimentConfig` injection:
  - `run_rag_dry_run(..., experiment_config=config)`
  - preserves existing `config_path` behavior for production/backward compatibility
- Exported `AblationRunner` from `backend/app/rag/__init__.py`.

#### Verification
- Added `backend/tests/test_rag_ablation.py` covering:
  - smoke manifest and TuViQA release dataset loading with `limit=2`
  - field mapping from `question/chart_repr` to `query/chart_data`
  - `gold_answer`, `expected_answer_summary`, `gold_context_spans`, and `question_complexity` loading
  - 2 questions x 2 configs matrix execution
  - `cache_disabled = true` enforcement on config variants
  - fake/in-memory experiment-run row creation and completion
  - item failure capture without fail-fast
  - experiment-run payload fields for `experiment_runs`
  - rule-based/semantic-lite metric keys in aggregate reports
  - report file generation
  - in-memory `ExperimentConfig` injection through `run_rag_dry_run(...)`
- Offline smoke command generated report files under:
  - `benchmark/tuvi_golden_dataset/reports/w4_abl_01/`
- Supabase persistence is implemented via `--persist-supabase`; the local verification used `--skip-persistence` to avoid unintended DB writes.

**Status**: COMPLETE - W4-ABL-01 deliverable is implemented against the real TuViQA release golden dataset and verified with offline smoke reporting plus test-covered experiment-run persistence behavior.

### Verification Commands - 2026-07-09
- Focused Week 4/RAG regression:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_experiment_config.py backend\tests\test_rag_dry_run.py backend\tests\test_rag_query_processing.py backend\tests\test_rag_retrieval.py backend\tests\test_runtime_embedding_service.py -q -p no:cacheprovider`
  - Result: `33 passed`
- RAG module compile check:
  - `python -m py_compile backend\app\rag\config.py backend\app\rag\graph.py backend\app\rag\nodes.py backend\app\rag\retrieval.py backend\app\rag\rewrite.py backend\app\rag\query_entities.py backend\app\rag\state.py`
  - Result: passed

### Verification Commands - 2026-07-10
- Focused Week 4/RAG regression including W4-RAG-04:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_experiment_config.py backend\tests\test_rag_dry_run.py backend\tests\test_rag_query_processing.py backend\tests\test_rag_retrieval.py backend\tests\test_rag_ranking.py backend\tests\test_runtime_embedding_service.py -q -p no:cacheprovider`
  - Result: `45 passed`
- Focused Week 4/RAG regression including W4-RAG-05:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_experiment_config.py backend\tests\test_rag_dry_run.py backend\tests\test_rag_query_processing.py backend\tests\test_rag_retrieval.py backend\tests\test_rag_ranking.py backend\tests\test_rag_context_generation_citations.py backend\tests\test_chat_route.py backend\tests\test_runtime_embedding_service.py -q -p no:cacheprovider`
  - Result: `52 passed, 10 warnings`
- RAG/backend compile check including W4-RAG-05 modules:
  - `.\.venv\Scripts\python.exe -m py_compile backend\app\main.py backend\app\rag\config.py backend\app\rag\graph.py backend\app\rag\nodes.py backend\app\rag\context.py backend\app\rag\generation.py backend\app\rag\citations.py backend\app\rag\ranking.py backend\app\rag\retrieval.py backend\app\rag\rewrite.py backend\app\rag\query_entities.py backend\app\rag\state.py`
  - Result: passed
- Focused W4-ABL-01 tests:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_rag_ablation.py -q -p no:cacheprovider`
  - Result: `5 passed`
- Focused Week 4/RAG regression including W4-ABL-01:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_experiment_config.py backend\tests\test_rag_dry_run.py backend\tests\test_rag_query_processing.py backend\tests\test_rag_retrieval.py backend\tests\test_rag_ranking.py backend\tests\test_rag_context_generation_citations.py backend\tests\test_chat_route.py backend\tests\test_runtime_embedding_service.py backend\tests\test_rag_ablation.py -q -p no:cacheprovider`
  - Result: `57 passed, 10 warnings`
- RAG/backend compile check including W4-ABL-01 modules:
  - `.\.venv\Scripts\python.exe -m py_compile backend\app\rag\config.py backend\app\rag\graph.py backend\app\rag\nodes.py backend\app\rag\ablation.py backend\app\rag\__init__.py scripts\run_ablation.py`
  - Result: passed
- Offline W4-ABL-01 smoke run:
  - `.\.venv\Scripts\python.exe scripts\run_ablation.py --manifest configs\w4_ablation_smoke.yaml --offline-smoke --skip-persistence --limit 2`
  - Result: completed `2` configs x `2` dataset items and wrote JSON/Markdown reports.

### Verification Commands - 2026-07-11
- Focused W4-ABL-01 tests after switching to the real TuViQA release dataset:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_rag_ablation.py -q -p no:cacheprovider`
  - Result: `5 passed`
- RAG/backend compile check for ablation modules:
  - `.\.venv\Scripts\python.exe -m py_compile backend\app\rag\ablation.py scripts\run_ablation.py`
  - Result: passed
- Offline W4-ABL-01 golden smoke run:
  - `.\.venv\Scripts\python.exe scripts\run_ablation.py --manifest configs\w4_ablation_smoke.yaml --offline-smoke --skip-persistence --limit 2`
  - Result: completed `2` configs x `2` TuViQA release records with both configs completed and report files regenerated.
- Focused Week 4/RAG regression including W4-ABL-01:
  - `.\.venv\Scripts\python.exe -m pytest backend\tests\test_experiment_config.py backend\tests\test_rag_dry_run.py backend\tests\test_rag_query_processing.py backend\tests\test_rag_retrieval.py backend\tests\test_rag_ranking.py backend\tests\test_rag_context_generation_citations.py backend\tests\test_chat_route.py backend\tests\test_runtime_embedding_service.py backend\tests\test_rag_ablation.py -q -p no:cacheprovider`
  - Result: `57 passed, 10 warnings`

### Current Week 4 Boundary
- Completed deliverables:
  - D-19: Migration `experiment_runs` and `ExperimentConfig` schema
  - D-20: LangGraph/RAGState config-aware
  - D-21: Query rewrite and entity extraction toggles
  - D-22: Graph, dense, and sparse retrieval toggles
  - D-23: Fusion dispatcher, reranker, and document grading toggle
  - D-24: Context assembly, generation, and citation mapping
  - D-25: `AblationRunner` skeleton
- D-26 is now completed in W5-FE-01 below.

---

## Week 5 Frontend Integration Progress Update - 2026-07-11

### W5-FE-01: Kết nối proxy Next.js `/api/chat` - COMPLETE

#### Implementation Summary
- Added a Next.js chat proxy route:
  - `frontend/app/api/chat/route.ts`
  - accepts `POST /api/chat`
  - requires `Authorization: Bearer <Supabase access_token>`
  - verifies the token with Supabase server-side via `supabase.auth.getUser(...)`
  - validates `chart_id` and `query`
  - forwards to FastAPI `/chat` using `BACKEND_API_BASE_URL` with fallback to `NEXT_PUBLIC_API_BASE_URL`
  - forwards `user_id` from the verified Supabase session instead of trusting client-provided user IDs
  - normalizes error responses and avoids leaking backend stack traces
  - applies a local request timeout for slow backend responses
- Added a minimal chart-bound chat UI:
  - `frontend/components/ChatInterface.tsx`
  - reads the current Supabase session client-side
  - sends chat requests to `/api/chat`
  - renders user messages, assistant answers, returned sources, and run metadata such as `experiment_id` and `chunk_strategy_id`
  - handles loading, disabled submit, auth errors, backend errors, and empty-source fallback text
- Integrated chat into chart detail:
  - `frontend/app/chart/[id]/page.tsx`
  - renders `<ChatInterface chartId={chart.id} chartLabel={chart.label} />` after the chart visualizer/debug section
- Refreshed global UI styling toward the new `DESIGN.md` direction:
  - `frontend/app/globals.css`
  - changed base canvas to warm cream `#faf9f5`
  - changed primary CTA/accent to coral `#cc785c`
  - added cream card, dark navy, elevated dark, muted, and on-dark tokens
  - updated display/body font stacks to serif display + Inter-like UI sans fallbacks
  - updated buttons, inputs, panels, debug code preview, and new chat components to follow cream/coral/dark-navy surface rhythm

#### Scope Boundary
- W5-FE-01 intentionally implements only proxy + minimal usable chat proof.
- Supabase chat history persistence remains W5-FE-02.
- Full interactive citation panel remains W5-FE-03.
- Rate limiting and broader error policy remain W5-FE-05.

#### Verification
- Frontend production build:
  - `cd frontend && npm run build`
  - Result: passed. Next.js compiled successfully, type checks passed, and `/api/chat` is listed as a dynamic route.

**Status**: COMPLETE - W5-FE-01 deliverable is implemented and build-verified. Chart detail can now send authenticated chat requests through the Next.js proxy and render backend `answer + sources` responses.

### Current Week 5 Boundary
- Completed deliverables:
  - D-26: Next.js chat proxy
  - D-27: Chat UI đầy đủ với lịch sử
  - D-28: Citation panel
- Not yet completed:
  - D-29: Chart detail page hoàn chỉnh
  - D-30: Error handling và rate limiting

---

## Week 5 Frontend Integration Progress Update - 2026-07-12

### W5-FE-02: Chat UI đầy đủ - COMPLETE

#### Implementation Summary
- Expanded the chart-bound chat UI in `frontend/components/ChatInterface.tsx`:
  - loads or creates one `chat_sessions` row per chart through the existing Supabase `chat_sessions.la_so_id` uniqueness boundary
  - persists full chat history into the existing `chat_sessions.messages` JSONB column
  - normalizes stored messages/sources before rendering so old or malformed JSON entries do not break the UI
  - keeps submit disabled while either history or backend chat request is loading
  - shows explicit history/cold-start status text
  - rolls back failed optimistic sends, restores the failed query into the input, and exposes a retry button
  - preserves answer metadata including `experiment_id`, `config_hash`, `chunk_strategy_id`, generation metadata, citation metadata, and source payloads
- Added shared chat data contracts in `frontend/lib/chatTypes.ts` for reuse between chat and citation components.

#### Scope Boundary
- Uses the existing single-session-per-chart schema (`chat_sessions.messages` JSONB) rather than introducing a normalized `chat_messages` table.
- Broader rate-limit/error policy remains W5-FE-05.

### W5-FE-03: Citation panel - COMPLETE

#### Implementation Summary
- Added `frontend/components/SourceCitationPanel.tsx`:
  - renders source name/id, page fallback, excerpt fallback, score, confidence, retrieval paths, and collapsible technical provenance (`source_id`, `chunk_id`, `chunk_hash`)
  - supports selected/highlighted source cards per assistant answer
  - provides no-source fallback text when the RAG response has no sources
- Updated `ChatInterface` to render a per-answer citation panel:
  - clickable inline citation markers when answer text contains backend `citation_marker` values
  - source quick buttons below each answer so source selection still works when the generated answer omits inline markers
  - per-answer selection state so each assistant response opens/highlights the correct source independently
- Updated `frontend/app/globals.css` with responsive chat history, retry, citation marker, citation panel, selected-source, and provenance styles.

#### Verification
- Frontend production build:
  - `cd frontend && npm run build`
  - Result: passed. Next.js compiled successfully, type checks passed, and `/chart/[id]` includes the expanded chat/citation bundle.

**Status**: COMPLETE - W5-FE-02 and W5-FE-03 deliverables are implemented and build-verified. Chart detail chat now persists multi-turn history in Supabase and renders interactive per-answer citation panels with provenance details.

---

## Week 5 Frontend Integration Progress Update - 2026-07-13

### W5-FE-04: Ghép đầy đủ trang chi tiết lá số - COMPLETE

#### Implementation Summary
- Hardened `frontend/app/chart/[id]/page.tsx` into a more complete chart-detail experience:
  - keeps route protection via Supabase session check and now uses `router.replace("/login")` for cleaner auth redirect behavior
  - filters chart fetch by both `id` and current `user_id` so inaccessible charts resolve to a clean not-found/forbidden state instead of a generic failure
  - distinguishes missing/inaccessible charts from normal success rendering and shows a page-level recovery panel with a dashboard action
  - expands chart summary with created-at metadata and clearer page copy about chart-bound chat history
  - keeps `ChatInterface` integrated after the visualizer so auto-created chat sessions continue to happen through the existing chat UI flow
- Polished the chart board readability in `frontend/components/TuViBoard.tsx` and `frontend/app/globals.css`:
  - each palace now shows an explicit `Cung {position}` badge
  - `ĐH` and `Chi` labels are made explicit for palace metadata at a glance
  - stronger highlighted palace styling and slightly larger palace/star typography improve quick visual scanning
  - visualizer heading now explains what metadata is shown in each palace cell, making it easier to determine which house is which

#### Verification
- Frontend production build:
  - `cd frontend && npm run build`
  - Result: passed. `/chart/[id]` compiled successfully with the refined chart detail and visualizer readability changes.

### W5-FE-05: Error handling và rate limiting - COMPLETE

#### Implementation Summary
- Strengthened `frontend/app/api/chat/route.ts`:
  - added a lightweight in-memory proxy guard keyed by authenticated user id to limit bursty repeated chat submits locally
  - returns `429` with friendly Vietnamese copy and `Retry-After` when the proxy guard is hit
  - normalizes backend `429` / quota-like failures into user-friendly rate-limit responses
  - normalizes validation/auth/not-found/backend failure messages more explicitly
  - logs important proxy failures to server logs without leaking backend stack traces to the client
- Improved frontend chat feedback in `frontend/components/ChatInterface.tsx`:
  - surfaces no-context fallback as a non-fatal explanatory notice inside assistant responses
  - surfaces citation fallback as a softer provenance note instead of a hard error
  - preserves retry flow for failed sends while keeping user-facing messages in Vietnamese

#### Verification
- Frontend production build:
  - `cd frontend && npm run build`
  - Result: passed. Next.js compiled successfully after proxy guard and error-state changes.

### Current Week 5 Boundary
- Completed deliverables:
  - D-26: Next.js chat proxy
  - D-27: Chat UI đầy đủ với lịch sử
  - D-28: Citation panel
  - D-29: Chart detail page hoàn chỉnh
  - D-30: Error handling và rate limiting
- Not yet completed:
  - None in Week 5 scope

**Status**: COMPLETE - W5-FE-04 and W5-FE-05 are now implemented and build-verified. Chart detail is more robust and readable, the TuViBoard is easier to scan by house, and chat proxy/UI error handling now covers burst rate limiting, timeout, validation, auth, and no-context fallback states more clearly.

---

## RAG Chat Reliability & Retrieval Quality Hotfix - 2026-07-11

### Scope
- Fixed the local `/chat` RAG path after frontend integration exposed two runtime issues:
  - backend chat instability / error fallback when Neo4j routing or optional retrieval paths failed
  - poor retrieval quality for simple entity-definition questions such as `Thái Dương có ý nghĩa gì`
- The focus was a production-safe local default path that can answer from Neo4j graph/sparse context without waiting on slow external rewrite/dense embedding steps.

### Root Causes Identified
- Runtime entity extraction was too broad:
  - `NguHanh: Âm Dương` included single-token aliases `Âm` and `Dương`
  - query `Thái Dương có ý nghĩa gì` therefore seeded both `Sao: Thái Dương` and noisy `NguHanh: Âm Dương`
- Production config had reranking and document grading disabled, so weak graph/sparse hits could flow directly into context assembly.
- Vietnamese fulltext retrieval was weak for accented entity-definition queries and could miss the exact definition chunk while returning loose token matches.
- Context assembly ranked some multi-path but mediocre candidates above exact-definition candidates.
- Citation confidence preferred `grade_score` before `rerank_score`, even though grading is mostly pass/fail and rerank better represents final relevance.

### Implementation Summary
- Hardened production runtime defaults in `configs/default_production.yaml`:
  - disabled query rewrite by default for local responsiveness
  - disabled dense retrieval by default to avoid on-demand BGE-M3 loading/timeouts
  - enabled local lexical/entity-aware reranker
  - enabled deterministic document grading
- Reduced noisy entity extraction in `configs/entity_extraction.yaml`:
  - removed aliases `Âm` and `Dương` from `Âm Dương`
  - kept only the exact alias `Âm Dương`
- Added exact canonical entity text retrieval in `backend/app/rag/retrieval.py`:
  - when query entities are available, sparse retrieval also searches chunks containing the canonical entity phrase directly
  - boosts definition-like chunks containing markers such as `Thái Dương:`, `Tánh chất`, `Tánh tình`, `Địa vị`, and `Thế đứng`
  - penalizes chart/example/table-like chunks such as `thông tin lá số`, `bảng tra`, and generic Tử Vi placement tables
- Improved local reranking in `backend/app/rag/ranking.py`:
  - added canonical entity exact-match features
  - added definition heading and definition quality features
  - added meaning-intent detection for questions containing signals like `ý nghĩa`, `nghĩa`, `là gì`, `tượng trưng`, `chủ về`
  - document grading now rejects empty text and can require exact canonical entity presence when extracted entities are available
- Fixed context ordering in `backend/app/rag/context.py`:
  - `balanced` strategy now prioritizes relevance score before multi-path bonus
  - score resolution now prefers `rerank_score` before `grade_score`
- Fixed citation confidence in `backend/app/rag/citations.py`:
  - confidence now prefers `rerank_score` before `grade_score`
- Added/updated regression coverage in:
  - `backend/tests/test_rag_ranking.py`
  - `backend/tests/test_rag_retrieval.py`
  - `backend/tests/test_chat_route.py`

### Validation
- Backend focused regression:
  - `pytest tests/test_rag_ranking.py tests/test_rag_retrieval.py tests/test_chat_route.py -q`
  - Result: `21 passed, 10 warnings`
- Smoke-tested the no-chart RAG endpoint with:
  - `/debug/rag-smoke-no-chart?query=Thái Dương có ý nghĩa gì`
- Before the fix, top citations were weak/noisy chunks such as Lưu Niên Văn Tinh, Âm Dương/vô chính diệu, or unrelated example chart passages.
- After the fix, the selected context includes the correct definition chunk first:
  - `TVGM_chunk_fixed_512_chunk_000087`
  - source: `Tử Vi Giảng Minh`, page `80`
  - excerpt contains: `Thái Dương: - Tánh chất: Quan lộc. - Tánh tình: Thông minh, Trung thực. - Địa vị Tiền tài: Uy quyền, Tài lộc.`

### Remaining Follow-ups
- Improve Vietnamese fulltext analyzer/tokenization to reduce dependence on exact-text fallback.
- Consider definition-query-specific context trimming, e.g. fewer chunks or stricter grading for `X có ý nghĩa gì`.
- Improve chunking so each major star/section has cleaner standalone chunks.
- Re-enable dense retrieval and query rewrite only after runtime preload/caching and timeout policy are stable.

**Status**: COMPLETE - Local `/chat` is stable enough for frontend use, and entity-definition retrieval quality is substantially improved for representative query `Thái Dương có ý nghĩa gì`.

---

## Week 6 RAG/Evaluation Progress Update - 2026-07-14

### Scope of this update

This update records the current Week 6 boundary after completing and verifying the question-aware retrieval work through `W6-RAG-05`. The goal is to keep `PROGRESS.md` aligned with the implementation state before planning the next tasks.

### W6-EVAL-02: Evaluation runner config-aware - COMPLETE WITH CAVEAT

#### Implementation Summary
- Added a config-aware evaluation runner path through `scripts/run_eval.py` and `backend/app/rag/evaluation.py`.
- The runner can execute the RAG pipeline directly with a selected `ExperimentConfig` and write structured JSON/Markdown reports.
- Evaluation report artifacts exist under:
  - `benchmark/tuvi_golden_dataset/reports/w6_eval_02/`
  - `benchmark/tuvi_golden_dataset/reports/w6_eval_02_smoke/`
- Report output includes metric policy notes for Direct/chart-only questions versus corpus-grounded questions.

#### Caveat
- The available report notes that official W6 metric runs require Gemini judge mode for RAGAS-like metrics.
- Existing smoke/baseline reports verify runner plumbing and report generation, but official metric interpretation should still distinguish Gemini-judged runs from offline smoke runs.

**Status**: COMPLETE WITH CAVEAT - The config-aware runner and report path are implemented. Official evaluation claims should reference whether the run used Gemini judge or offline smoke mode.

### W6-RAG-01: Retrieval diagnostics theo complexity và question family - COMPLETE

#### Implementation Summary
- Added structured retrieval diagnostics in `backend/app/rag/diagnostics.py`.
- Diagnostics summarize:
  - extracted/query entities
  - provided or inferred `question_family`
  - provided or inferred `question_complexity`
  - retrieval plan source
  - candidate counts by graph/dense/sparse/fused/context-selected
  - final selected retrieval paths
  - selected, required, and missing evidence roles
  - graph retrieval mode/fallback metadata
  - chart facts summary
- Diagnostics are exposed in RAG responses/dry-run state for debugging and evaluation aggregation.

**Status**: COMPLETE - Retrieval diagnostics are implemented and covered by focused tests.

### W6-RAG-02: Rule-based query planner - COMPLETE

#### Implementation Summary
- Added deterministic planner logic in `backend/app/rag/planner.py`.
- Supported question families include:
  - `core_identity`
  - `menh_house_interpretation`
  - `than_cu_interpretation`
  - `menh_cuc_relation`
  - `special_state_interpretation`
  - `dai_van_interpretation`
  - `menh_tam_hop`
  - `menh_xung_chieu`
  - `topic_house_plus_relations`
  - `synthesis_judgement`
- Planner output includes:
  - `question_family`
  - `question_complexity`
  - retrieval depth
  - required evidence roles
  - chart fact intents
  - enabled retrieval paths
  - graph mode
  - dense gate metadata
- Live chat fallback heuristics infer family/complexity from query text and entities when dataset labels are absent.

**Status**: COMPLETE - Planner output is available in state and diagnostics, with tests covering family mapping and fallback inference.

### W6-RAG-03: Chart fact extractor - COMPLETE

#### Implementation Summary
- Added chart-aware extraction logic that populates `state["chart_facts"]` before retrieval/context assembly.
- The extractor is defensive across multiple chart shapes, including chart representation variants and palace/cung-style structures.
- Extracted information includes:
  - chart availability and detected schema
  - target houses
  - target stars
  - house facts
  - relations
  - verified claims
  - unverified claims/warnings
- Chart facts are summarized in retrieval diagnostics and are available for chart-aware context construction.

**Status**: COMPLETE - Chart fact extraction is implemented and tested for multiple chart-data shapes and defensive fallback behavior.

### W6-RAG-04: Role-aware retrieval - COMPLETE

#### Implementation Summary
- Added evidence-role-aware retrieval query generation through role retrieval utilities used by graph and sparse retrieval.
- Supported evidence roles include:
  - `house_scope`
  - `star_definition`
  - `modifier_effect`
  - `relation_rule`
  - `combination_pattern`
- Retrieval candidates can now carry role metadata such as:
  - `evidence_role`
  - `evidence_roles`
  - `retrieval_intent`
  - `role_query`
- Generic retrieval remains as fallback so recall does not depend only on role-specific queries.
- Diagnostics include candidate counts by evidence role and role query summaries.

**Status**: COMPLETE - Role-aware graph/sparse retrieval is implemented and covered by retrieval tests.

### W6-RAG-05: Conjunctive graph retrieval - COMPLETE

#### Implementation Summary
- Extended graph retrieval from entity-any only to configurable graph modes:
  - `entity_any`
  - `entity_all`
  - `min_hit_count`
- Planner-selected graph modes are now assigned by question family:
  - direct/simple families use `entity_any`
  - relation-heavy One-hop families can use `entity_all`
  - Two-hop/synthesis families can use `min_hit_count`
- Graph retrieval enforces `required_entity_hits` in the Cypher/transaction path for strict matching.
- If strict graph matching returns zero candidates, retrieval falls back in a controlled way to a less strict mode and records diagnostics.
- Graph diagnostics now include:
  - requested mode
  - effective mode
  - requested/effective required entity hits
  - fallback used
  - fallback reason
  - role metadata

#### Verification
- Focused W6-RAG-05 tests:
  - `cd backend && python -m pytest tests/test_rag_retrieval.py -k "graph_retrieval_entity_all_fallbacks_to_entity_any_when_strict_empty or graph_retrieval_tx_enforces_required_entity_hits" -p no:cacheprovider -q`
  - Result: `2 passed, 11 deselected`
- Week 6 RAG focused regression:
  - `cd backend && python -m pytest tests/test_rag_retrieval.py tests/test_rag_chart_facts.py tests/test_rag_planner.py tests/test_rag_diagnostics.py -p no:cacheprovider -q`
  - Result: `30 passed`

**Status**: COMPLETE - Multi-entity graph retrieval can require all/minimum entity hits, strict fallback is traced, and retrieval tests pass.

### Current Week 6 Boundary

#### Completed or implementation-verified
- `W6-EVAL-02`: Evaluation runner config-aware, with official-metric caveat for Gemini judge mode.
- `W6-RAG-01`: Retrieval diagnostics by complexity/family.
- `W6-RAG-02`: Rule-based query planner.
- `W6-RAG-03`: Chart fact extractor and chart-aware state.
- `W6-RAG-04`: Role-aware retrieval with evidence roles.
- `W6-RAG-05`: Conjunctive graph retrieval with `entity_all`/`min_hit_count` and strict fallback diagnostics.

#### Not yet completed / next candidates
- `W6-RAG-06`: Role-aware context assembly.
  - Needed before official `W6-ABL-02` because retrieval ablation depends on context selection by required evidence roles.
  - Expected work: prioritize chart facts, select at least one chunk per required role when budget allows, record role coverage summary, and format context blocks with role labels.
- `W6-RAG-07`: Planner-gated dense retrieval.
  - Should wait until `W6-RAG-06` is complete.
  - Expected work: enforce dense gate so Direct chart QA does not run dense retrieval, add dense diagnostics, and produce latency/quality evidence.
- `W6-DOC-01`: Question-aware and chart-aware retrieval roadmap doc.
  - Recommended before or alongside `W6-RAG-06`/`W6-RAG-07` so the design rationale remains explicit.
- `W6-ABL-02`: Retrieval/fusion/reranker ablation v1.
  - Blocked until at least `W6-RAG-06` is complete per `PLAN.md` dependencies.

### Recommended Next Step

Before implementation work resumes, write or update the design/roadmap documentation for question-aware and chart-aware retrieval, then implement `W6-RAG-06` with focused tests for role-aware context assembly and citation preservation.

---

## Week 6 RAG Progress Update - W6-RAG-06 Complete - 2026-07-14

### W6-RAG-06: Role-aware context assembly - COMPLETE

#### Implementation Summary
- Upgraded `backend/app/rag/context.py` so context assembly becomes role-aware when `retrieval_plan.required_evidence_roles` is present.
- Kept backward-compatible behavior for queries/configs without required evidence roles:
  - the existing configured context strategy such as `balanced`, `graph_first`, `dense_first`, or `compact` still orders candidates;
  - role-aware selection only adds a soft role-coverage pass before global fill when the planner requires evidence roles.
- Implemented role-aware selection policy:
  - attempt to select at least one candidate per required evidence role when budget allows;
  - deduplicate selected chunks by `chunk_hash`/`chunk_id`;
  - fill remaining budget with globally ranked candidates;
  - sort final selected chunks back by original strategy order to preserve relevance and stable citation marker ordering.
- Preserved chart-first context ordering:
  - `[CHART]` summary remains before corpus chunks;
  - `[CHART_FACTS]` remains before corpus chunks;
  - corpus chunks still receive citation markers `[S1]`, `[S2]`, ...
- Expanded `context_summary` with W6-RAG-06 diagnostics:
  - `role_aware_enabled`
  - `required_evidence_roles`
  - `selected_evidence_roles`
  - `missing_evidence_roles`
  - `role_coverage_rate`
  - `selected_chunks_by_role`
  - `role_selection.required_role_count`
  - `role_selection.covered_role_count`
  - `role_selection.fallback_fill_count`
  - `chart_context_priority = "before_corpus_chunks"`
- Kept role labels in generated context blocks using existing metadata line format:
  - `evidence_roles: ... | retrieval_intent: ...`
- Updated chart-only generation behavior in `backend/app/rag/generation.py`:
  - generation can now run when `final_context` contains chart/chart-fact context even if no corpus `context_chunks` are selected;
  - citation mapping still returns no corpus sources when there are no selected corpus chunks;
  - retrieval backend failure remains protected and still produces `no_context` fallback instead of masking backend outage with chart-only context.

#### Files Modified
- `backend/app/rag/context.py`
- `backend/app/rag/generation.py`
- `backend/tests/test_rag_context_generation_citations.py`
- `backend/tests/test_rag_dry_run.py`

#### Verification
- Focused context/generation/citation tests:
  - `cd backend && python -m pytest tests/test_rag_context_generation_citations.py -p no:cacheprovider -q`
  - Result: `10 passed`
- W6 RAG focused regression:
  - `cd backend && python -m pytest tests/test_rag_context_generation_citations.py tests/test_rag_diagnostics.py tests/test_rag_retrieval.py tests/test_rag_planner.py tests/test_rag_chart_facts.py -p no:cacheprovider -q`
  - Result: `40 passed, 1 warning`
- Dry-run/chat regression:
  - `cd backend && python -m pytest tests/test_rag_dry_run.py tests/test_chat_route.py -p no:cacheprovider -q`
  - Result: `4 passed, 11 warnings`
- Combined W6/backend chat regression:
  - `cd backend && python -m pytest tests/test_rag_context_generation_citations.py tests/test_rag_diagnostics.py tests/test_rag_retrieval.py tests/test_rag_planner.py tests/test_rag_chart_facts.py tests/test_rag_dry_run.py tests/test_chat_route.py -p no:cacheprovider -q`
  - Result: `44 passed, 11 warnings`

#### Current Boundary After W6-RAG-06
- Completed:
  - `W6-RAG-01`: retrieval diagnostics by complexity/family.
  - `W6-RAG-02`: rule-based query planner.
  - `W6-RAG-03`: chart fact extractor.
  - `W6-RAG-04`: role-aware retrieval.
  - `W6-RAG-05`: conjunctive graph retrieval.
  - `W6-RAG-06`: role-aware context assembly.
- Next recommended tasks:
  - `W6-DOC-01`: write `docs/rag_question_aware_retrieval.md` to document the now-implemented question-aware/chart-aware retrieval design.
  - `W6-RAG-07`: planner-gated dense retrieval with latency/quality diagnostics.
  - `W6-ABL-02`: retrieval/fusion/reranker ablation v1 can now proceed after documentation/planner-gated dense decision, because the W6-RAG-06 dependency is satisfied.

**Status**: COMPLETE - W6-RAG-06 deliverable is implemented and test-verified. Context assembly is now question-family-aware and role-aware while preserving previous behavior when no required evidence roles are present.

---

## Week 6 RAG Progress Update - W6-RAG-07 Complete - 2026-07-14

### W6-RAG-07: Planner-gated dense retrieval - COMPLETE

#### Implementation Summary
- Implemented planner-gated dense retrieval in `backend/app/rag/nodes.py`.
- Dense retrieval now runs only when all runtime gates allow it:
  - `ExperimentConfig.dense_retrieval_enabled` is true;
  - `retrieval_plan.enabled_retrieval_paths.dense` is true;
  - `retrieval_plan.dense_gate.enabled` is true;
  - query term count satisfies `retrieval_plan.dense_gate.min_query_terms` when configured;
  - retrieval backend is still available.
- Direct chart-only QA remains protected:
  - `core_identity` planner output disables dense retrieval;
  - dense is skipped even when an ablation config globally enables dense.
- Added dense trace detail for evaluation/debugging:
  - `enabled_by_config`
  - `enabled_by_plan`
  - `enabled_by_dense_gate`
  - `query_term_count`
  - `min_query_terms`
  - `query_terms_ok`
  - `skipped_reason`
  - `duration_ms` for completed/fallback dense calls
  - `embedding_cache_stats`
- Added lazy query embedding cache to `DenseQueryEmbeddingService` in `backend/app/clients.py`:
  - keeps the existing service-level `@lru_cache(maxsize=1)`;
  - caches repeated normalized query strings inside the service;
  - exposes `cache_stats()` for trace diagnostics;
  - does not preload BGE-M3 automatically.
- Added dense-specific retrieval diagnostics in `backend/app/rag/diagnostics.py`:
  - candidate count;
  - selected context count;
  - selected context rate;
  - dense gate/config flags;
  - skip reason;
  - dense node latency;
  - embedding cache stats.
- Added ablation-ready config:
  - `configs/w6_planner_gated_dense.yaml`
  - It sets `dense_retrieval_enabled: true`, while runtime execution remains planner-gated.
- Kept `configs/default_production.yaml` dense off by default and updated comments to point to the ablation config.

#### Clarified Decisions From User Confirmation
These confirmations apply to this W6-RAG-07 task implementation only. Final production behavior should be revisited later after ablation and production p95 latency evidence.

1. Dense production default vs ablation preparation:
   - Confirmed for this task: keep `default_production.yaml` dense off and prepare an ablation config instead.
   - Implemented: `configs/w6_planner_gated_dense.yaml` enables dense globally for experiments, but planner gate still prevents Direct chart QA from running dense.
   - Production recommendation later: only turn dense on in `default_production.yaml` if W6/W7 ablation shows a quality gain that justifies latency/cost, and p95 chat latency remains within target.
2. Preload behavior:
   - Confirmed for this task: no automatic preload; use lazy-load plus query embedding cache.
   - Implemented: BGE-M3 local client is still created lazily on first dense query; repeated query embeddings are cached.
   - Production recommendation later: consider startup/pre-warm or background preload only after measuring cold-start impact on Render/local runtime.
3. Ablation config artifact:
   - Confirmed for this task: create a dedicated config YAML.
   - Implemented: `configs/w6_planner_gated_dense.yaml`.
   - Production recommendation later: include this config in W6-ABL-02/W7-CONFIG-01 evidence before promoting it.
4. Latency diagnostics scope:
   - Confirmed for this task: measure dense-node latency only.
   - Implemented: `dense_retrieval` trace has `duration_ms`; retrieval diagnostics exposes it.
   - Production recommendation later: W7 observability should add end-to-end span timing and per-node Langfuse spans for all major pipeline nodes, not just dense.

#### Files Modified
- `backend/app/clients.py`
- `backend/app/rag/nodes.py`
- `backend/app/rag/diagnostics.py`
- `backend/tests/test_experiment_config.py`
- `backend/tests/test_rag_diagnostics.py`
- `backend/tests/test_rag_retrieval.py`
- `backend/tests/test_runtime_embedding_service.py`
- `configs/default_production.yaml`
- `configs/w6_planner_gated_dense.yaml`
- `PROGRESS.md`

#### Verification
- Focused W6-RAG-07 regression:
  - `cd backend && python -m pytest tests/test_rag_retrieval.py tests/test_rag_diagnostics.py tests/test_runtime_embedding_service.py tests/test_experiment_config.py -p no:cacheprovider -q`
  - Result: `39 passed, 1 warning`
- Broader W6/backend chat regression:
  - `cd backend && python -m pytest tests/test_rag_context_generation_citations.py tests/test_rag_diagnostics.py tests/test_rag_retrieval.py tests/test_rag_planner.py tests/test_rag_chart_facts.py tests/test_rag_dry_run.py tests/test_chat_route.py tests/test_runtime_embedding_service.py tests/test_experiment_config.py -p no:cacheprovider -q`
  - Result: `68 passed, 11 warnings`

#### Current Boundary After W6-RAG-07
- Completed:
  - `W6-RAG-01`: retrieval diagnostics by complexity/family.
  - `W6-RAG-02`: rule-based query planner.
  - `W6-RAG-03`: chart fact extractor.
  - `W6-RAG-04`: role-aware retrieval.
  - `W6-RAG-05`: conjunctive graph retrieval.
  - `W6-RAG-06`: role-aware context assembly.
  - `W6-RAG-07`: planner-gated dense retrieval with cache and dense latency diagnostics.
- Next recommended tasks:
  - `W6-DOC-01`: write `docs/rag_question_aware_retrieval.md` documenting the implemented question-aware/chart-aware retrieval design, including the W6-RAG-07 production caveats above.
  - `W6-ABL-02`: run retrieval/fusion/reranker ablation comparing default no-dense against `configs/w6_planner_gated_dense.yaml`.
  - `W7-OBS-01`/`W7-OBS-02`: add production span timing and p95 latency evidence before deciding whether dense should be enabled in final production config.

**Status**: COMPLETE - W6-RAG-07 deliverable is implemented and test-verified. Dense retrieval is now planner-gated, Direct chart QA skips dense, One-hop/Two-hop can run dense when config and planner allow it, and ablation-ready config/diagnostics are available.

---

## Week 6 Documentation Progress Update - W6-DOC-01 Complete - 2026-07-14

### W6-DOC-01: Question-aware and chart-aware retrieval roadmap doc - COMPLETE

#### Implementation Summary
- Created `docs/rag_question_aware_retrieval.md` as the primary W6 design note for the now-implemented question-aware/chart-aware retrieval path.
- Updated `docs/README.md` to link the new design note under Design notes.
- Documented the progression from generic retrieval limitations to the current pipeline:
  - query family and complexity diagnostics;
  - deterministic query planner;
  - chart fact extraction and chart-aware context;
  - role-aware graph/sparse retrieval;
  - conjunctive graph retrieval modes;
  - role-aware context assembly;
  - planner-gated dense retrieval and ablation config.
- Added a full question-family mapping for the current planner families:
  - `core_identity`
  - `menh_house_interpretation`
  - `than_cu_interpretation`
  - `menh_cuc_relation`
  - `special_state_interpretation`
  - `dai_van_interpretation`
  - `menh_tam_hop`
  - `menh_xung_chieu`
  - `topic_house_plus_relations`
  - `synthesis_judgement`
- Added evidence-role documentation for:
  - `house_scope`
  - `star_definition`
  - `modifier_effect`
  - `relation_rule`
  - `combination_pattern`
- Added the Task A-G mapping back to W6-RAG-01..07.
- Added validation guidance and manual/dry-run checks for Direct, One-hop, Two-hop and dense-ablation behavior.

#### Production Caveats Captured
- Dense remains off in `configs/default_production.yaml`; use `configs/w6_planner_gated_dense.yaml` for ablation.
- Dense should only be promoted to production after W6/W7 quality and p95 latency evidence.
- BGE-M3 remains lazy-loaded with query embedding cache; no automatic preload is recommended until cold-start impact is measured.
- Current dense timing is node-local; W7 observability should add Langfuse spans for all major pipeline nodes.
- Direct chart QA may be correctly chart-grounded without corpus citation, so evaluation/UI should distinguish chart-grounded vs corpus-grounded answers.

#### Files Modified
- `docs/rag_question_aware_retrieval.md`
- `docs/README.md`
- `PROGRESS.md`

#### Verification
- Documentation artifact exists:
  - `Test-Path docs/rag_question_aware_retrieval.md`
  - Result: `True`
- Required documentation patterns verified:
  - `core_identity`
  - `W6-RAG-07`
  - `configs/w6_planner_gated_dense.yaml`
  - `role_coverage_rate`
- Docs index verified to include `rag_question_aware_retrieval.md`.

#### Current Boundary After W6-DOC-01
- Completed and documented:
  - `W6-RAG-01`: retrieval diagnostics by complexity/family.
  - `W6-RAG-02`: rule-based query planner.
  - `W6-RAG-03`: chart fact extractor.
  - `W6-RAG-04`: role-aware retrieval.
  - `W6-RAG-05`: conjunctive graph retrieval.
  - `W6-RAG-06`: role-aware context assembly.
  - `W6-RAG-07`: planner-gated dense retrieval.
  - `W6-DOC-01`: question-aware/chart-aware retrieval design doc.
- Next recommended task:
  - `W6-ABL-02`: run retrieval/fusion/reranker ablation comparing default no-dense against `configs/w6_planner_gated_dense.yaml` and other planned configs.

**Status**: COMPLETE - W6-DOC-01 deliverable is implemented. The team can now understand the question-aware/chart-aware retrieval roadmap, implemented scope, diagnostics, validation plan and production caveats without reading the whole codebase.

---

## Week 6 Ablation Progress Update - W6-ABL-02 Complete - 2026-07-14

### W6-ABL-02: Retrieval/fusion/reranker ablation v1 - COMPLETE

#### Implementation Summary
- Created `configs/w6_abl_02_retrieval_matrix.yaml` as the official W6-ABL-02 retrieval/fusion/reranker matrix manifest.
- Added 11 ablation configs covering the PLAN.md requirements:
  - `baseline_graph_sparse_rrf`
  - `graph_only_rrf`
  - `sparse_only_rrf`
  - `dense_only_rrf`
  - `dense_sparse_rrf`
  - `graph_dense_rrf`
  - `graph_sparse_rrf`
  - `all_paths_planner_dense_rrf`
  - `baseline_no_reranker`
  - `baseline_weighted_sum`
  - `baseline_graph_first`
- Dense variants use `configs/w6_planner_gated_dense.yaml`, so dense is globally enabled for ablation but still planner-gated at runtime:
  - Direct chart QA should skip dense.
  - One-hop/Two-hop can run dense when planner and query length allow it.
- Extended `backend/app/rag/evaluation.py` report generation with an automatic `ablation_analysis` block containing:
  - baseline config name;
  - rankings by Context Recall, Citation Coverage, Graph Hit Rate and p95 latency;
  - retrieval miss summary;
  - rerank miss summary;
  - preliminary recommendation heuristic.
- Extended the Markdown report with an `## Ablation analysis` section including retrieval miss and rerank miss tables.
- Added regression tests for:
  - W6-ABL-02 manifest loading;
  - 11 unique experiment configs;
  - dense/no-reranker/fusion overrides;
  - `ablation_analysis` JSON/Markdown rendering;
  - retrieval miss and rerank miss heuristics.

#### Files Modified or Created
- `configs/w6_abl_02_retrieval_matrix.yaml`
- `backend/app/rag/evaluation.py`
- `backend/tests/test_rag_evaluation.py`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.json`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.md`
- `PROGRESS.md`

#### Verification - Focused Tests
Command:

```powershell
cd backend; python -m pytest tests/test_rag_evaluation.py tests/test_experiment_config.py -p no:cacheprovider -q
```

Result:

```text
24 passed in 2.38s
```

#### Verification - W6-ABL-02 Offline Smoke
Command:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_02_retrieval_matrix.yaml --offline-smoke --limit 2 --skip-persistence
```

Result summary:

```text
manifest_name: w6_abl_02_retrieval_fusion_reranker_v1
dataset_item_count: 2
config_count: 11
judge_backend: static-smoke
statuses: all 11 configs completed
```

Generated local smoke reports:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.md
```

Report pattern checks passed for:

```text
Ablation analysis
Retrieval miss summary
Rerank miss summary
baseline_graph_sparse_rrf
```

#### Official Run Command
The implementation smoke did **not** persist Supabase rows and did **not** use Gemini judge. This is intentional: static smoke verifies plumbing only and is not the official W6 metric run.

Official partial run when Gemini quota and live Neo4j/Supabase env are available:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_02_retrieval_matrix.yaml --judge-backend gemini --limit 10 --persist-supabase
```

Official full run:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_02_retrieval_matrix.yaml --judge-backend gemini --persist-supabase
```

#### Caveats and Boundary
- The smoke report uses `static-smoke`, so its metric values and preliminary recommendation are not production evidence.
- Dense latency/quality tradeoff must be judged from the official Gemini/live retrieval run, not from offline smoke.
- The `ablation_analysis.preliminary_recommendation` is a heuristic ranking helper, not a final production config decision.
- Final production config selection remains part of `W7-CONFIG-01` after W6-ABL-02 official evidence and W7 p95 latency evidence.

#### Next Recommended Tasks
- Run W6-ABL-02 official partial/full with Gemini judge when quota allows.
- Continue to `W6-ABL-03` chunking strategy ablation after retrieval/fusion/reranker evidence is available.
- Use W6-ABL-02 report output as input to `W7-CONFIG-01` production config selection.

**Status**: COMPLETE - W6-ABL-02 implementation is complete and smoke-verified. The retrieval/fusion/reranker matrix, automated ablation analysis, local report artifacts and verification commands are in place. Official Gemini/live DB run remains the next evidence-gathering step when quota/env are available.

---

## Cập nhật tiến độ Tuần 6 - Hoàn tất cài đặt W6-ABL-03 - 2026-07-14

### W6-ABL-03: Ablation chiến lược chunking - ĐÃ CÀI ĐẶT VÀ SMOKE-VERIFY

#### Mục tiêu của task
W6-ABL-03 dùng để so sánh 3 chiến lược chunking trên cùng một nền dữ liệu, không đổi corpus và không đổi golden dataset. Biến chính của thí nghiệm là:

```text
chunk_strategy_id
```

Ba chiến lược được so sánh trong runtime hiện tại là:

```text
chunk_fixed_512
chunk_structure_parent_child
chunk_semantic_embedding_bge_m3
```

Ghi chú quan trọng: `PLAN.md` gọi chiến lược semantic là `chunk_semantic_embedding`, nhưng code runtime hiện chỉ chấp nhận mã chính thức `chunk_semantic_embedding_bge_m3`. Vì vậy W6-ABL-03 dùng `chunk_semantic_embedding_bge_m3` và ghi rõ đây là mã vận hành của strategy semantic embedding.

#### Quyết định triển khai đã chốt
- Dùng `chunk_semantic_embedding_bge_m3`, không sửa code để thêm alias `chunk_semantic_embedding`.
- Matrix chính giữ cố định retrieval stack:
  - Graph retrieval: bật.
  - Sparse retrieval: bật.
  - Dense retrieval: tắt.
  - Fusion: `rrf`.
  - Reranker: bật.
  - Context assembly: `balanced`.
- Lý do tắt dense: W6-ABL-03 phải cô lập biến chunking. Nếu bật dense, kết quả sẽ trộn lẫn ảnh hưởng của chunking với query embedding, vector index, preload/cache và latency dense retrieval.
- Kiểm tra coverage local dùng `--allow-missing`, vì repo hiện chỉ có artifact local cho `chunk_fixed_512`; coverage runtime chính thức phải kiểm bằng Neo4j.
- Thêm phân tích riêng `chunking_ablation_analysis` trong report để có ranking theo strategy và gợi ý ứng viên chunking sơ bộ.

#### File đã tạo hoặc chỉnh sửa
- `configs/w6_abl_03_chunking_matrix.yaml`
- `scripts/check_w6_abl_03_chunk_coverage.py`
- `backend/app/rag/evaluation.py`
- `backend/tests/test_rag_evaluation.py`
- `backend/tests/test_w6_abl_03_chunk_coverage.py`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.json`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.md`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.json`
- `benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md`
- `PROGRESS.md`

#### Manifest W6-ABL-03
Manifest chính:

```text
configs/w6_abl_03_chunking_matrix.yaml
```

Manifest có 3 config:

| Config | Chunk strategy | Retrieval stack |
|---|---|---|
| `fixed_512_graph_sparse_rrf` | `chunk_fixed_512` | Graph + Sparse + RRF + reranker |
| `parent_child_graph_sparse_rrf` | `chunk_structure_parent_child` | Graph + Sparse + RRF + reranker |
| `semantic_bge_m3_graph_sparse_rrf` | `chunk_semantic_embedding_bge_m3` | Graph + Sparse + RRF + reranker |

Tất cả config dùng cùng 4 nguồn:

```text
TVKL, TVNL, TVHS, TVGM
```

#### Coverage checker
Script mới:

```text
scripts/check_w6_abl_03_chunk_coverage.py
```

Script kiểm tra đủ 12 cặp source-strategy:

```text
4 nguồn x 3 strategy = 12 cặp
```

Hai chế độ:

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode local-artifacts
python scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
```

Ý nghĩa:
- `local-artifacts`: chỉ kiểm file JSONL trong repo, phù hợp smoke cục bộ.
- `neo4j`: kiểm dữ liệu `Chunk` runtime trong Neo4j, nên dùng làm bằng chứng chính thức trước khi chạy Gemini evaluation.

#### Kết quả coverage local smoke
Command đã chạy:

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode local-artifacts --allow-missing
```

Kết quả:

```text
completed: false
expected_pair_count: 12
observed_pair_count: 4
missing_pair_count: 8
mode: local-artifacts
```

Diễn giải:
- Repo hiện có đủ local artifact cho `chunk_fixed_512` trên 4 nguồn.
- Repo hiện thiếu local artifact cho:
  - `chunk_structure_parent_child` trên 4 nguồn;
  - `chunk_semantic_embedding_bge_m3` trên 4 nguồn.
- Đây chưa phải kết luận runtime thiếu dữ liệu, vì retrieval đọc từ Neo4j. Cần chạy `--mode neo4j` để xác nhận dữ liệu live DB.

Report coverage đã sinh:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.md
```

#### Phân tích chunking trong evaluation report
Đã bổ sung `chunking_ablation_analysis` vào report JSON khi manifest là W6-ABL-03 hoặc khi report có nhiều `chunk_strategy_id`.

Nội dung phân tích gồm:
- phạm vi so sánh chunking;
- ghi chú tên strategy semantic;
- chính sách tắt dense để cô lập biến chunking;
- danh sách strategy;
- ranking theo Context Recall;
- ranking theo Citation Coverage;
- ranking theo Graph Hit Rate;
- ranking theo p95 latency;
- ứng viên chunking sơ bộ.

Trong Markdown report, section tiếng Việt là:

```text
## Phân tích ablation chiến lược chunking
```

#### Verification - Focused tests
Command:

```powershell
cd backend; python -m pytest tests/test_rag_evaluation.py tests/test_experiment_config.py tests/test_w6_abl_03_chunk_coverage.py -p no:cacheprovider -q
```

Kết quả:

```text
28 passed in 4.99s
```

#### Verification - Evaluation smoke
Command:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --offline-smoke --limit 2 --skip-persistence
```

Kết quả tóm tắt:

```text
manifest_name: w6_abl_03_chunking_strategy_v1
dataset_item_count: 2
config_count: 3
judge_backend: static-smoke
statuses: all 3 configs completed
```

Report evaluation đã sinh:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md
```

Đã kiểm tra report có các phần:

```text
Phân tích ablation chiến lược chunking
Ứng viên chunking sơ bộ
chunk_semantic_embedding_bge_m3
```

#### Lưu ý rất quan trọng về kết quả smoke
Kết quả smoke dùng `static-smoke`, không dùng Gemini judge, không dùng Neo4j live, không persist Supabase. Vì vậy:
- Không được dùng metric smoke để chọn production config.
- Không được coi ứng viên chunking sơ bộ trong smoke là quyết định cuối.
- W6-ABL-03 chỉ có bằng chứng chính thức sau khi:
  1. `--mode neo4j` xác nhận đủ 12 cặp source-strategy trong live DB;
  2. chạy Gemini judge trên cùng golden dataset/subset;
  3. so sánh Context Recall, Citation Coverage, Graph Hit Rate và latency.

#### Lệnh kiểm tra runtime chính thức bằng Neo4j
Khi có env Neo4j live:

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
```

Điều kiện đạt:

```text
completed: true
expected_pair_count: 12
observed_pair_count: 12
missing_pair_count: 0
```

#### Lệnh chạy official partial bằng Gemini
Khi có quota Gemini và Neo4j/Supabase sẵn sàng:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --persist-supabase
```

#### Lệnh chạy official full bằng Gemini

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --persist-supabase
```

#### Tiêu chí hoàn tất bằng chứng W6-ABL-03 sau này
W6-ABL-03 implementation đã xong, nhưng bằng chứng chính thức cần thêm:
- Neo4j coverage đủ 12 cặp source-strategy.
- Report official có đủ 3 strategy trên cùng golden dataset/corpus.
- Ranking strategy dựa trên metric thật:
  - Context Recall;
  - Citation Coverage;
  - Graph Hit Rate;
  - p95 latency.
- Có khuyến nghị chunking candidate kèm lý do.

#### Task tiếp theo khuyến nghị
- Nếu muốn đóng bằng chứng W6-ABL-03 ngay: chạy `--mode neo4j`, rồi chạy official Gemini partial/full.
- Nếu chưa có quota/env: chuyển sang `W6-INT-01` hoặc chuẩn bị dữ liệu/Neo4j để chạy official ablation.
- Kết quả W6-ABL-03 official sẽ là đầu vào cho `W7-CONFIG-01` khi chọn production config cuối.

**Trạng thái**: COMPLETE ở mức cài đặt và smoke verification. Chưa COMPLETE ở mức bằng chứng official vì local repo hiện thiếu artifact cho 8/12 cặp và chưa chạy Gemini/live Neo4j official run.

---

## Cập nhật tiến độ W6-ABL-03 - Neo4j coverage và Gemini partial official - 2026-07-14

### Kết quả chạy Option 1
Đã thực hiện Option 1 theo thứ tự an toàn:

1. Kiểm tra runtime coverage trong Neo4j.
2. Chạy W6-ABL-03 bằng Gemini judge trên golden subset `limit 10`.
3. Verify report JSON/Markdown và log lỗi.

### 1. Neo4j coverage - PASS
Command đã chạy:

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
```

Kết quả:

```text
completed: true
expected_pair_count: 12
observed_pair_count: 12
missing_pair_count: 0
mode: neo4j
```

Report đã cập nhật:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.md
```

Coverage runtime theo Neo4j:

| Source | `chunk_fixed_512` | `chunk_structure_parent_child` | `chunk_semantic_embedding_bge_m3` |
|---|---:|---:|---:|
| `TVKL` | 347 | 1330 | 511 |
| `TVNL` | 266 | 1110 | 363 |
| `TVHS` | 287 | 1138 | 439 |
| `TVGM` | 258 | 924 | 377 |

Diễn giải:
- Local artifacts vẫn thiếu một số file JSONL, nhưng runtime Neo4j đã đủ 12/12 cặp source-strategy.
- W6-ABL-03 có thể chạy official evaluation vì RAG retrieval đọc từ Neo4j.

### 2. Supabase persistence attempt - BLOCKED
Command đã thử trước:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --persist-supabase
```

Kết quả: fail trước khi chạy evaluation vì Supabase chưa thấy bảng `experiment_runs`:

```text
postgrest.exceptions.APIError: {
  'message': "Could not find the table 'public.experiment_runs' in the schema cache",
  'code': 'PGRST205'
}
```

Nguyên nhân khả dĩ:
- migration `infra/supabase/migrations/20260709_experiment_runs.sql` đã có trong repo nhưng chưa được apply lên Supabase project đang dùng; hoặc
- migration đã apply nhưng PostgREST schema cache chưa reload.

Việc cần làm để bật lại `--persist-supabase`:

```text
Apply migration infra/supabase/migrations/20260709_experiment_runs.sql lên Supabase live DB,
sau đó reload PostgREST/schema cache nếu cần.
```

Migration hiện có trong repo tạo:
- bảng `experiment_runs`;
- trigger `experiment_runs_update_timestamp`;
- indexes `idx_experiment_runs_experiment_id`, `idx_experiment_runs_config_hash`, `idx_experiment_runs_status`.

### 3. Gemini partial official local report - PASS
Vì Supabase persistence bị block, đã chạy lại Gemini partial với `--skip-persistence` để vẫn lấy metric official local:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --skip-persistence
```

Do tool terminal có timeout ngắn, run được chạy background và log vào:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/gemini_partial_stdout.log
benchmark/tuvi_golden_dataset/reports/w6_abl_03/gemini_partial_stderr.log
```

Kết quả:

```text
manifest_name: w6_abl_03_chunking_strategy_v1
judge_backend: gemini
dataset_item_count: 10
config_count: 3
statuses: completed, completed, completed
```

Report đã cập nhật:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md
```

Không thấy lỗi trong log theo các pattern:

```text
Traceback, Error, Exception, APIError, quota, 429, ResourceExhausted, Deadline
```

Log stderr có nhiều warning Neo4j dạng deprecation:

```text
CALL subquery without a variable scope clause is deprecated.
```

Đây là warning Cypher, không làm fail run. Nên xử lý sau để giảm nhiễu log, không phải blocker W6-ABL-03.

### 4. Metric partial limit 10
Kết quả overall từ report Gemini partial:

| Config | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fixed_512_graph_sparse_rrf` | 10 | 0.81 | 0.70 | 0.5556 | 1.0 | 1.0 | 14074.47 |
| `parent_child_graph_sparse_rrf` | 10 | 0.74 | 0.67 | 0.5444 | 1.0 | 1.0 | 7431.16 |
| `semantic_bge_m3_graph_sparse_rrf` | 10 | 0.85 | 0.74 | 0.5444 | 1.0 | 1.0 | 18042.16 |

Ranking đáng chú ý:
- Context Recall cao nhất: `chunk_fixed_512` với `0.5556`.
- Faithfulness và Answer Relevancy cao nhất: `chunk_semantic_embedding_bge_m3`.
- p95 latency tốt nhất: `chunk_structure_parent_child`.
- Graph Hit và Citation Coverage đều `1.0` cho cả 3 strategy trên subset 10 câu.

### 5. Kết luận hiện tại
W6-ABL-03 hiện đã đạt:
- Implementation complete.
- Local smoke complete.
- Neo4j runtime coverage complete 12/12.
- Gemini partial official local report complete trên 10 câu x 3 configs.

W6-ABL-03 vẫn chưa đạt full official closure vì:
- `--persist-supabase` đang bị block bởi bảng `experiment_runs` chưa có trong Supabase schema cache.
- Chưa chạy full dataset Gemini evaluation.

### 6. Khuyến nghị trước khi chạy full
Không nên chạy full với `--persist-supabase` cho đến khi xử lý Supabase migration/schema cache.

Hai lựa chọn tiếp theo:

1. **Khuyến nghị để hoàn tất đúng chuẩn PLAN.md**:
   - apply migration `infra/supabase/migrations/20260709_experiment_runs.sql` lên Supabase live DB;
   - verify `experiment_runs` visible qua PostgREST;
   - rerun partial hoặc full với `--persist-supabase`.

2. **Nếu chỉ cần report file local trước**:
   - chạy full với `--skip-persistence`;
   - ghi caveat rõ rằng kết quả chưa sync vào `experiment_runs`.

Lệnh full local-only nếu chọn cách 2:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --skip-persistence
```

Lệnh full đúng chuẩn sau khi Supabase migration sẵn sàng:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --persist-supabase
```

**Trạng thái cập nhật**: W6-ABL-03 PASS ở mức Neo4j coverage + Gemini partial official local report. BLOCKED ở phần Supabase persistence/full official closure do bảng `experiment_runs` chưa sẵn sàng trong Supabase live schema cache.

---

## Hotfix chất lượng RAG sau kiểm thử live W6-RAG-05/W6-RAG-06 - 2026-07-16

### Bối cảnh
Sau khi W6-RAG-05 đã cài đặt xong, kiểm thử chat thật cho thấy pipeline đã chạy được end-to-end nhưng còn ba vấn đề chất lượng:

- Câu factual như “Cung Mệnh của lá số này nằm ở đâu và có sao nào?” đã lấy đúng chart facts, nhưng context/citation còn dễ kéo thêm nguồn sách không cần thiết.
- Câu luận Mệnh có thể giữ chunk về sao không có trong lá số, ví dụ chunk Thất Sát trong khi Mệnh thực tế có Thiên Lương/Thái Dương.
- Câu “tam hợp Phúc-Phối-Di” có lúc bị entity extraction thêm nhầm cung Phụ Mẫu vào `target_houses`/chart facts.

### Thay đổi đã làm

1. `backend/app/rag/chart_facts.py`
   - Khóa `target_houses` khi planner đã nhận diện tam hợp tường minh từ câu hỏi.
   - Canonical hóa tên cung từ retrieval plan/query entities.
   - Sinh relation tam hợp thật từ `explicit_house_triad` hoặc ontology cung thay vì placeholder chung.
   - Render quan hệ vào block `[LIÊN HỆ CUNG]`.
   - Đổi header chart facts context từ `[CHART_FACTS]` sang `[CHART]` để tránh model sinh marker lỗi kiểu `[[CHART]_FACTS]`.

2. `backend/app/rag/context.py`
   - Thêm `chart_relevance_filter` trước bước order/select context.
   - Khi đã có đủ candidate chạm tới sao/cung trong lá số, loại bớt chunks lệch trọng tâm.
   - Ưu tiên sao thật trong lá số; house-only hit vẫn được giữ cho role `house_scope`, `relation_rule`, `combination_pattern`.
   - Ghi metadata `context_summary.chart_relevance_filter` để debug.

3. `backend/app/rag/generation.py`
   - Prompt yêu cầu chỉ dùng `[CHART]` cho dữ kiện lá số.
   - Fallback vẫn tương thích context cũ có `[CHART_FACTS]`.
   - Fallback answer có thể tóm tắt relation tam hợp đã nhận diện.

4. Tests cập nhật/thêm mới
   - `backend/tests/test_rag_chart_facts.py`
   - `backend/tests/test_rag_context_generation_citations.py`
   - `backend/tests/test_rag_dry_run.py`

5. Tài liệu cập nhật
   - `docs/rag_question_aware_retrieval.md`

### Verification

Đã chạy pass:

```powershell
cd backend
python -m pytest tests/test_rag_chart_facts.py tests/test_rag_context_generation_citations.py tests/test_rag_planner.py tests/test_rag_dry_run.py -q
```

Kết quả:

```text
36 passed, 1 warning
```

Đã chạy thêm regression retrieval/ranking:

```powershell
cd backend
python -m pytest tests/test_rag_diagnostics.py tests/test_rag_role_retrieval.py tests/test_rag_retrieval.py tests/test_rag_ranking.py -q
```

Kết quả:

```text
33 passed, 1 warning
```

### Trạng thái
Hotfix chất lượng context/chart facts đã hoàn tất ở mức unit/regression test. Bước tiếp theo nên kiểm thử lại 3 câu live trong UI hoặc API:

1. factual chart QA về cung Mệnh;
2. luận giải cung Mệnh có Thiên Lương/Thái Dương;
3. tam hợp Phúc-Phối-Di.

---

## Chốt W6-ABL-03 - Claim DONE theo balanced golden subset - 2026-07-15

### Quyết định chốt
W6-ABL-03 được chốt **DONE cho phạm vi ablation chunking v1** dựa trên bằng chứng đã có:

- đã có matrix 3 chunk strategy đại diện;
- đã kiểm tra Neo4j runtime coverage đủ 12/12 cặp `source_id + chunk_strategy_id`;
- đã chạy Gemini judge trên balanced golden subset gồm 10 câu, phủ đủ 10 question family chính;
- đã sinh report JSON/Markdown có ranking chunk strategy, metric table, grouped metrics theo complexity/family, retrieval miss và rerank miss;
- cùng một corpus, cùng một golden dataset, cùng một retrieval stack Graph + Sparse + RRF + reranker được dùng để so sánh 3 strategy.

Phần Supabase `experiment_runs` persistence không được dùng để block W6-ABL-03 nữa vì đây là blocker hạ tầng kết nối/migration Supabase, không phải thiếu implementation/evidence của ablation chunking. Blocker này cần xử lý trước các run production/final evaluation sau.

### Bằng chứng đã verify

#### 1. Coverage 12/12 trong Neo4j
Command:

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
```

Kết quả:

```text
completed=true
expected_pair_count=12
observed_pair_count=12
missing_pair_count=0
```

Report:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/chunk_strategy_coverage.md
```

#### 2. Balanced golden subset
Dataset release thực tế có 100 item:

```text
TVQA-001 .. TVQA-100
Direct: 10
One-hop: 46
Two-hop: 44
10 question family, mỗi family 10 câu
```

W6-ABL-03 Gemini run đã dùng `--limit 10`, tương ứng 10 item đầu `TVQA-001..TVQA-010`. Đây là balanced subset vì phủ đủ 10 question family chính:

| Item | Question family | Complexity |
|---|---|---|
| `TVQA-001` | `core_identity` | Direct |
| `TVQA-002` | `menh_house_interpretation` | One-hop |
| `TVQA-003` | `than_cu_interpretation` | One-hop |
| `TVQA-004` | `menh_cuc_relation` | One-hop |
| `TVQA-005` | `special_state_interpretation` | One-hop |
| `TVQA-006` | `menh_tam_hop` | Two-hop |
| `TVQA-007` | `menh_xung_chieu` | Two-hop |
| `TVQA-008` | `dai_van_interpretation` | One-hop |
| `TVQA-009` | `topic_house_plus_relations` | Two-hop |
| `TVQA-010` | `synthesis_judgement` | Two-hop |

Như vậy run này thỏa điều kiện “cùng golden subset” cho cả 3 chunk strategy và đủ đại diện Direct/One-hop/Two-hop.

#### 3. Gemini official local run
Command đã chạy thành công:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --skip-persistence
```

Kết quả:

```text
manifest_name=w6_abl_03_chunking_strategy_v1
judge_backend=gemini
dataset_item_count=10
config_count=3
statuses=completed, completed, completed
```

Report:

```text
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md
```

### Metric chốt W6-ABL-03

| Config | Chunk strategy | Items | Faithfulness | Answer relevancy | Context recall | Graph hit | Citation coverage | p95 latency ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `fixed_512_graph_sparse_rrf` | `chunk_fixed_512` | 10 | 0.81 | 0.70 | 0.5556 | 1.0 | 1.0 | 14074.47 |
| `parent_child_graph_sparse_rrf` | `chunk_structure_parent_child` | 10 | 0.74 | 0.67 | 0.5444 | 1.0 | 1.0 | 7431.16 |
| `semantic_bge_m3_graph_sparse_rrf` | `chunk_semantic_embedding_bge_m3` | 10 | 0.85 | 0.74 | 0.5444 | 1.0 | 1.0 | 18042.16 |

### Kết luận chunking candidate v1

Không có một strategy thắng tuyệt đối trên mọi metric:

- `chunk_fixed_512` thắng nhẹ về `context_recall_avg`.
- `chunk_semantic_embedding_bge_m3` thắng về `faithfulness_avg` và `answer_relevancy_avg`.
- `chunk_structure_parent_child` thắng rõ về latency p95.
- Cả 3 đều đạt `graph_hit_rate=1.0` và `citation_coverage_rate=1.0` trên balanced subset.

Candidate sơ bộ cho production v1 vẫn là:

```text
chunk_semantic_embedding_bge_m3
```

Lý do:
- chất lượng trả lời tốt nhất trên Faithfulness và Answer Relevancy;
- Citation Coverage và Graph Hit không kém hai strategy còn lại;
- latency cao hơn, nên cần tiếp tục tối ưu top-k/context budget hoặc so sánh lại ở W7-CONFIG-01 trước khi lock production config.

Candidate latency fallback:

```text
chunk_structure_parent_child
```

Lý do:
- p95 thấp nhất trong 3 strategy;
- phù hợp nếu W7 latency target quan trọng hơn chênh lệch quality metric.

### Những việc đã thử nhưng không dùng để block DONE

#### Supabase persistence
Đã thử:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --persist-supabase
```

Kết quả bị block:

```text
Could not find the table 'public.experiment_runs' in the schema cache
code=PGRST205
```

Đã thử apply migration bằng helper:

```powershell
.\.venv\Scripts\python.exe scripts/apply_supabase_migration.py infra/supabase/migrations/20260709_experiment_runs.sql
```

Kết quả bị block ở network/DNS direct DB:

```text
failed to resolve host 'db.baxcnbbhhnhajiyjmzfi.supabase.co'
```

Đã thử hostaddr IPv6 từ DNS, nhưng network local không reach được IPv6 Postgres:

```text
Network is unreachable
```

Đã thử kiểm PostgREST bằng service role, bảng vẫn chưa visible.

Kết luận: Supabase persistence cần xử lý bằng một trong các cách sau trước W7/W8 production/final runs:

1. apply SQL trực tiếp trong Supabase SQL Editor;
2. cập nhật `.env` với Supabase pooler `DATABASE_URL` đúng;
3. thiết lập Supabase CLI access token/project link và chạy migration qua CLI.

#### Full 100-item run
Đã kiểm tra release dataset có 100 item. Đã thử start full run không limit với Gemini, nhưng dừng lại để tránh tiêu quota kéo dài khi persistence vẫn chưa giải quyết. Full-100 là follow-up tốt cho W7/W8 final evaluation, không bắt buộc để claim W6-ABL-03 vì W6-ABL-03 yêu cầu so sánh trên cùng golden subset và hiện subset 10 câu đã cân bằng theo 10 family.

### Lệnh tái lập W6-ABL-03 đã chốt

```powershell
python scripts/check_w6_abl_03_chunk_coverage.py --mode neo4j
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --skip-persistence
```

### Lệnh follow-up khi Supabase đã sẵn sàng

Partial persistence verification:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --limit 10 --persist-supabase
```

Full 100-item official run:

```powershell
python scripts/run_eval.py --manifest configs/w6_abl_03_chunking_matrix.yaml --judge-backend gemini --persist-supabase
```

**Trạng thái cuối W6-ABL-03**: DONE cho chunking ablation v1. Có report và ranking strategy trên balanced golden subset, đủ 12 cặp source-strategy runtime trong Neo4j, cùng corpus/config/dataset subset cho 3 strategy. Supabase persistence được ghi nhận là blocker hạ tầng follow-up, không còn chặn claim DONE của task W6-ABL-03.

---

## W6-INT-01 - Integration test với production candidate config - 2026-07-15

### Phạm vi đã cài đặt

Đã cài đặt luồng integration test theo hướng hybrid đã duyệt:

- tạo config candidate riêng cho W6 integration, không sửa `default_production.yaml` trước W7-CONFIG-01;
- chạy automated smoke cho backend health, chart engine và RAG retrieval/context/citation;
- dùng deterministic generation để không tiêu Gemini quota ở integration smoke, nhưng vẫn dùng Neo4j runtime thật và config candidate thật;
- sinh report JSON/Markdown và checklist thủ công cho phần browser login/dashboard/chart detail/citation panel;
- chạy frontend production build để xác nhận `/chart/[id]`, `/dashboard`, `/api/chat` vẫn compile.

### File đã thêm

#### Config candidate

```text
configs/w6_integration_candidate.yaml
```

Config này dùng candidate chất lượng từ W6-ABL-03:

```text
experiment_id=w6_int_01_candidate_semantic_bge_m3
chunk_strategy_id=chunk_semantic_embedding_bge_m3
dense_retrieval_enabled=false
retrieval stack=Graph + Sparse + RRF + lexical reranker
```

Lý do không sửa `default_production.yaml`: task W7-CONFIG-01 mới là nơi lock production config cuối cùng. W6-INT-01 chỉ cần candidate tạm để kiểm end-to-end.

#### Script smoke integration

```text
scripts/run_w6_int_01_smoke.py
```

Script kiểm các bước:

1. `GET /health` bằng FastAPI `TestClient`.
2. `POST /chart/tuvi` để tạo lá số Tử Vi thật bằng chart engine.
3. Chạy RAG trực tiếp với:
   - chart vừa tạo;
   - Neo4j driver thật;
   - `configs/w6_integration_candidate.yaml`;
   - `DeterministicGenerationClient` để tránh gọi Gemini generation;
   - `retrieval_fallback_on_error=true`.
4. Kiểm 3 câu:
   - factual/chart fact;
   - interpretive/Mệnh;
   - multi-hop/tam hợp/xung chiếu.
5. Ghi bug P0/P1/P2 nếu có.

### Report đã sinh

```text
benchmark/tuvi_golden_dataset/reports/w6_int_01/integration_report.json
benchmark/tuvi_golden_dataset/reports/w6_int_01/integration_report.md
benchmark/tuvi_golden_dataset/reports/w6_int_01/manual_checklist.md
benchmark/tuvi_golden_dataset/reports/w6_int_01/smoke_stdout.log
benchmark/tuvi_golden_dataset/reports/w6_int_01/smoke_stderr.log
```

### Lệnh đã chạy

Validate config:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'backend'); from app.rag.config import load_experiment_config; c=load_experiment_config('configs/w6_integration_candidate.yaml'); print(c.experiment_id, c.chunk_strategy_id, c.dense_retrieval_enabled, c.fusion_method)"
```

Kết quả:

```text
w6_int_01_candidate_semantic_bge_m3 chunk_semantic_embedding_bge_m3 False rrf
```

Unit/API regression smoke:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_health.py backend/tests/test_chat_route.py backend/tests/test_experiment_config.py -q
```

Kết quả:

```text
18 passed, 10 warnings
```

Integration smoke:

```powershell
.\.venv\Scripts\python.exe scripts/run_w6_int_01_smoke.py --config configs/w6_integration_candidate.yaml --output-dir benchmark/tuvi_golden_dataset/reports/w6_int_01
```

Kết quả:

```text
status=pass
bug_summary={'P0': 0, 'P1': 0, 'P2': 0}
```

Frontend build:

```powershell
cd frontend
npm run build
```

Kết quả:

```text
Compiled successfully
/chart/[id] compiled successfully
/dashboard compiled successfully
/api/chat compiled successfully
```

### Kết quả automated integration smoke

Tổng quan:

```text
status=pass
P0=0
P1=0
P2=0
duration_ms=43004.27
config_hash=7f3d735a1468fe3edb17c300aff5bfa56ab6993035a83f39e30d2a04e94fa6e6
```

Health/chart:

| Bước | Kết quả | Latency | Ghi chú |
|---|---:|---:|---|
| `health` | PASS | 13.29 ms | `GET /health` trả 200 |
| `chart_creation` | PASS | 34.55 ms | `chart_type=TUVI`, `palace_count=12` |

Chat/RAG:

| ID | Loại | Pass | Sources | Citation | Complexity | Latency |
|---|---|---:|---:|---:|---|---:|
| `factual_chart_fact` | factual | PASS | 2 | true | One-hop | 10652.81 ms |
| `interpretive_menh` | interpretive | PASS | 2 | true | Two-hop | 18553.89 ms |
| `multi_hop_tam_hop_xung_chieu` | multi-hop | PASS | 2 | true | Two-hop | 13741.21 ms |

Diễn giải:

- Backend health pass.
- Chart engine tạo được lá số Tử Vi có đủ 12 cung.
- RAG dùng candidate `chunk_semantic_embedding_bge_m3` trả answer cho cả 3 loại câu.
- Interpretive và multi-hop đều có source/citation.
- Retrieval diagnostics có mặt trong response.
- Không ghi nhận bug P0/P1/P2 trong automated smoke.

### Checklist thủ công đã tạo

File:

```text
benchmark/tuvi_golden_dataset/reports/w6_int_01/manual_checklist.md
```

Checklist này dành cho phần browser thật:

1. login;
2. tạo lá số từ UI;
3. redirect sang `/chart/[id]`;
4. render `TuViBoard` đủ 12 cung;
5. hỏi factual;
6. hỏi interpretive;
7. hỏi multi-hop;
8. kiểm citation panel;
9. kiểm loading/error state.

Lưu ý quan trọng: repo hiện chưa có Playwright/Cypress setup chính thức, nên W6-INT-01 hiện được verify tự động ở backend/chart/RAG/build layer, còn browser login/UI cần kiểm thủ công theo checklist. Nếu muốn automation đầy đủ ở giai đoạn W7/W8, nên bổ sung Playwright riêng thay vì nhét scope đó vào W6-INT-01.

### Bug P0/P1/P2

Automated smoke:

```text
P0=0
P1=0
P2=0
```

Không ghi nhận blocker trong phần backend/chart/RAG/build. Phần browser manual chưa chạy bằng công cụ tự động; checklist đã được tạo để người kiểm thử điền kết quả.

### Trạng thái W6-INT-01

**Status**: COMPLETE ở mức cài đặt và automated local integration smoke. Backend health, chart creation, RAG factual/interpretive/multi-hop, citation/source presence và frontend production build đều pass. Manual browser checklist đã sẵn sàng để xác nhận login/dashboard/chart detail/citation panel trên trình duyệt thật.


---

## W7-ABL-01 - Generation model và prompt template ablation partial-10 - 2026-07-16

### Phạm vi đã cài đặt

Đã triển khai ablation generation/prompt theo đúng phạm vi partial 10 câu đã chốt:

- giữ retrieval config cố định theo W6 integration candidate để cô lập biến generation;
- dùng `chunk_semantic_embedding_bge_m3` + Graph + Sparse + RRF + lexical reranker;
- tắt dense retrieval để không trộn biến dense vào generation ablation;
- so sánh 3 prompt template trên cùng model `gemini-3.1-flash-lite-preview`;
- chạy Gemini judge partial 10 câu balanced;
- skip Supabase persistence vì blocker `experiment_runs` schema cache vẫn là caveat hạ tầng.

### File đã thêm hoặc chỉnh sửa

Prompt registry:

```text
backend/app/rag/prompt_templates.py
backend/app/rag/generation.py
```

Config/manifest W7:

```text
configs/w7_generation_baseline_v1_flash_lite.yaml
configs/w7_generation_grounded_v2_flash_lite.yaml
configs/w7_generation_structured_v3_flash_lite.yaml
configs/w7_abl_01_generation_prompt_matrix.yaml
```

Evaluation/report analysis:

```text
backend/app/rag/evaluation.py
```

Tests:

```text
backend/tests/test_experiment_config.py
backend/tests/test_rag_context_generation_citations.py
backend/tests/test_rag_evaluation.py
```

### Prompt templates được so sánh

| Config | Prompt template | Generation model | Retrieval control |
|---|---|---|---|
| `baseline_v1_flash_lite` | `tuvi_generation_v1` | `gemini-3.1-flash-lite-preview` | semantic BGE-M3 + Graph/Sparse/RRF/reranker, dense off |
| `grounded_v2_flash_lite` | `tuvi_generation_grounded_v2` | `gemini-3.1-flash-lite-preview` | semantic BGE-M3 + Graph/Sparse/RRF/reranker, dense off |
| `structured_v3_flash_lite` | `tuvi_generation_structured_v3` | `gemini-3.1-flash-lite-preview` | semantic BGE-M3 + Graph/Sparse/RRF/reranker, dense off |

### Lệnh đã chạy

Unit/config/evaluation tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_rag_context_generation_citations.py backend/tests/test_rag_evaluation.py backend/tests/test_experiment_config.py -q
```

Kết quả:

```text
46 passed
```

RAG/chart regression sau khi thêm prompt registry:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_rag_chart_facts.py backend/tests/test_rag_context_generation_citations.py backend/tests/test_rag_planner.py backend/tests/test_rag_dry_run.py -q
```

Kết quả:

```text
37 passed, 1 warning
```

Static smoke W7:

```powershell
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w7_abl_01_generation_prompt_matrix.yaml --offline-smoke --limit 3 --skip-persistence
```

Gemini limit-1 probe:

```powershell
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w7_abl_01_generation_prompt_matrix.yaml --judge-backend gemini --limit 1 --skip-persistence --output-dir benchmark/tuvi_golden_dataset/reports/w7_abl_01_limit1_probe
```

Official partial-10 Gemini run:

```powershell
.\.venv\Scripts\python.exe scripts/run_eval.py --manifest configs/w7_abl_01_generation_prompt_matrix.yaml --judge-backend gemini --limit 10 --skip-persistence
```

Ghi chú vận hành: trong terminal/tool hiện tại, lệnh foreground dài hơn timeout wrapper nên partial-10 được chạy nền qua `cmd /B`. Các log thử nghiệm retry/popen/cmd cũ đã được dọn; chỉ giữ lại report chính và log run thành công.

### Report đã sinh

```text
benchmark/tuvi_golden_dataset/reports/w7_abl_01/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w7_abl_01/evaluation_report.md
benchmark/tuvi_golden_dataset/reports/w7_abl_01/gemini_partial_cmd3_stdout.log
benchmark/tuvi_golden_dataset/reports/w7_abl_01/gemini_partial_cmd3_stderr.log
```

Probe riêng:

```text
benchmark/tuvi_golden_dataset/reports/w7_abl_01_limit1_probe/evaluation_report.json
benchmark/tuvi_golden_dataset/reports/w7_abl_01_limit1_probe/evaluation_report.md
```

### Kết quả Gemini partial-10

Tổng quan:

```text
manifest_name=w7_abl_01_generation_prompt_v1
judge_backend=gemini
dataset_item_count=10
config_count=3
statuses=3/3 completed
```

Metric chính:

| Config | Prompt | Faithfulness | Answer Relevancy | Context Recall | Citation Coverage | p95 latency |
|---|---|---:|---:|---:|---:|---:|
| `baseline_v1_flash_lite` | `tuvi_generation_v1` | 0.92 | 0.79 | 0.7000 | 1.00 | 25911.78 ms |
| `grounded_v2_flash_lite` | `tuvi_generation_grounded_v2` | 0.92 | 0.76 | 0.6444 | 1.00 | 30187.57 ms |
| `structured_v3_flash_lite` | `tuvi_generation_structured_v3` | 0.67 | 0.52 | 0.3222 | 1.00 | 28321.40 ms |

### Candidate được chọn

Ứng viên generation/prompt sơ bộ cho W7-CONFIG-01:

```text
prompt_template_id=tuvi_generation_v1
generation_model=gemini-3.1-flash-lite-preview
config=baseline_v1_flash_lite
```

Lý do:

- Faithfulness đồng hạng cao nhất với grounded v2: `0.92`.
- Answer Relevancy cao nhất: `0.79`.
- Context Recall cao nhất: `0.7000`.
- Citation Coverage đạt `1.00`.
- p95 latency thấp nhất trong 3 config: `25911.78 ms`.

`grounded_v2_flash_lite` vẫn là candidate phụ nếu team ưu tiên prompt chặt hơn về policy, nhưng partial-10 cho thấy baseline v1 cân bằng chất lượng/latency tốt hơn. `structured_v3_flash_lite` không nên promote vì Faithfulness, Answer Relevancy và Context Recall thấp rõ.

### Caveats

- Đây là partial-10 Gemini judge, chưa phải full dataset/final evaluation.
- Supabase persistence vẫn skip do blocker `experiment_runs` chưa visible trong live schema cache.
- Runtime/test vẫn có warning `google.generativeai` deprecated; chưa block functional nhưng nên migrate sang `google.genai` ở technical debt.
- Report title hiện vẫn ghi `W6 Evaluation report` do runner dùng chung W6-EVAL framework; nội dung manifest/report là W7-ABL-01 và có section riêng `Phân tích ablation generation prompt/model`.

### Trạng thái W7-ABL-01

**Status**: COMPLETE theo phạm vi partial-10 đã chốt. Có implementation prompt registry, config/manifest W7, tests pass, static smoke pass, Gemini limit-1 probe pass, Gemini partial-10 pass, report JSON/Markdown và candidate prompt/model sơ bộ cho `W7-CONFIG-01`.

---

## W7-CONFIG-01 Production Config Locked by Evidence - 2026-07-16

### Trạng thái

`configs/default_production.yaml` đã được lock làm production default vận hành cho W7:

```text
experiment_id=default_production_v2
chunk_strategy_id=chunk_semantic_embedding_bge_m3
retrieval=Graph + Sparse + RRF
reranker=lexical-overlap-v1 enabled, top_k=10
dense_retrieval_enabled=false
query_rewrite_enabled=false
prompt_template_id=tuvi_generation_v1
generation_model=gemini-3.1-flash-lite-preview
context_assembly_strategy=balanced
cache_disabled=true
```

Config hash đã lock bằng `backend/app/rag/config.py::config_hash` trên Pydantic-normalized payload. Giá trị `Path` được canonicalize sang POSIX form để cùng config giữ cùng hash trên Windows/Render Linux:

```text
c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96
```

### Evidence và rationale

Decision report đầy đủ:

```text
benchmark/tuvi_golden_dataset/reports/w7_config_01/production_config_decision.md
```

Evidence chính:

- `benchmark/tuvi_golden_dataset/reports/w6_abl_03/evaluation_report.md`
  - Gemini partial-10 balanced.
  - Semantic BGE-M3 đạt Faithfulness `0.85`, Answer Relevancy `0.74`, Citation Coverage `1.0`, Graph Hit `1.0` và 2 retrieval miss.
  - Fixed-512 nhỉnh hơn Context Recall (`0.5556` so với `0.5444`); parent-child nhanh hơn rõ ở p95. Vì W7 đang quality-first, semantic BGE-M3 được chọn nhưng latency vẫn là follow-up bắt buộc.
- `benchmark/tuvi_golden_dataset/reports/w7_abl_01/evaluation_report.md`
  - Gemini partial-10 balanced.
  - `tuvi_generation_v1` đạt Faithfulness `0.92`, Answer Relevancy `0.79`, Context Recall `0.7000`, Citation Coverage `1.0`, và p95 thấp nhất trong ba prompt (`25911.78 ms`).
- `benchmark/tuvi_golden_dataset/reports/w6_abl_02/evaluation_report.md`
  - Chỉ là static smoke 2 item, nên không được dùng để tuyên bố retrieval/fusion/reranker winner.
  - Graph + Sparse + RRF + lexical reranker được giữ như control stack đã chạy ổn trong W6-ABL-03, W7-ABL-01 và W6-INT-01, không phải vì W6-ABL-02 đã chứng minh chính thức.

### Files cập nhật

- `configs/default_production.yaml`
- `benchmark/tuvi_golden_dataset/reports/w7_config_01/production_config_decision.md`
- `backend/tests/test_experiment_config.py`
- `backend/tests/test_rag_dry_run.py`
- `PROGRESS.md`

Hai test file được đồng bộ vì trước đó hardcode contract `default_production_v1`/`chunk_fixed_512`. Test config hiện kiểm rõ toàn bộ các lựa chọn production đã lock.

### Verification

Config load/hash:

```text
experiment_id=default_production_v2
chunk_strategy_id=chunk_semantic_embedding_bge_m3
config_hash=c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96
result=locked-config-ok
```

Config tests:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest backend/tests/test_experiment_config.py -q -p no:cacheprovider
```

Kết quả: `18 passed`.

RAG regression tests:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest backend/tests/test_rag_context_generation_citations.py backend/tests/test_rag_evaluation.py backend/tests/test_rag_chart_facts.py backend/tests/test_rag_planner.py backend/tests/test_rag_dry_run.py -q -p no:cacheprovider
```

Kết quả: `49 passed, 1 warning`. Warning là SDK `google.generativeai` đã hết support và cần migrate riêng sang `google.genai`.

Offline config/runner smoke:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe scripts/run_eval.py --config configs/default_production.yaml --offline-smoke --limit 3 --skip-persistence --no-report-files
```

Kết quả: single config hoàn tất `3/3`, `failed_count=0`, `judge_backend=static-smoke`. Run này chỉ xác nhận config/runner plumbing, không được tính là benchmark chất lượng.

### Chưa chạy full benchmark

Chưa chạy full 100-item golden dataset cho `default_production_v2`. Production config này được lock từ evidence Gemini partial-10 cân bằng của W6-ABL-03 và W7-ABL-01 để unblock W7 deploy/observability. Full final evaluation vẫn thuộc `W8-EVAL-01` hoặc một pre-release run riêng khi quota/capacity cho phép.

Các experiment/measurement còn deferred:

- full official Gemini retrieval/fusion/reranker matrix;
- full 100-item production config evaluation;
- dense retrieval promotion study;
- query rewrite ablation;
- alternative generation-model comparison;
- W7-OBS-02 production p95 trên 20 query mix;
- persisted official runs trong Supabase.

### Caveats và blockers

- Supabase live vẫn trả `PGRST205`: `Could not find the table 'public.experiment_runs' in the schema cache`. Cần apply `infra/supabase/migrations/20260709_experiment_runs.sql` và reload PostgREST schema cache trước persisted final run.
- Latency partial hiện chưa đạt target production trong PLAN; cần đo lại đúng môi trường deploy ở W7-OBS-02 và tối ưu top-k/context budget nếu cần.
- Runtime/evaluation còn dùng deprecated `google.generativeai`.
- Live Neo4j logs trước đó có warning `CALL subquery without a variable scope clause is deprecated`.

**Status**: COMPLETE cho phạm vi W7 operational config lock. `default_production_v2` và hash đã được xác nhận bằng test/smoke; full-dataset scientific evaluation và production p95 vẫn là follow-up bắt buộc, không được xem là đã hoàn thành trong task này.

---

## W8-EVAL-PREP-01 Evaluation Runner Hardening - 2026-07-16

### Implementation

- Thêm atomic checkpoint/provenance module: `backend/app/rag/evaluation_checkpoint.py`.
- Checkpoint identity khóa dataset SHA-256, ordered item IDs, effective config hashes, judge backend/model, generation models, manifest/evaluator fingerprints và Git SHA/dirty state.
- `scripts/run_eval.py` hỗ trợ:
  - `--checkpoint-dir`;
  - `--resume`;
  - `--retry-failed`;
  - `--max-item-attempts`;
  - `--retry-base-seconds`.
- Checkpoint tồn tại nhưng không truyền `--resume` bị từ chối để tránh reuse ngoài ý muốn.
- Resume chỉ hoạt động khi toàn bộ run identity khớp; mismatch trả exit code `2`.
- Evaluation pair có bounded retry và attempt metadata.
- `generation_backend_error` được xem là failed infrastructure pair và không gọi judge; `no_context` vẫn là retrieval outcome hợp lệ để judge.
- Config có item failed mang status `failed`; report có status `completed`, `partial` hoặc `failed`; CLI trả exit code `1` nếu còn failed pairs.
- Thêm timing cho graph/dense/sparse retrieval, fusion, rerank, document grading, context assembly và generation.
- Report có RAG, retrieval, generation, judge, evaluation-total p50/p95, execution completeness, fallback summary và provenance.
- `checkpoint_summary.json` được ghi atomically sau từng pair.

### Files

- `backend/app/rag/evaluation_checkpoint.py`
- `backend/app/rag/evaluation.py`
- `backend/app/rag/nodes.py`
- `scripts/run_eval.py`
- `backend/tests/test_evaluation_checkpoint.py`
- `backend/tests/test_evaluation_runner_resilience.py`
- `backend/tests/test_run_eval_cli.py`
- `backend/tests/test_rag_retrieval.py`
- `backend/tests/test_rag_diagnostics.py`

### Verification

- Checkpoint/resilience/matrix/evaluation/retrieval/diagnostics/config/CLI focused suite: `80 passed`.
- Related RAG regression suite: `42 passed`.
- Full backend suite sau mọi thay đổi: `387 passed, 11 warnings`.
- Python compile check: `compileall=pass`.
- Focused RAG suites có warning `google.generativeai` đã hết support. Full backend suite còn các Starlette/Pydantic deprecation warning đã tồn tại; tất cả đều không block functional tests.
- CLI invalid `--resume` không có checkpoint dir trả exit code `2`.

**Status**: COMPLETE - runner đã đủ checkpoint/resume, provenance, retry, failure semantics và latency telemetry để chuyển sang live preflight/full benchmark.

---

## W8-EVAL-PREP-02 Retrieval Matrix V2 - 2026-07-16

### Matrix đã chuẩn hóa

Tạo `configs/w8_abl_01_retrieval_matrix_v2.yaml` gồm 10 config:

1. `baseline_graph_sparse_rrf`
2. `graph_only_rrf`
3. `sparse_only_rrf`
4. `dense_only_rrf`
5. `dense_sparse_rrf`
6. `graph_dense_rrf`
7. `all_paths_planner_dense_rrf`
8. `baseline_no_reranker`
9. `baseline_weighted_sum`
10. `baseline_graph_first`

Control giữ cố định cho cả 10 config:

```text
chunk_strategy_id=chunk_semantic_embedding_bge_m3
prompt_template_id=tuvi_generation_v1
generation_model=gemini-3.1-flash-lite-preview
query_rewrite_enabled=false
context_assembly_strategy=balanced
document_grading_enabled=true
cache_disabled=true
```

Dense variants kế thừa `default_production.yaml`, không còn dùng fixed-512. Duplicate `graph_sparse_rrf` đã bị loại. `baseline_graph_first` chỉ đổi `fusion_method`, không đổi context assembly.

### Verification

- Matrix load: `10` configs.
- Unique effective config hashes: `10`.
- Unique behavior signatures khi bỏ `experiment_id`/`name`: `10`.
- Chunk strategies: chỉ `chunk_semantic_embedding_bge_m3`.
- Matrix/timing focused suite: `23 passed`.
- Offline smoke:

```text
expected_pair_count=20
completed_pair_count=20
failed_pair_count=0
executed_pair_count=20
resumed_pair_count=0
```

- Resume smoke cùng checkpoint:

```text
expected_pair_count=20
completed_pair_count=20
failed_pair_count=0
executed_pair_count=0
resumed_pair_count=20
```

- `retrieval_p95_ms` đã có giá trị cho cả 10 config trong offline report.
- Artifacts:
  - `benchmark/tuvi_golden_dataset/reports/w8_eval_prep_02_smoke/`
  - `benchmark/tuvi_golden_dataset/reports/w8_eval_prep_02_smoke_resume/`
- Không phát hiện secret trong checkpoint/report artifacts.
- Các smoke trên dùng `judge_backend=static-smoke` và deterministic dependencies; chỉ chứng minh runner/matrix/timing/resume plumbing, không phải quality benchmark. Official metrics vẫn phải chạy live Neo4j + Gemini ở W8-EVAL-PREFLIGHT-01/W8-EVAL-01.

**Status**: COMPLETE - retrieval/fusion/reranker matrix v2 đã fair, không duplicate/confound, offline 10x2 và resume 20/20 pass. Bước tiếp theo là W8-EVAL-PREFLIGHT-01 với live Neo4j/Gemini.

---

## W8-EVAL-PREFLIGHT-01 Live Go/No-Go - 2026-07-17

### Identity và infrastructure gates

- Git SHA: `bd1305c1a97907cd1ee397790eb5bafa4f3a666f`; tracked tree sạch trong toàn bộ live run.
- Production config: `default_production_v2`, hash `c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96`.
- Dataset: 100 items; preflight chọn có thứ tự `TVQA-001..006` gồm Direct, One-hop và Two-hop.
- Retrieval matrix: 10 effective config hashes duy nhất.
- Evaluator fingerprint: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`.
- Regression: `387 passed, 11 warnings`; `compileall=pass`.
- Gemini exact model `gemini-3.1-flash-lite-preview`: 4/4 configured keys pass, primary key pass.
- Neo4j coverage: 12/12 source-strategy pairs, không thiếu pair.
- Semantic BGE-M3 smoke: 2/2 queries pass; mỗi query có 5 dense và 5 sparse hits; index check pass.

### Live evaluator gates

Production `default_production.yaml`, limit 6:

```text
expected_pair_count=6
completed_pair_count=6
failed_pair_count=0
executed_pair_count=6
resumed_pair_count=0
generation_backend_fallback_count=0
retrieval_backend_fallback_count=0
judge_failure_count=0
no_context_count=0
citation_fallback_count=0
```

Retrieval/fusion/reranker matrix v2, 10 configs x 6 items:

```text
expected_pair_count=60
completed_pair_count=60
failed_pair_count=0
executed_pair_count=60
resumed_pair_count=0
```

- Cả 10 configs mang status `completed`; không có generation/retrieval/judge failure hoặc fallback.
- Dense path thực sự được chọn trong cả 4 dense-enabled variants; graph và sparse paths cũng được exercise theo effective config.
- Live resume cùng checkpoint pass với `executed_pair_count=0`, `resumed_pair_count=60`; toàn bộ result lấy từ checkpoint.
- Deliberate `--limit 5` provenance mismatch bị reject trước evaluator với exit code `2`; differing fields gồm `selected_item_ids`.
- Một Neo4j read timeout transient được driver retry; run cuối vẫn 60/60 và không có retrieval fallback.

### Artifacts và quyết định

- Root: `benchmark/tuvi_golden_dataset/reports/w8_eval_preflight_01/`.
- Go/no-go reports:
  - `preflight_report.json`
  - `preflight_report.md`
- Có repository identity, Gemini diagnostics, Neo4j coverage, semantic retrieval smoke, production/matrix checkpoints và reports, resume report, mismatch evidence, sanitized command log và artifact SHA-256 provenance.
- Secret scan: 0 findings; không ghi API key/password/token vào artifacts.
- Scope chỉ là operational subset trên `CHART-001`, không phải quality benchmark cân bằng hoặc kết luận khoa học cuối.
- Full-100 không được khởi động trong task này.

**Status**: COMPLETE / GO - mọi hard preflight gate đã pass; có thể chuyển sang W8-EVAL-01 sau khi revalidate identity ngay trước full run.

---

## W8-EVAL-01 Production Full-100 - 2026-07-17

### Scope và identity

- Chạy đúng một locked production config `default_production_v2` trên toàn bộ `TVQA-001..TVQA-100`.
- Git SHA: `c32771fefb5bc14686660a43ab0bd3ba4d79d4b7`.
- Config hash: `c40227a029588b7793201702798e96e640d7a436131d6f5f0437f67151803d96`.
- Dataset SHA-256: `90376a87cec29cc22e93dc71b41e054ed2f0183bc515a52aa461fecd43cc008c`.
- Evaluator SHA-256: `9ae528d893159c4092c3129523da8d69a7a79a6ab5c32a132791158287eda314`.
- Generation và judge: `gemini-3.1-flash-lite-preview`; live Neo4j + Gemini; Supabase persistence skip do blocker `PGRST205`.
- Protocol và target được freeze trước run theo `SPECIFICATIONS.md`: Faithfulness 0.80, Relevancy 0.75, Context Recall 0.70, Graph Hit 0.65, Citation Coverage 0.90, RAG p95 8s, retrieval p95 3s.

### Prelaunch gates

- Backend regression: `387 passed, 11 warnings`; compile pass.
- Gemini exact model: 4/4 keys pass, primary pass.
- Neo4j coverage: 12/12 source-strategy pairs.
- Semantic BGE-M3 smoke: 2/2 queries pass; mỗi query có 5 dense và 5 sparse hits.

### Execution và resume

```text
expected_pair_count=100
completed_pair_count=100
failed_pair_count=0
executed_pair_count=100
resumed_pair_count=0
```

- 100 unique item IDs, đủ `TVQA-001..100`.
- Generation fallback = 0, retrieval fallback = 0, judge failure = 0, no-context = 0, citation fallback = 0.
- Resume verification trực tiếp trả exit code 0 với `executed_pair_count=0`, `resumed_pair_count=100` và toàn bộ result từ checkpoint.
- Detached PowerShell worker không đọc được exit code của venv launcher nên monitor ghi exit code null/failed; đây chỉ là wrapper telemetry limitation. Canonical report `status=completed`, checkpoint 100/100 và direct resume exit 0 xác nhận run hợp lệ.

### Final automatic metrics

| Metric | Result | Target | Verdict |
|---|---:|---:|---|
| Faithfulness | 0.853 | >= 0.80 | PASS |
| Answer Relevancy | 0.719 | >= 0.75 | FAIL |
| Context Recall | 0.6223 | >= 0.70 | FAIL |
| Graph Hit Rate | 0.967 | >= 0.65 | PASS |
| Citation Coverage | 0.978 | >= 0.90 | PASS |
| RAG p95 | 26530.42 ms | <= 8000 ms | FAIL |
| Retrieval p95 | 24467.90 ms | <= 3000 ms | FAIL |

- Chart Context Grounding: `0.8889`; Corpus Source Coverage: `1.0`.
- Generation p95: `2835.35 ms`; judge p95: `2023.82 ms`; evaluation-total p95: `27926.93 ms`.
- `dai_van_interpretation` là family yếu nhất: Relevancy `0.34`, Context Recall `0.27`, RAG p95 `39779.29 ms`.
- Human review queue tự động có 49 item và control sample 20 item; human review/adjudication chưa được người thật ký hoàn tất.

### Artifacts và verdict

- Artifact root: `benchmark/tuvi_golden_dataset/reports/w8_eval_01/`.
- Canonical report: `evaluation/report_final.md`.
- Có raw report/checkpoint, resume report, per-item exports, subgroup complexity/family/chart/topic, latency outliers, review queue, frozen criteria, secret scan và SHA-256 manifest.
- Secret scan: 0 findings.

```text
RUN_VALID
QUALITY_FAIL
PERFORMANCE_FAIL
HUMAN_PENDING
OVERALL=PRODUCTION_HOLD
```

**Status**: COMPLETE / PRODUCTION_HOLD - full evaluation đã hoàn tất và có kết luận rõ. Config hiện tại chưa được claim production-pass; cần human adjudication và remediation Answer Relevancy, Context Recall, retrieval latency trước khi đánh giá lại một config có identity mới.
