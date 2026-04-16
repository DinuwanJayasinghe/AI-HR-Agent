-- Migration script to add GPS location columns to attendance_logs table
-- Run this in your PostgreSQL database

-- Add the new location columns
ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS check_in_latitude FLOAT;
ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS check_in_longitude FLOAT;
ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS check_out_latitude FLOAT;
ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS check_out_longitude FLOAT;

-- Drop the old location column if it exists
ALTER TABLE attendance_logs DROP COLUMN IF EXISTS location;

-- Verify the changes
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'attendance_logs'
ORDER BY ordinal_position;
