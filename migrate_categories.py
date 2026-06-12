import os
import json
import time
import difflib
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal

def migrate_remaining_categories():
    db: Session = SessionLocal()
    print("Starting Intelligent AI Category Migration...")

    try:
        # 1. Load all categories
        categories_raw = db.execute(text("SELECT id, slug, seo_title FROM categories")).fetchall()
        
        # 2. Fetch only the remaining brands that are missing a category
        brands = db.execute(
            text("SELECT id, name, seo_keywords::text FROM brands WHERE category_id IS NULL")
        ).fetchall()
        
        if not brands:
            print("No uncategorized brands found! Your data is already fully mapped.")
            return

        print(f"Found {len(brands)} brands requiring analysis.")

        success_count = 0

        for brand in brands:
            brand_text = str(brand.seo_keywords).lower() if brand.seo_keywords else ""
            best_match_id = None
            highest_ratio = 0.0

            for cat in categories_raw:
                # Provide fallbacks if fields are None
                slug = cat.slug or ""
                seo_title = cat.seo_title or ""
                cat_text = f"{slug} {seo_title}".lower()
                
                # difflib compares the text and gives a similarity score from 0.0 to 1.0
                similarity = difflib.SequenceMatcher(None, brand_text, cat_text).ratio()
        
                if similarity > highest_ratio and similarity > 0.3: # 0.3 is the confidence threshold
                    highest_ratio = similarity
                    best_match_id = cat.id

            if best_match_id:
                db.execute(
                    text("UPDATE brands SET category_id = :cat_id WHERE id = :brand_id"),
                    {"cat_id": best_match_id, "brand_id": brand.id}
                )
                success_count += 1
                print(f"Mapped '{brand.name}' -> Category ID: {best_match_id} (Score: {highest_ratio:.2f})")
            else:
                print(f"Skipped '{brand.name}': No confident category match.")

        db.commit()
        print(f"\nMigration Complete! Successfully mapped {success_count} out of {len(brands)} remaining brands.")

    except Exception as e:
        print(f"Structural database failure: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_remaining_categories()
