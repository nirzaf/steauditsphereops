-- POC-ONLY schema. These tables are disposable feasibility evidence, not
-- production DocTypes or a replacement for the R1 schema tasks.
CREATE TABLE IF NOT EXISTS scope_guard (
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  generation BIGINT UNSIGNED NOT NULL DEFAULT 0,
  revision BIGINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (client_id, period)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS poc_package (
  id CHAR(36) NOT NULL,
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  evaluated_generation BIGINT UNSIGNED NOT NULL,
  revision BIGINT UNSIGNED NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  CONSTRAINT fk_package_scope FOREIGN KEY (client_id, period)
    REFERENCES scope_guard (client_id, period)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS command_receipt (
  id CHAR(36) NOT NULL,
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  actor_id VARCHAR(140) NOT NULL,
  idempotency_key VARCHAR(180) NOT NULL,
  payload_digest CHAR(64) NOT NULL,
  result_digest CHAR(64) NULL,
  state VARCHAR(32) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_receipt_scope_actor_key (client_id, period, actor_id, idempotency_key),
  CONSTRAINT fk_receipt_scope FOREIGN KEY (client_id, period)
    REFERENCES scope_guard (client_id, period)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS poc_outbox (
  id CHAR(36) NOT NULL,
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  state VARCHAR(32) NOT NULL,
  attempt INT UNSIGNED NOT NULL DEFAULT 0,
  fence BIGINT UNSIGNED NOT NULL DEFAULT 0,
  payload_digest CHAR(64) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_outbox_scope_state (client_id, period, state),
  CONSTRAINT fk_outbox_scope FOREIGN KEY (client_id, period)
    REFERENCES scope_guard (client_id, period)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS checkpoint_reference (
  id CHAR(36) NOT NULL,
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  release_identity CHAR(64) NOT NULL,
  checkpoint_identity CHAR(64) NOT NULL,
  epoch BIGINT UNSIGNED NOT NULL,
  observed_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  UNIQUE KEY uq_checkpoint_release (release_identity),
  CONSTRAINT fk_checkpoint_scope FOREIGN KEY (client_id, period)
    REFERENCES scope_guard (client_id, period)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS poc_audit_event (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  client_id VARCHAR(140) NOT NULL,
  period VARCHAR(32) NOT NULL,
  actor_id VARCHAR(140) NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  entity_id VARCHAR(140) NOT NULL,
  revision BIGINT UNSIGNED NOT NULL,
  payload_digest CHAR(64) NOT NULL,
  created_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  KEY ix_audit_scope_time (client_id, period, created_at),
  CONSTRAINT fk_audit_scope FOREIGN KEY (client_id, period)
    REFERENCES scope_guard (client_id, period)
) ENGINE=InnoDB;
