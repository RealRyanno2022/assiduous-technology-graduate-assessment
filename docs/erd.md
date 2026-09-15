# Data model (ERD)

```mermaid
erDiagram
    COMPANIES ||--o{ FILING_PERIODS : reports
    COMPANIES ||--o{ SOURCE_DOCUMENTS : files
    SOURCE_DOCUMENTS ||--o{ FILING_PERIODS : evidences
    FILING_PERIODS ||--o{ FINANCIAL_LINE_ITEMS : contains
    FILING_PERIODS ||--o{ COMPUTED_METRICS : derives
    FILING_PERIODS ||--o{ AI_INSIGHTS : narrates
    AI_INSIGHTS ||--o{ EMBEDDINGS : embeds
    FINANCIAL_LINE_ITEMS ||--o{ EMBEDDINGS : embeds

    COMPANIES {
        int id PK
        string name
        string ticker
        string isin
        string country
        string sector
    }
    SOURCE_DOCUMENTS {
        int id PK
        int company_id FK
        string doc_type
        string title
        string file_path
        date published_date
        datetime ingested_at
    }
    FILING_PERIODS {
        int id PK
        int company_id FK
        int source_document_id FK
        string period_type
        string period_label
        date period_start
        date period_end
        bool is_audited
    }
    FINANCIAL_LINE_ITEMS {
        int id PK
        int filing_period_id FK
        int source_document_id FK
        string statement
        string line_item
        numeric value_eur
        numeric comparative_value_eur
        string extraction_confidence
        string raw_snippet
    }
    COMPUTED_METRICS {
        int id PK
        int filing_period_id FK
        string category
        string metric_key
        numeric metric_value
        string unit
        datetime computed_at
    }
    AI_INSIGHTS {
        int id PK
        int filing_period_id FK
        string category
        string title
        string body
        string model
        datetime created_at
    }
    EMBEDDINGS {
        int id PK
        string source_type
        int source_id
        string content
        vector embedding
    }
    USERS {
        int id PK
        string email
        string hashed_password
        string full_name
        string role
    }
```

`filing_periods.period_type` is one of `HY` / `FY`. `financial_line_items.statement` is
one of `pnl` / `balance_sheet` / `cash_flow`. `computed_metrics.category` and
`ai_insights.category` are one of `growth` / `profitability` / `cash_liquidity` /
`solvency` / `returns`. `embeddings.embedding` is `vector(1536)` (pgvector) in Postgres;
on the SQLite dev fallback it degrades to a JSON-encoded float array and RAG retrieval
falls back to keyword lookup over `content` (see ADR 0002).
