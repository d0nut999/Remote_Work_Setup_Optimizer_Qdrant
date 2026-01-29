"""
Setup script for Qdrant Cloud and data ingestion
Run this script to initialize your Qdrant collection and upload sample data
"""
import json
import os
import sys
import asyncio
from pathlib import Path

# Add backend to path so we can import our services
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.qdrant_service import QdrantService
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

async def setup_qdrant():
    """Initialize Qdrant and upload sample data"""
    print("🚀 Setting up Qdrant for Remote Work Setup Optimizer...")
    
    try:
        # Initialize Qdrant service
        qdrant_service = QdrantService()
        await qdrant_service.initialize()
        
        print(" Qdrant service initialized successfully")
        
        # Load sample products
        sample_products_path = Path(__file__).parent / "products.json"
        with open(sample_products_path, 'r') as f:
            products = json.load(f)
        
        print(f" Loaded {len(products)} sample products")
        
        # Upload products to Qdrant
        print(" Uploading products to Qdrant...")
        product_ids = await qdrant_service.add_products_batch(products)
        
        print(f" Successfully uploaded {len(product_ids)} products to Qdrant")
        
        # Test basic connection instead of search
        print(" Testing basic connection...")
        health = await qdrant_service.health_check()
        print(f" Connection test successful: {health}")
        
        print("\n Qdrant setup completed successfully!")
        print(f" Uploaded {len(product_ids)} products to Qdrant")
        print("\nNext steps:")
        print("1. Start the backend server: cd backend && uvicorn main:app --reload")
        print("2. Test the API at: http://localhost:8000/docs")
        print("3. Start building your frontend!")
        
    except Exception as e:
        print(f" Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have created a .env file in the backend directory")
        print("2. Check that your QDRANT_URL and QDRANT_API_KEY are correct")
        print("3. Ensure you have a stable internet connection")
        raise

def create_env_file():
    """Create a .env file with instructions if it doesn't exist"""
    env_path = Path(__file__).parent.parent / "backend" / ".env"
    
    if not env_path.exists():
        print(" Creating .env file template...")
        
        env_content = """# Qdrant Configuration
# Get these from your Qdrant Cloud dashboard: https://cloud.qdrant.io/
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your-api-key-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# ML Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
DEVICE=cpu

# Data Sources
PRODUCTS_DATA_PATH=../data/sample_products.json
ENABLE_SCRAPING=False
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f" Created .env file at {env_path}")
        print("\n  IMPORTANT: You need to update the .env file with your Qdrant credentials!")
        print("\nTo get your Qdrant credentials:")
        print("1. Go to https://cloud.qdrant.io/")
        print("2. Create a free account")
        print("3. Create a new cluster")
        print("4. Copy the cluster URL and API key to your .env file")
        print("5. Run this script again")
        
        return False
    
    return True

if __name__ == "__main__":
    # Check if .env file exists and create if needed
    if not create_env_file():
        sys.exit(1)
    
    # Check if required environment variables are set
    if not os.getenv("QDRANT_URL") or not os.getenv("QDRANT_API_KEY"):
        print(" Please update your .env file with Qdrant credentials before running setup")
        sys.exit(1)
    
    # Run the setup
    asyncio.run(setup_qdrant())
