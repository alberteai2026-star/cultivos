ALTER TABLE audit_exports
  ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'solicitado' AFTER signature,
  ADD COLUMN error_message TEXT NULL AFTER status,
  ADD COLUMN completed_at DATETIME NULL AFTER error_message;

CREATE INDEX idx_audit_exports_status ON audit_exports (status);
