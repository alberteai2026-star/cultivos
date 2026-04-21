ALTER TABLE report_exports
  ADD COLUMN signed_by VARCHAR(120) NULL AFTER generated_at,
  ADD COLUMN signature_hash VARCHAR(160) NULL AFTER signed_by,
  ADD COLUMN signed_at DATETIME NULL AFTER signature_hash;

CREATE INDEX idx_report_exports_signed_at ON report_exports (signed_at);
