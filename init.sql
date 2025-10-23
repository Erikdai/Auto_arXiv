-- 创建papers表
CREATE TABLE IF NOT EXISTS papers (
    id VARCHAR(50) PRIMARY KEY,
    sn SERIAL,
    category VARCHAR(20),
    title TEXT,
    authors TEXT,
    abstract TEXT,
    url TEXT,
    added_at DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_papers_added_at ON papers(added_at);
CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category);
CREATE INDEX IF NOT EXISTS idx_papers_sn ON papers(sn);