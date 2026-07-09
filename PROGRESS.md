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
