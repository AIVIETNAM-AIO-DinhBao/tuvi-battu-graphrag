-- Archive-safe migration to enforce the Tử Vi-only MVP scope.
-- This migration intentionally refuses to delete or convert existing data.

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM la_so
    WHERE chart_system IS DISTINCT FROM 'TUVI'
  ) THEN
    RAISE EXCEPTION
      'Cannot enforce Tử Vi-only chart_system constraint: archive or remove non-TUVI rows from la_so first.';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM source_chunks
    WHERE domain IS DISTINCT FROM 'TUVI'
  ) THEN
    RAISE EXCEPTION
      'Cannot enforce Tử Vi-only source_chunks domain constraint: archive or remove non-TUVI rows first.';
  END IF;
END $$;

ALTER TABLE la_so
  ALTER COLUMN chart_system SET DEFAULT 'TUVI';

ALTER TABLE la_so
  DROP CONSTRAINT IF EXISTS la_so_chart_system_check;

ALTER TABLE la_so
  ADD CONSTRAINT la_so_chart_system_check CHECK (chart_system = 'TUVI');

ALTER TABLE la_so
  ALTER COLUMN chart_version SET DEFAULT 'tuvi-v1';

ALTER TABLE source_chunks
  ALTER COLUMN domain SET DEFAULT 'TUVI';

ALTER TABLE source_chunks
  DROP CONSTRAINT IF EXISTS source_chunks_domain_check;

ALTER TABLE source_chunks
  ADD CONSTRAINT source_chunks_domain_check CHECK (domain = 'TUVI');
