ALTER TABLE ai_insights
  ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'nuevo' AFTER priority,
  ADD COLUMN outcome_notes TEXT NULL AFTER status,
  ADD COLUMN resolved_at DATETIME NULL AFTER outcome_notes;

CREATE INDEX idx_ai_insights_status ON ai_insights (status);
