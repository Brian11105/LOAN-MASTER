from app import app, db
from sqlalchemy import inspect

with app.app_context():
    print("🔧 Setting up database...")
    
    # Drop all tables (if they exist)
    db.drop_all()
    print("✅ Dropped existing tables")
    
    # Create all tables
    db.create_all()
    print("✅ Created all tables")
    
    # Verify tables exist
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables created: {tables}")
    
    print("\n✅ Database setup complete!")