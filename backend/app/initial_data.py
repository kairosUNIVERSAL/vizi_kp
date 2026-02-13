import logging
from decimal import Decimal
from typing import Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Company, PriceItem, User

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
    {
        "email": "focus.dispatch@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus Dispatch Center",
            "phone": "+7 (901) 100-00-05",
            "city": "Yekaterinburg",
            "address": "Mira 7",
            "website": "https://dispatch-demo.local",
            "messenger_type": "whatsapp",
            "messenger_contact": "+79011000005",
            "warranty_material": 8,
            "warranty_work": 1,
            "validity_days": 5,
            "discount": Decimal("2.00"),
        },
    },
    {
        "email": "focus.measure@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus Measure Unit",
            "phone": "+7 (901) 100-00-06",
            "city": "Samara",
            "address": "Molodogvardeyskaya 20",
            "website": "https://measure-demo.local",
            "messenger_type": "telegram",
            "messenger_contact": "@focus_measure",
            "warranty_material": 11,
            "warranty_work": 2,
            "validity_days": 12,
            "discount": Decimal("4.00"),
        },
    },
    {
        "email": "focus.b2b@kp.local",
        "password": "FocusUser2026!",
        "is_admin": False,
        "company": {
            "name": "Focus B2B Channel",
            "phone": "+7 (901) 100-00-07",
            "city": "Nizhny Novgorod",
            "address": "Belinskogo 32",
            "website": "https://b2b-demo.local",
            "messenger_type": "telegram",
            "messenger_contact": "@focus_b2b",
            "warranty_material": 18,
            "warranty_work": 4,
            "validity_days": 20,
            "discount": Decimal("6.00"),
        },
    },
]

LEGACY_MOCK_ITEM_NAMES = {
    "PVC Matte",
    "PVC Gloss",
    "Fabric White",
    "Wall Profile",
    "Shadow Profile",
    "Spot Installation",
    "Chandelier Installation",
    "Pipe Bypass",
    "Inner Corner",
    "Delivery",
}


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


def _find_source_company_id(db: Session) -> Optional[int]:
    focus_emails = {account["email"] for account in FOCUS_GROUP_ACCOUNTS}
    admins = db.query(User).filter(User.is_admin == True).order_by(User.created_at.asc()).all()

    for admin in admins:
        if not admin.company or admin.email in focus_emails:
            continue
        has_items = db.query(PriceItem.id).filter(PriceItem.company_id == admin.company.id).first() is not None
        if has_items:
            return admin.company.id

    for admin in admins:
        if not admin.company:
            continue
        has_items = db.query(PriceItem.id).filter(PriceItem.company_id == admin.company.id).first() is not None
        if has_items:
            return admin.company.id

    return None


def _company_has_legacy_mock_items(db: Session, company_id: int) -> bool:
    names = {
        row[0]
        for row in db.query(PriceItem.name).filter(PriceItem.company_id == company_id).all()
    }
    return bool(names) and names == LEGACY_MOCK_ITEM_NAMES


def _build_source_signature(db: Session, source_company_id: Optional[int]) -> Set[Tuple]:
    if source_company_id is None:
        return set()

    source_items = db.query(PriceItem).filter(PriceItem.company_id == source_company_id).all()
    return {
        (
            item.category_id,
            item.name,
            item.unit,
            str(item.price),
            item.synonyms or "",
            bool(item.is_active),
            bool(item.is_custom),
        )
        for item in source_items
    }


def _company_matches_source_signature(items: list[PriceItem], source_signature: Set[Tuple]) -> bool:
    if not source_signature:
        return False
    if len(items) != len(source_signature):
        return False

    company_signature = {
        (
            item.category_id,
            item.name,
            item.unit,
            str(item.price),
            item.synonyms or "",
            bool(item.is_active),
            bool(item.is_custom),
        )
        for item in items
    }
    return company_signature == source_signature


def _cleanup_seeded_price_items(db: Session, company: Company, source_signature: Set[Tuple]) -> None:
    items = db.query(PriceItem).filter(PriceItem.company_id == company.id).all()
    if not items:
        return

    should_cleanup = _company_has_legacy_mock_items(db, company.id) or _company_matches_source_signature(items, source_signature)
    if not should_cleanup:
        return

    db.query(PriceItem).filter(PriceItem.company_id == company.id).delete(synchronize_session=False)
    db.commit()
    logger.info("Cleared seeded price items for focus account company_id=%s", company.id)


def init_db(db: Session) -> None:
    source_company_id = _find_source_company_id(db)
    source_signature = _build_source_signature(db, source_company_id)
    if source_company_id:
        logger.info("Using source admin company_id=%s for focus-group price structure", source_company_id)
    else:
        logger.warning("Source admin company with price items not found")

    for account in FOCUS_GROUP_ACCOUNTS:
        user = _ensure_user(db, account)
        company = _ensure_company(db, user, account["company"])
        _cleanup_seeded_price_items(db, company, source_signature)

    logger.info("Focus-group seed completed (%s accounts)", len(FOCUS_GROUP_ACCOUNTS))
