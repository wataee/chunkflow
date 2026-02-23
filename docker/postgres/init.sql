CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure vector database ready
SELECT * FROM pg_extension WHERE extname = 'vector';
