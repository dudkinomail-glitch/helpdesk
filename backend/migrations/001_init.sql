-- Base migration placeholder for production deployment via psql/alembic handoff.
CREATE TABLE IF NOT EXISTS schema_migrations (
    version varchar(50) PRIMARY KEY,
    applied_at timestamp default now()
);
INSERT INTO schema_migrations(version) VALUES ('001_init') ON CONFLICT DO NOTHING;
