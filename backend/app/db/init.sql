-- Initialize database with extensions and initial data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for text search
CREATE INDEX IF NOT EXISTS idx_charging_sessions_text_search 
ON charging_sessions USING gin(to_tsvector('english', 
    coalesce(vehicle_model, '') || ' ' || 
    coalesce(charging_station_location, '') || ' ' || 
    coalesce(user_type, '')
));

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_charging_sessions_updated_at 
    BEFORE UPDATE ON charging_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_charging_stations_updated_at 
    BEFORE UPDATE ON charging_stations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at 
    BEFORE UPDATE ON vehicles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_models_updated_at 
    BEFORE UPDATE ON ml_models 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
