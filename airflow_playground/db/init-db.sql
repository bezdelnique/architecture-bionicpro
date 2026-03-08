CREATE DATABASE crm;
GRANT ALL PRIVILEGES ON DATABASE crm TO airflow;

CREATE DATABASE dwh;
GRANT ALL PRIVILEGES ON DATABASE dwh TO airflow;


CREATE TABLE device_data (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    meter_id VARCHAR(255),
    device_data VARCHAR(4000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO device_data (username, meter_id, device_data, created_at)
SELECT
    'prothetic1',
    'dev1',
    'Stance flexion: ' || ROUND((15 + random() * 10)::numeric, 1) || '°, ' ||
    'Swing flexion: ' || ROUND((50 + random() * 20)::numeric, 1) || '°, ' ||
    'Extension assist: ' || CASE WHEN random() < 0.8 THEN 'optimal' ELSE 'reduced' END || ', ' ||
    'Loading response: ' || ROUND((800 + random() * 300)::numeric, 0) || 'N, ' ||
    'Battery cycles remaining: ' || (400 + (random() * 200)::int),
    CURRENT_TIMESTAMP - (INTERVAL '1 hour' * generate_series(0, 48))
FROM generate_series(1, 10);



INSERT INTO device_data (username, meter_id, device_data, created_at)
SELECT
    'prothetic2',
    'dev2',
    'Stance flexion: ' || ROUND((15 + random() * 10)::numeric, 1) || '°, ' ||
    'Swing flexion: ' || ROUND((50 + random() * 20)::numeric, 1) || '°, ' ||
    'Extension assist: ' || CASE WHEN random() < 0.8 THEN 'optimal' ELSE 'reduced' END || ', ' ||
    'Loading response: ' || ROUND((800 + random() * 300)::numeric, 0) || 'N, ' ||
    'Battery cycles remaining: ' || (400 + (random() * 200)::int),
    CURRENT_TIMESTAMP - (INTERVAL '1 hour' * generate_series(0, 48))
FROM generate_series(1, 10);



INSERT INTO device_data (username, meter_id, device_data, created_at)
SELECT
    'prothetic3',
    'dev3',
    'Stance flexion: ' || ROUND((15 + random() * 10)::numeric, 1) || '°, ' ||
    'Swing flexion: ' || ROUND((50 + random() * 20)::numeric, 1) || '°, ' ||
    'Extension assist: ' || CASE WHEN random() < 0.8 THEN 'optimal' ELSE 'reduced' END || ', ' ||
    'Loading response: ' || ROUND((800 + random() * 300)::numeric, 0) || 'N, ' ||
    'Battery cycles remaining: ' || (400 + (random() * 200)::int),
    CURRENT_TIMESTAMP - (INTERVAL '1 hour' * generate_series(0, 48))
FROM generate_series(1, 10);



INSERT INTO crm.device_data (username, meter_id, device_data, created_at)
SELECT
    'prothetic3',
    'dev4',
    'Stance flexion: ' || ROUND((15 + random() * 10)::numeric, 1) || '°, ' ||
    'Swing flexion: ' || ROUND((50 + random() * 20)::numeric, 1) || '°, ' ||
    'Extension assist: ' || CASE WHEN random() < 0.8 THEN 'optimal' ELSE 'reduced' END || ', ' ||
    'Loading response: ' || ROUND((800 + random() * 300)::numeric, 0) || 'N, ' ||
    'Battery cycles remaining: ' || (400 + (random() * 200)::int),
    CURRENT_TIMESTAMP - (INTERVAL '1 hour' * generate_series(0, 48))
FROM generate_series(1, 10);



CREATE TABLE device_data (
                             id SERIAL PRIMARY KEY,
                             username VARCHAR(255),
                             meter_id VARCHAR(255),
                             device_data VARCHAR(4000),
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

