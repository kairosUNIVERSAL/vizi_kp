import sys
import os
import openpyxl
import logging

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging to write to a file to avoid encoding issues with stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import_log.txt", mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

from app.database import SessionLocal
from app.models import PriceItem, Category, Company, User
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File path to the Excel file
EXCEL_PATH = r"c:\Assensio99\Code stuf\KP_LIGHT_VISO\price_list_ceiling.xlsx"

def import_price_list():
    db = SessionLocal()
    try:
        if not os.path.exists(EXCEL_PATH):
            logger.error(f"File not found: {EXCEL_PATH}")
            return

        # Load workbook
        workbook = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        
        # Get default company (or create logic to find it)
        # Assuming single user/company for now or specific target
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user or not user.company:
            logger.error("Default user or company not found.")
            return
        
        company_id = user.company.id
        logger.info(f"Importing for company: {user.company.name} (ID: {company_id})")

        # Define sheet to category mapping + equipment flag
        # Based on Excel analysis:
        # "Полотна" -> pvc/fabric?
        # "Профили" -> profiles
        # "Освещение" -> lighting (Equipment)
        # "Гардины" -> curtains (Equipment?) -> Let's ask or assume based on logic. Usually Equipment.
        # "Работы" -> works
        # "Доп. материалы" -> extra
        
        # Mapping logic: Sheet Name -> (Slug, IsEquipment)
        sheet_mapping = {
            "Полотна": ("pvc", False), # Assuming mixed or mainly PVC/Fabric
            "Профили": ("profiles", False),
            "Освещение": ("lighting", True),
            "Гардины": ("curtains", True), # New category possibly
            "Работы": ("works", False),
            "Доп. материалы": ("extra", False),
            # Add others if found in Excel inspection
        }

        # Clear existing items? Or Update?
        # Strategy: Deactivate all existing system items for this company to avoid duplicates, 
        # or just delete if we want a fresh start. 
        # Given "обновить прайс и его структуру в точности как в файле", 
        # it's better to sync categories and items.
        
        # Let's iterate over sheets
        for sheet_name in workbook.sheetnames:
            if sheet_name not in sheet_mapping:
                logger.warning(f"Skipping unknown sheet: {sheet_name}")
                # Create category dynamically?
                slug = sheet_name.lower().replace(" ", "_")
                is_equipment = False
                if "освещение" in slug or "свет" in slug or "оборудование" in slug or "карниз" in slug:
                     is_equipment = True
                sheet_mapping[sheet_name] = (slug, is_equipment)
            
            slug, is_equipment = sheet_mapping[sheet_name]
            
            # Find or Create Category
            category = db.query(Category).filter(Category.slug == slug).first()
            if not category:
                logger.info(f"Creating category: {sheet_name} ({slug})")
                category = Category(
                    name=sheet_name,
                    slug=slug,
                    is_system=True,
                    is_equipment=is_equipment
                )
                db.add(category)
                db.commit()
                db.refresh(category)
            else:
                # Update is_equipment flag
                category.is_equipment = is_equipment
                category.name = sheet_name # Update name to match Excel if needed
                db.add(category)
                db.commit()

            # Process Rows
            ws = workbook[sheet_name]
            
            # Locate headers
            # Assuming row 1 or 2 has headers?
            # Based on inspection:
            # Sheet "Полотна": headers likely around row 3 or 4.
            # Let's look for "Наименование" or similar.
            
            header_row_idx = -1
            col_map = {} # 'name': idx, 'unit': idx, 'price': idx
            
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                row_values = [str(c).strip().lower() for c in row if c is not None]
                if "наименование" in row_values or "материал" in row_values:
                    header_row_idx = i + 1 # 1-based for openpyxl if needed, but we use enumerate
                    # Map columns
                    for col_idx, cell_value in enumerate(row):
                        val = str(cell_value).strip().lower() if cell_value else ""
                        if "наименование" in val or "материал" in val:
                            col_map['name'] = col_idx
                        elif "ед" in val:
                            col_map['unit'] = col_idx
                        elif "цена" in val: # "цена дилера" ? "цена клиента"? Take last one?
                            # Often there are multiple prices. Let's look for "цена" or "стоимость"
                            # If "цена монтажа" is separate, we might need composite item.
                            # For now, simplistic approach: "Цена"
                            if 'price' not in col_map: 
                                col_map['price'] = col_idx
                    
                    if 'name' in col_map and 'price' in col_map:
                        break
            
            if header_row_idx == -1:
                logger.warning(f"Could not find headers in sheet {sheet_name}")
                continue
                
            logger.info(f"Processing sheet {sheet_name}, headers at row {header_row_idx}")

            # Read data
            for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
                # Check validation
                if not row[col_map['name']]: continue
                
                name = str(row[col_map['name']]).strip()
                if not name: continue
                
                unit = "шт"
                if 'unit' in col_map and row[col_map['unit']]:
                    unit = str(row[col_map['unit']]).strip()
                
                price_val = 0
                if 'price' in col_map and row[col_map['price']]:
                    try:
                        # Clean price string
                        p_str = str(row[col_map['price']]).replace(" ", "").replace(",", ".")
                        price_val = float(p_str)
                    except:
                        price_val = 0
                
                # Create or Update PriceItem
                # Check if exists by name in this category
                item = db.query(PriceItem).filter(
                    PriceItem.company_id == company_id,
                    PriceItem.category_id == category.id,
                    PriceItem.name == name
                ).first()
                
                if item:
                    item.price = price_val
                    item.unit = unit
                    item.is_active = True
                else:
                    item = PriceItem(
                        company_id=company_id,
                        category_id=category.id,
                        name=name,
                        unit=unit,
                        price=price_val,
                        is_active=True,
                        is_custom=False
                    )
                    db.add(item)
            
            db.commit()
            logger.info(f"Sheet {sheet_name} processed.")

    except Exception as e:
        logger.exception(f"Error importing excel: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_price_list()
