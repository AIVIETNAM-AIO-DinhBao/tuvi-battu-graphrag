-- Add strategy-aware provenance fields required by W3-INGEST-05.
-- Existing rows are preserved; nullable additions are backfilled where possible.

ALTER TABLE source_chunks
  ADD COLUMN IF NOT EXISTS source_id TEXT,
  ADD COLUMN IF NOT EXISTS chunk_id TEXT,
  ADD COLUMN IF NOT EXISTS chunk_strategy_id TEXT,
  ADD COLUMN IF NOT EXISTS chunk_type TEXT,
  ADD COLUMN IF NOT EXISTS parent_id TEXT,
  ADD COLUMN IF NOT EXISTS section_id TEXT,
  ADD COLUMN IF NOT EXISTS text TEXT,
  ADD COLUMN IF NOT EXISTS provenance JSONB DEFAULT '{}'::jsonb;

ALTER TABLE source_chunks
  ALTER COLUMN source_type SET DEFAULT 'book';

UPDATE source_chunks
SET
  source_id = COALESCE(source_id, metadata->>'source_id', source_name),
  chunk_id = COALESCE(chunk_id, metadata->>'chunk_id', chunk_hash),
  chunk_strategy_id = COALESCE(chunk_strategy_id, metadata->>'chunk_strategy_id', 'unknown'),
  text = COALESCE(text, chunk_text),
  provenance = COALESCE(provenance, metadata->'provenance', '{}'::jsonb)
WHERE source_id IS NULL
   OR chunk_id IS NULL
   OR chunk_strategy_id IS NULL
   OR text IS NULL
   OR provenance IS NULL;

ALTER TABLE source_chunks
  ALTER COLUMN source_id SET NOT NULL,
  ALTER COLUMN chunk_id SET NOT NULL,
  ALTER COLUMN chunk_strategy_id SET NOT NULL,
  ALTER COLUMN text SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_source_chunks_source_id ON source_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_source_chunks_chunk_id ON source_chunks(chunk_id);
CREATE INDEX IF NOT EXISTS idx_source_chunks_strategy ON source_chunks(chunk_strategy_id);
