"""WSGI entry point for Render deployment."""
from app import app
from database import init_db
import seed_data_v3 as full_seed
import content_updater

# Initialize database and seed data on startup
init_db()
full_seed.seed_all()
content_updater.load_detailed_content()
