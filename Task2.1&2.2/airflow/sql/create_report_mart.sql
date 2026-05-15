CREATE TABLE IF NOT EXISTS prosthesis_report_mart
(
    report_date Date,
    user_id String,
    prosthesis_id String,
    client_name String,
    client_country String,
    telemetry_events_count UInt64,
    avg_response_ms Float64,
    max_response_ms Float64,
    avg_battery_level Float64,
    min_battery_level UInt8,
    processed_at DateTime
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (user_id, prosthesis_id, report_date);