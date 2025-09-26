"""Initial migration

Revision ID: 003_initial_migration
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create all tables
    op.create_table('sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('web', 'pdf', 'youtube', 'rss', 'newsletter', 'kindle', name='sourcetype'), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('raw', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_id'), 'sources', ['id'], unique=False)
    
    op.create_table('rss_feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('weight', sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rss_feeds_id'), 'rss_feeds', ['id'], unique=False)
    op.create_index(op.f('ix_rss_feeds_url'), 'rss_feeds', ['url'], unique=True)
    
    op.create_table('articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_md', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('source_domain', sa.String(), nullable=True),
        sa.Column('guid', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['feed_id'], ['rss_feeds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_articles_id'), 'articles', ['id'], unique=False)
    op.create_index(op.f('ix_articles_url'), 'articles', ['url'], unique=True)
    op.create_index(op.f('ix_articles_guid'), 'articles', ['guid'], unique=True)
    
    op.create_table('highlights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_highlights_id'), 'highlights', ['id'], unique=False)
    
    op.create_table('embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('object_type', sa.String(), nullable=False),
        sa.Column('object_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('vector', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_embeddings_id'), 'embeddings', ['id'], unique=False)
    
    op.create_table('article_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('vector', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_embeddings_id'), 'article_embeddings', ['id'], unique=False)
    
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('highlight_id', sa.Integer(), nullable=False),
        sa.Column('next_review_at', sa.DateTime(), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=True),
        sa.Column('ease', sa.Float(), nullable=True),
        sa.Column('reps', sa.Integer(), nullable=True),
        sa.Column('last_result', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['highlight_id'], ['highlights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    
    op.create_table('review_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('highlight_id', sa.Integer(), nullable=False),
        sa.Column('session_type', sa.String(), nullable=False),
        sa.Column('question', sa.Text(), nullable=True),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('correct_answer', sa.Text(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('difficulty_rating', sa.Integer(), nullable=True),
        sa.Column('time_spent', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['highlight_id'], ['highlights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_review_sessions_id'), 'review_sessions', ['id'], unique=False)
    
    op.create_table('exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('config_json', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exports_id'), 'exports', ['id'], unique=False)
    
    op.create_table('rss_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['feed_id'], ['rss_feeds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rss_items_id'), 'rss_items', ['id'], unique=False)


def downgrade():
    op.drop_table('rss_items')
    op.drop_table('exports')
    op.drop_table('review_sessions')
    op.drop_table('reviews')
    op.drop_table('article_embeddings')
    op.drop_table('embeddings')
    op.drop_table('highlights')
    op.drop_table('articles')
    op.drop_table('rss_feeds')
    op.drop_table('sources')