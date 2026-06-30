// Neo4j schema setup for TuVi GraphRAG

CREATE CONSTRAINT chunk_hash_unique IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.chunk_hash IS UNIQUE;

CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
FOR (c:Chunk)
REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT source_identity_unique IF NOT EXISTS
FOR (s:Source)
REQUIRE (s.source_id, s.domain) IS UNIQUE;

CREATE CONSTRAINT entity_identity_unique IF NOT EXISTS
FOR (e:Entity)
REQUIRE (e.canonical_name, e.entity_type, e.domain) IS UNIQUE;

CREATE CONSTRAINT sao_canonical_unique IF NOT EXISTS
FOR (s:Sao)
REQUIRE s.canonical_name IS UNIQUE;

CREATE CONSTRAINT cung_canonical_unique IF NOT EXISTS
FOR (c:Cung)
REQUIRE c.canonical_name IS UNIQUE;

CREATE CONSTRAINT thien_can_canonical_unique IF NOT EXISTS
FOR (t:ThienCan)
REQUIRE t.canonical_name IS UNIQUE;

CREATE CONSTRAINT dia_chi_canonical_unique IF NOT EXISTS
FOR (d:DiaChi)
REQUIRE d.canonical_name IS UNIQUE;

CREATE CONSTRAINT ngu_hanh_canonical_unique IF NOT EXISTS
FOR (n:NguHanh)
REQUIRE n.canonical_name IS UNIQUE;

CREATE INDEX chunk_domain_strategy IF NOT EXISTS
FOR (c:Chunk) ON (c.domain, c.chunk_strategy_id);

CREATE INDEX entity_domain_type IF NOT EXISTS
FOR (e:Entity) ON (e.domain, e.entity_type);

CREATE INDEX mentions_source_chunk IF NOT EXISTS
FOR ()-[r:MENTIONS]-() ON (r.chunk_hash, r.chunk_strategy_id);

CREATE VECTOR INDEX chunkVector IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}};

CREATE VECTOR INDEX chunkVectorBgeM3 IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding_bge_m3)
OPTIONS {indexConfig: {`vector.dimensions`: 1024, `vector.similarity_function`: 'cosine'}};

CREATE FULLTEXT INDEX chunkFulltext IF NOT EXISTS
FOR (c:Chunk) ON EACH [c.text, c.title, c.keywords];
