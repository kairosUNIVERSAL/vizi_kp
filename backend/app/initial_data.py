import logging
from decimal import Decimal
from typing import Dict

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Category, Company, PriceItem, User

logger = logging.getLogger(__name__)

FOCUS_GROUP_ACCOUNTS = [
    {
        "email": "focus.admin@kp.local",
        "password": "FocusAdmin2026!",
        "is_admin": True,
        "company": {
            "name": "Focus Admin Ceiling",
            "phone": "+7 (901) 100-00-01",
            "city": "Moscow",
            "address": "Tverskaya 1",
            "website": "https://admin-demo.local",
            "messenger_type": "telegram",
            "messenger_contact": "@focus_admin",
            "warranty_material": 20,
            "warranty_work": 5,
            "validity_days": 21,
            "discount": Decimal("3.00"),
        },
    },
    {
        "email": "focus.sales@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus Sales Studio",
            "phone": "+7 (901) 100-00-02",
            "city": "Saint Petersburg",
            "address": "Nevsky 10",
            "website": "https://sales-demo.local",
            "messenger_type": "whatsapp",
            "messenger_contact": "+79011000002",
            "warranty_material": 15,
            "warranty_work": 3,
            "validity_days": 14,
            "discount": Decimal("7.00"),
        },
    },
    {
        "email": "focus.ops@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus Operations Team",
            "phone": "+7 (901) 100-00-03",
            "city": "Kazan",
            "address": "Baumana 5",
            "website": "https://ops-demo.local",
            "messenger_type": "telegram",
            "messenger_contact": "@focus_ops",
            "warranty_material": 12,
            "warranty_work": 2,
            "validity_days": 10,
            "discount": Decimal("5.00"),
        },
    },
    {
        "email": "focus.newcomer@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus Newcomer Branch",
            "phone": "+7 (901) 100-00-04",
            "city": "Novosibirsk",
            "address": "Lenina 15",
            "website": "https://newcomer-demo.local",
            "messenger_type": "telegram",
            "messenger_contact": "@focus_newcomer",
            "warranty_material": 10,
            "warranty_work": 1,
            "validity_days": 7,
            "discount": Decimal("0.00"),
        },
    },
]

CATEGORY_SEED = [
    {"name": "PVC", "slug": "pvc", "is_equipment": False},
    {"name": "Fabric", "slug": "fabric", "is_equipment": False},
    {"name": "Profiles", "slug": "profiles", "is_equipment": False},
    {"name": "Lighting", "slug": "lighting", "is_equipment": True},
    {"name": "Works", "slug": "works", "is_equipment": False},
    {"name": "Extra", "slug": "extra", "is_equipment": True},
]

PRICE_TEMPLATE = [
    {"category_slug": "pvc", "name": "PVC Matte", "unit": "m2", "price": Decimal("520.00"), "synonyms": "pvc,matte,film"},
    {"category_slug": "pvc", "name": "PVC Gloss", "unit": "m2", "price": Decimal("560.00"), "synonyms": "pvc,gloss"},
    {"category_slug": "fabric", "name": "Fabric White", "unit": "m2", "price": Decimal("980.00"), "synonyms": "fabric,white"},
    {"category_slug": "profiles", "name": "Wall Profile", "unit": "m", "price": Decimal("180.00"), "synonyms": "profile,wall"},
    {"category_slug": "profiles", "name": "Shadow Profile", "unit": "m", "price": Decimal("1250.00"), "synonyms": "shadow,eurokraab"},
    {"category_slug": "lighting", "name": "Spot Installation", "unit": "pcs", "price": Decimal("450.00"), "synonyms": "spot,light"},
    {"category_slug": "lighting", "name": "Chandelier Installation", "unit": "pcs", "price": Decimal("1100.00"), "synonyms": "chandelier"},
    {"category_slug": "works", "name": "Pipe Bypass", "unit": "pcs", "price": Decimal("350.00"), "synonyms": "pipe,bypass"},
    {"category_slug": "works", "name": "Inner Corner", "unit": "pcs", "price": Decimal("0.00"), "synonyms": "corner,inner"},
    {"category_slug": "extra", "name": "Delivery", "unit": "order", "price": Decimal("1500.00"), "synonyms": "delivery,logistics"},
]


def _ensure_categories(db: Session) -> Dict[str, Category]:
    existing = {cat.slug: cat for cat in db.query(Category).all()}
    created = 0

    for order, payload in enumerate(CATEGORY_SEED):
        cat = existing.get(payload["slug"])
        if cat:
            continue

        cat = Category(
            name=payload["name"],
            slug=payload["slug"],
            sort_order=order,
            is_system=True,
            is_equipment=payload["is_equipment"],
        )
        db.add(cat)
        created += 1
        existing[payload["slug"]] = cat

    if created:
        db.commit()
        logger.info("Created %s system categories for focus accounts", created)

    return {cat.slug: cat for cat in db.query(Category).all()}


def _ensure_user(db: Session, account: dict) -> User:
    user = db.query(User).filter(User.email == account["email"]).first()
    if user is None:
        user = User(
            email=account["email"],
            password_hash=get_password_hash(account["password"]),
            is_active=True,
            is_admin=account["is_admin"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created focus account %s", user.email)
        return user

    dirty = False
    if not user.is_active:
        user.is_active = True
        dirty = True
    if user.is_admin != account["is_admin"]:
        user.is_admin = account["is_admin"]
        dirty = True

    if dirty:
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Updated focus account flags for %s", user.email)

    return user


def _ensure_company(db: Session, user: User, company_defaults: dict) -> Company:
    company = user.company
    if company is None:
        company = Company(user_id=user.id, **company_defaults)
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info("Created company profile for %s", user.email)
        return company

    dirty = False
    for field, value in company_defaults.items():
        current = getattr(company, field, None)
        if current in (None, ""):
            setattr(company, field, value)
            dirty = True

    if dirty:
        db.add(company)
        db.commit()
        db.refresh(company)
        logger.info("Filled missing company fields for %s", user.email)

    return company


def _ensure_price_items(db: Session, company: Company, categories: Dict[str, Category]) -> None:
    existing_items = db.query(PriceItem).filter(PriceItem.company_id == company.id).count()
    if existing_items > 0:
        return

    for row in PRICE_TEMPLATE:
        category = categories.get(row["category_slug"])
        if category is None:
            logger.warning("Missing category slug '%s', skipping item '%s'", row["category_slug"], row["name"])
            continue

        db.add(
            PriceItem(
                company_id=company.id,
                category_id=category.id,
                name=row["name"],
                unit=row["unit"],
                price=row["price"],
                synonyms=row["synonyms"],
                is_active=True,
                is_custom=False,
            )
        )

    db.commit()
    logger.info("Seeded demo price list for company_id=%s", company.id)


def init_db(db: Session) -> None:
    categories = _ensure_categories(db)

    for account in FOCUS_GROUP_ACCOUNTS:
        user = _ensure_user(db, account)
        company = _ensure_company(db, user, account["company"])
        _ensure_price_items(db, company, categories)

    logger.info("Focus-group seed completed (%s accounts)", len(FOCUS_GROUP_ACCOUNTS))
