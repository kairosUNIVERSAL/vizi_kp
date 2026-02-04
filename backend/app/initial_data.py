from sqlalchemy.orm import Session
from app.models import User, Company, Category, PriceItem
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

def init_db(db: Session):
    # Check if user exists
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        logger.info("Creating default user...")
        user = User(
            email="user@example.com",
            password_hash=get_password_hash("password"),
            is_active=True,
            is_admin=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        company = Company(
            user_id=user.id,
            name="Мои Потолки",
            phone="+7 (999) 000-00-00",
            city="Москва"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Init Categories
        categories_data = [
            ("ПВХ полотна", "pvc"),
            ("Тканевые полотна", "fabric"),
            ("Профили", "profiles"),
            ("Освещение", "lighting"),
            ("Работы", "works"),
            ("Доп. расх.", "extra")
        ]
        
        cats = {}
        for idx, (name, slug) in enumerate(categories_data):
            cat = Category(name=name, slug=slug, sort_order=idx)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            cats[slug] = cat

        # Init Price Items
        items_data = [
            (cats['pvc'].id, "MSD Premium матовый", "м²", 500, "полотно, пленка"),
            (cats['pvc'].id, "MSD Premium сатин", "м²", 500, "сатин"),
            (cats['pvc'].id, "MSD Premium глянец", "м²", 500, "глянец, лак"),
            (cats['profiles'].id, "Профиль стеновой ПВХ", "м.п.", 150, "профиль, багет"),
            (cats['profiles'].id, "Профиль теневой EuroKraab", "м.п.", 1200, "еврокраб, теневой"),
            (cats['lighting'].id, "Точечный светильник (монтаж)", "шт", 500, "точки, светильники"),
            (cats['lighting'].id, "Люстра (монтаж)", "шт", 1000, "люстра"),
            (cats['works'].id, "Внутренний угол", "шт", 0, "угол"), # Часто бесплатно или включено
            (cats['works'].id, "Обход трубы", "шт", 300, "труба")
        ]
        
        for cat_id, name, unit, price, synonyms in items_data:
            item = PriceItem(
                company_id=company.id, # Assign to default company for now, or make global system items?
                                       # System architecture implies items belong to company. 
                                       # So we add to this user's company.
                category_id=cat_id,
                name=name,
                unit=unit,
                price=price,
                synonyms=synonyms,
                is_active=True,
                is_custom=False
            )
            db.add(item)
        
        db.commit()
        logger.info("Initial data created.")
    else:
        logger.info("Initial data already exists.")
