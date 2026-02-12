# Database Schema Design

## Purpose
Design database schema for the application with proper entity modeling, relationships, and optimization for PostgreSQL.

## Steps
1. Identify entities and their attributes
2. Define relationships between entities
3. Plan indexes for query optimization
4. Design for scalability and performance

## Output
Optimized PostgreSQL schema with SQLModel integration

## Implementation Details

### Entity Identification
- Analyze application requirements and user stories
- Identify core business entities (User, Task, etc.)
- Define attributes for each entity
- Determine data types for each attribute
- Identify required vs optional fields
- Plan for audit fields (created_at, updated_at, deleted_at)
- Consider soft delete requirements

### Entity Attributes Planning
- **Primary Keys**: Use UUID or auto-incrementing integers
- **Foreign Keys**: Reference related entities
- **Timestamps**: Track creation and modification times
- **Status Fields**: Use enums for predefined states
- **Text Fields**: Choose appropriate length constraints
- **Numeric Fields**: Select precision for decimals
- **Boolean Fields**: For binary states
- **JSON Fields**: For flexible/nested data structures

### Relationship Definition

#### One-to-Many Relationships
- User has many Tasks
- Define foreign key on the "many" side
- Add cascade delete/update rules
- Consider indexing foreign keys

#### Many-to-Many Relationships
- Use junction/association tables
- Include composite primary keys
- Add timestamps if relationship has temporal data
- Consider additional attributes on the relationship

#### One-to-One Relationships
- Rare but useful for optional data
- Use unique constraint on foreign key
- Consider if data should be in same table

### PostgreSQL-Specific Features

#### Data Types
- Use `UUID` for distributed systems
- Use `TIMESTAMP WITH TIME ZONE` for dates
- Use `JSONB` for flexible document storage
- Use `ENUM` types for fixed value sets
- Use `TEXT` instead of VARCHAR when no limit needed
- Use `SERIAL` or `BIGSERIAL` for auto-increment

#### Constraints
- PRIMARY KEY constraints
- FOREIGN KEY constraints with ON DELETE/UPDATE rules
- UNIQUE constraints for natural keys
- CHECK constraints for data validation
- NOT NULL constraints for required fields
- DEFAULT values for common cases

#### Indexes
- Primary key indexes (automatic)
- Foreign key indexes (manual, highly recommended)
- Unique indexes for natural keys
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- GIN/GiST indexes for JSONB and full-text search

### Index Planning Strategy

#### When to Add Indexes
- Columns used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY
- Columns used in GROUP BY
- Foreign key columns (always)
- Columns with high cardinality

#### Index Types
- **B-tree** (default): Most common, good for equality and range queries
- **Hash**: Only for equality comparisons
- **GIN**: For JSONB, arrays, full-text search
- **GiST**: For geometric data, full-text search
- **BRIN**: For very large tables with natural ordering

#### Index Optimization
- Avoid over-indexing (impacts write performance)
- Use composite indexes for multi-column queries
- Order columns in composite indexes by selectivity
- Monitor index usage with pg_stat_user_indexes
- Remove unused indexes periodically

### SQLModel Integration

#### Model Definition
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

### Schema Design Best Practices

#### Normalization
- Follow 3NF (Third Normal Form) for most cases
- Denormalize strategically for read-heavy workloads
- Avoid redundant data storage
- Use foreign keys to maintain referential integrity

#### Naming Conventions
- Use snake_case for table and column names
- Use plural names for tables (users, tasks)
- Use descriptive names (created_at, not just created)
- Prefix junction tables with both entity names
- Use consistent naming patterns across schema

#### Security Considerations
- Never store passwords in plain text
- Use separate columns for sensitive data
- Consider encryption at rest for PII
- Implement row-level security if needed
- Use database roles and permissions
- Audit sensitive table access

#### Scalability Planning
- Design for horizontal partitioning if needed
- Consider table partitioning for large datasets
- Plan for archival strategy
- Use appropriate data types to minimize storage
- Avoid unbounded text fields when possible
- Consider read replicas for read-heavy loads

### Migration Strategy

#### Version Control
- Use Alembic or similar migration tool
- Keep migrations in version control
- Write both upgrade and downgrade scripts
- Test migrations on staging before production
- Document breaking changes

#### Migration Best Practices
- Make migrations reversible when possible
- Avoid data loss in migrations
- Use transactions for atomic changes
- Test with production-like data volumes
- Plan for zero-downtime deployments
- Add indexes concurrently in production

### Performance Optimization

#### Query Optimization
- Use EXPLAIN ANALYZE to understand query plans
- Optimize N+1 query problems with joins
- Use connection pooling
- Implement query result caching
- Batch operations when possible
- Use prepared statements

#### Table Optimization
- Set appropriate autovacuum settings
- Monitor table bloat
- Use VACUUM and ANALYZE regularly
- Consider table partitioning for large tables
- Archive old data periodically

### Data Integrity

#### Constraints
- Use foreign keys to enforce relationships
- Add check constraints for business rules
- Use unique constraints for natural keys
- Set appropriate NOT NULL constraints
- Define default values where sensible

#### Triggers and Functions
- Use triggers for audit logging
- Implement updated_at triggers
- Use database functions for complex logic
- Consider performance impact of triggers

### Documentation

#### Schema Documentation
- Document each table's purpose
- Explain complex relationships
- Note any denormalization decisions
- Document index rationale
- Maintain ER diagrams
- Keep migration history documented

## Example Schema for Todo App

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Validation Checklist
- [ ] All entities identified from requirements
- [ ] Relationships properly defined with foreign keys
- [ ] Appropriate indexes planned for common queries
- [ ] Data types chosen for optimal storage and performance
- [ ] Constraints added for data integrity
- [ ] Naming conventions followed consistently
- [ ] Migration strategy planned
- [ ] Security considerations addressed
- [ ] Scalability requirements considered
- [ ] Documentation completed
