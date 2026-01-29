"""
Upload products.json to Qdrant
"""
import json
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.qdrant_service import QdrantService
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")


async def upload_to_qdrant(products):
    """Upload products to Qdrant in batches"""
    try:
        qdrant_service = QdrantService()
        await qdrant_service.initialize()
        
        logger.info(f"⬆️ Uploading {len(products)} products to Qdrant in batches...")
        
        # Upload in batches of 100 to avoid connection issues
        batch_size = 100
        total_uploaded = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(products) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Uploading batch {batch_num}/{total_batches} ({len(batch)} products)...")
            
            try:
                product_ids = await qdrant_service.add_products_batch(batch)
                total_uploaded += len(product_ids)
                logger.info(f"✅ Batch {batch_num} uploaded successfully")
            except Exception as batch_error:
                logger.warning(f"⚠️ Batch {batch_num} failed, retrying...")
                # Retry once
                try:
                    product_ids = await qdrant_service.add_products_batch(batch)
                    total_uploaded += len(product_ids)
                    logger.info(f"✅ Batch {batch_num} uploaded on retry")
                except Exception as retry_error:
                    logger.error(f"❌ Batch {batch_num} failed after retry: {retry_error}")
                    continue
        
        logger.info(f"✅ Successfully uploaded {total_uploaded} products total")
        
        # Health check
        health = await qdrant_service.health_check()
        logger.info(f"🏥 Health check: {health}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return False


async def main():
    """Main function"""
    json_file = Path(__file__).parent / "products.json"
    
    print("🚀 Uploading products.json to Qdrant...\n")
    
    # Load products from JSON
    print("📂 Loading products.json...")
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    print(f"✅ Loaded {len(products)} products\n")
    
    # Upload to Qdrant
    print("📤 Uploading to Qdrant...")
    success = await upload_to_qdrant(products)
    
    if success:
        print("\n🎉 All done! Your products are now in Qdrant!")
        print(f"Total products: {len(products)}")
        categories = set(p.get('category', 'unknown') for p in products)
        print(f"Categories: {categories}")
    else:
        print("\n❌ Upload failed. Check your Qdrant connection.")


if __name__ == "__main__":
    asyncio.run(main())
