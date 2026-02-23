# ChunkFlow — Document Ingestion & PGVector Indexing Pipeline

[![CI](https://github.com/wataee/chunkflow/actions/workflows/ci.yml/badge.svg)](https://github.com/wataee/chunkflow/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An asynchronous ETL pipeline and REST service for ingesting unstructured documents (multi-column PDFs, DOCX, scans), extracting layout-aware elements, chunking with contextual metadata, and generating vector embeddings stored in PostgreSQL via `pgvector` with HNSW indexing.

---

## Why this exists

Many RAG implementations fail on real enterprise documents because they rely on naive fixed-size character splitting (`chunk_size=500`). When parsing complex multi-page financial reports, legal contracts, or technical manuals, naive splitters cut through tables, orphan section headers, and discard document hierarchy.

This service implements a structured ingestion workflow:
1. **Layout-aware partitioning** with `unstructured` to extract headers, narrative text, lists, and tables as discrete elements.
2. **Context-preserving chunking** that binds headings to downstream paragraph chunks so embeddings preserve topical context.
3. **PGVector HNSW indexing** (`m=16`, `ef_construction=64`) for sub-15ms approximate nearest neighbor retrieval on 1536-dimensional embeddings.
4. **Metadata filtering**: filter chunks by tenant ID, document type, ingestion date, or section tags directly in PostgreSQL.

---

## Core Pipeline Architecture

```
[Raw Document: PDF/DOCX]
         │
         ▼
[Unstructured Partitioning] ──▶ Extracts Title, NarrativeText, Table, ListItem
         │
         ▼
[Hierarchical Chunking]     ──▶ Combines small elements, binds parent section titles
         │
         ▼
[OpenAI / HuggingFace Embeddings] (1536-dim / 768-dim)
         │
         ▼
[PostgreSQL + PGVector]     ──▶ HNSW Index (Cosine Distance: `<=>`)
         │
         ▼
[Hybrid Metadata Search]    ──▶ Fast similarity search with tenant & category filters
```

---

## Quickstart

### 1. Requirements & Environment
* Docker & Docker Compose (or local PostgreSQL 16 with `pgvector` extension)
* Python 3.11+

```bash
git clone https://github.com/wataee/chunkflow.git
cd chunkflow

cp .env.example .env
# Edit .env with your OPENAI_API_KEY and database credentials
```

### 2. Run with Docker Compose
The easiest way to spin up the service along with PostgreSQL + `pgvector`:

```bash
docker compose up -d --build
```
The API is live at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

### 3. Local Development Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Run migrations / create tables
python -m app.db.init_db

# Start development server
uvicorn app.main:app --reload --port 8000
```

---

## Ingestion Example (Python SDK / HTTP)

### Ingest a Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -F "file=@annual_report_2025.pdf" \
  -F "category=financials" \
  -F "tenant_id=acme-corp"
```

Response:
```json
{
  "document_id": "doc_8f91a2c4e",
  "filename": "annual_report_2025.pdf",
  "elements_extracted": 342,
  "chunks_created": 84,
  "status": "indexed",
  "duration_seconds": 3.42
}
```

### Similarity Query with Metadata Filtering
```bash
curl -X POST "http://localhost:8000/api/v1/search/similarity" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was the EBITDA margin in Q3?",
    "top_k": 3,
    "filters": {
      "tenant_id": "acme-corp",
      "category": "financials"
    }
  }'
```

---

## PGVector Indexing Configuration

By default, tables are created with an HNSW index using cosine distance:

```sql
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

For similarity queries:
```sql
SELECT id, document_id, chunk_index, content, metadata,
       1 - (embedding <=> :query_embedding) AS similarity_score
FROM document_chunks
WHERE tenant_id = :tenant_id
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

---

## Testing

The project includes unit and integration tests using `pytest` and mocks for OpenAI / vector calls:

```bash
pytest tests/ -v
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
