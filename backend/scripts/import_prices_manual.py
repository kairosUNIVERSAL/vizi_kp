"""
Direct database import script from manually extracted Excel data.
Run: docker compose exec backend python scripts/import_prices_manual.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import PriceItem, Category

DEFAULT_COMPANY_ID = 1

# Data extracted from screenshots
CATEGORIES_DATA = [
    {"name": "ПВХ полотна", "slug": "pvh_polotna"},
    {"name": "Тканевые полотна", "slug": "tkanevye_polotna"},
    {"name": "Монтаж полотна", "slug": "montazh_polotna"},
    {"name": "Профиль ПВХ", "slug": "profil_pvh"},
    {"name": "Теневой профиль", "slug": "tenevoy_profil"},
    {"name": "Парящий потолок", "slug": "paryashiy_potolok"},
    {"name": "Трек", "slug": "trek"},
    {"name": "Световая линия", "slug": "svetovaya_liniya"},
    {"name": "Светильники", "slug": "svetilniki"},
    {"name": "Карнизы", "slug": "karnizy"},
    {"name": "Вентиляция", "slug": "ventilyaciya"},
    {"name": "Обходы", "slug": "obhody"},
    {"name": "Сложности", "slug": "slozhnosti"},
    {"name": "Демонтаж", "slug": "demontazh"},
    {"name": "Дополнительно", "slug": "dopolnitelno"},
    {"name": "Точечные GX53", "slug": "tochechnye_gx53"},
    {"name": "Лампы GX53", "slug": "lampy_gx53"},
    {"name": "Точечные MR16", "slug": "tochechnye_mr16"},
    {"name": "Лампы MR16", "slug": "lampy_mr16"},
    {"name": "Трековые", "slug": "trekovye"},
    {"name": "Накладные", "slug": "nakladnye"},
    {"name": "Линейные", "slug": "lineynye"},
    {"name": "LED лента", "slug": "led_lenta"},
    {"name": "Блоки питания", "slug": "bloki_pitaniya"},
    {"name": "Профили LED", "slug": "profili_led"},
    {"name": "Люстры", "slug": "lyustry"},
    {"name": "Комплектующие", "slug": "komplektuyushie"},
    {"name": "Бесщелевой", "slug": "beshelevoy"},
    {"name": "Разделитель", "slug": "razdelitel"},
    {"name": "Гарпун", "slug": "garpun"},
]

# Items from screenshots (category_slug, name, price, unit, synonyms)
ITEMS_DATA = [
    # === ПОЛОТНА (screenshot 1) ===
    ("pvh_polotna", "MSD Classic Мат 3.2м", 450, "м²", "эконом, msd classic"),
    ("pvh_polotna", "MSD Classic Сатин 3.2м", 450, "м²", ""),
    ("pvh_polotna", "MSD Classic Глянец 3.2м", 500, "м²", ""),
    ("pvh_polotna", "MSD Premium Мат 3.2м", 550, "м²", "экологичный"),
    ("pvh_polotna", "MSD Premium Сатин 3.2м", 550, "м²", ""),
    ("pvh_polotna", "MSD Premium Глянец 3.2м", 600, "м²", ""),
    ("pvh_polotna", "MSD Premium Мат 5м", 650, "м²", "широкий бесшовный"),
    ("pvh_polotna", "MSD Premium Сатин 5м", 650, "м²", ""),
    ("pvh_polotna", "MSD Premium Глянец 5м", 700, "м²", ""),
    ("pvh_polotna", "MSD Premium 5.8м", 750, "м²", "максимальная ширина"),
    ("pvh_polotna", "Bauf Мат 3.2м", 550, "м²", "плотное полотно, bauf"),
    ("pvh_polotna", "Bauf Сатин 3.2м", 550, "м²", "bauf"),
    ("pvh_polotna", "Bauf Глянец 3.2м", 590, "м²", "bauf"),
    ("pvh_polotna", "Bauf 4.5м", 650, "м²", "широкий, bauf"),
    ("pvh_polotna", "Bauf 5.5м", 700, "м²", "bauf"),
    ("pvh_polotna", "Bauf FireProof КМ3 3.2м", 600, "м²", "пожаробезопасный"),
    ("pvh_polotna", "Bauf FireProof КМ3 4.5м", 650, "м²", ""),
    ("pvh_polotna", "Pongs Мат 3.25м", 700, "м²", "германия премиум, pongs"),
    ("pvh_polotna", "Pongs Сатин 3.25м", 700, "м²", "pongs"),
    ("pvh_polotna", "Pongs Глянец 3.25м", 750, "м²", "pongs"),
    ("pvh_polotna", "DEKEN Мат 3.2м", 600, "м²", "качество, deken"),
    ("pvh_polotna", "DEKEN Сатин 3.2м", 600, "м²", "deken"),
    ("pvh_polotna", "DEKEN Глянец 3.2м", 650, "м²", "deken"),
    ("tkanevye_polotna", "Descor Ткань 5.1м", 1200, "м²", "германия, без нагрева, descor"),
    ("tkanevye_polotna", "Clipso Ткань 5.1м", 1500, "м²", "франция премиум, clipso"),
    ("pvh_polotna", "MSD/Bauf Мат Цветной 3.2м", 600, "м²", "палитра 150+ цветов"),
    ("pvh_polotna", "MSD/Bauf Глянец Цветной 3.2м", 650, "м²", ""),
    ("pvh_polotna", "MSD/Bauf Сатин Цветной 3.2м", 600, "м²", ""),
    ("pvh_polotna", "MSD/Bauf Мат Чёрный 3.2м", 700, "м²", ""),
    ("pvh_polotna", "MSD/Bauf Глянец Чёрный 3.2м", 750, "м²", "зеркальный эффект"),
    
    # === УСЛУГИ (screenshot 2) ===
    ("montazh_polotna", "Монтаж полотна до 3.2м", 350, "м²", "натяжка, установка"),
    ("montazh_polotna", "Монтаж полотна 5м широкий", 400, "м²", "пятиметровый"),
    ("montazh_polotna", "Монтаж тканевого полотна", 500, "м²", "ткань, descor, clipso"),
    ("profil_pvh", "ПВХ профиль стартовый", 200, "м", "багет, стеновой"),
    ("profil_pvh", "Маскировочная лента белая", 150, "м", "вставка, заглушка"),
    ("profil_pvh", "Маскировочная лента цветная", 180, "м", ""),
    ("profil_pvh", "Работа с углами на ПВХ профиле", 200, "м", "угол, внутренний, внешний"),
    ("profil_pvh", "Соединение полотен (разделитель)", 1490, "м", "стык, разделительный"),
    ("tenevoy_profil", "Профиль теневой EuroKraab", 1500, "м", "еврокрааб, евро краб, краб, теневой"),
    ("tenevoy_profil", "Профиль теневой EuroKraab Strong", 1700, "м", "усиленный"),
    ("tenevoy_profil", "Угол теневого профиля внутренний", 575, "шт", "внутренний угол"),
    ("tenevoy_profil", "Угол теневого профиля внешний", 575, "шт", "внешний угол, наружный"),
    ("tenevoy_profil", "Теневой профиль Бизон", 900, "м", "bizon"),
    ("tenevoy_profil", "Бесщелевой профиль KRAAB 3.0", 900, "м", "без щели"),
    ("paryashiy_potolok", "Парящий профиль с подсветкой", 1600, "м", "парящий, подсветка периметра"),
    ("paryashiy_potolok", "Парящий профиль без подсветки", 1200, "м", ""),
    ("paryashiy_potolok", "Угол парящего профиля", 800, "шт", ""),
    ("trek", "Трековое освещение (профиль+монтаж)", 6000, "м", "трек, трековый, шинопровод"),
    ("trek", "Обработка торцов на треке", 3000, "шт", "торец, заглушка"),
    ("trek", "Работа с углами на треке", 1000, "шт", "угол трека"),
    ("trek", "Подключение трекового оборудования", 1500, "шт", "запуск, подключение"),
    ("trek", "Закладная под накладной трек", 990, "м", "накладной шинопровод"),
    ("trek", "Установка накладного трека", 550, "м", ""),
    ("svetovaya_liniya", "Световая линия (профиль+монтаж)", 2300, "м", "светолиния, свет линия"),
    ("svetovaya_liniya", "Монтаж светодиодной ленты", 300, "м", "LED лента"),
    ("svetovaya_liniya", "Установка рассеивателя", 900, "м", "диффузор"),
    ("svetovaya_liniya", "Работа с углами световой линии", 2500, "шт", "угол световой"),
    ("svetovaya_liniya", "Пайка ленты на углах", 500, "шт", "спайка"),
    ("svetovaya_liniya", "Подключение блоков питания", 1500, "шт", "блок, драйвер"),
    ("svetovaya_liniya", "Торец/заглушка световой линии", 350, "шт", "закладная под светильник"),
    ("svetilniki", "Закладная под точечный светильник", 350, "шт", "точечник, спот"),
    ("svetilniki", "Установка светильника накладного", 600, "шт", "накладной"),
    ("svetilniki", "Установка светильника (вклейка кольца)", 920, "шт", "вклейска кольца"),
    ("svetilniki", "Установка прямоугольного светильника", 1800, "шт", "прямоугольный, квадратный"),
    ("svetilniki", "Закладная под люстру", 400, "шт", "платформа под люстру"),
    ("svetilniki", "Закладная под люстру усиленная", 500, "шт", "тяжелая люстра"),
    ("svetilniki", "Установка люстры (без сборки)", 500, "шт", "подключение люстры"),
    ("svetilniki", "Установка люстры (со сборкой)", 1000, "шт", "сборка люстры"),
    ("svetilniki", "Установка люстры тяжелой (15-30 кг)", 1500, "шт", ""),
    ("svetilniki", "Прокладка проводки для светильников", 150, "м", "кабель, провод"),
    ("karnizy", "Ниша под шторы (профиль ПК-5)", 3600, "м", "скрытый карниз, ниша"),
    ("karnizy", "Ниша под шторы SLOTT", 8000, "м", "слот, премиум"),
    ("karnizy", "Закладная под гардину", 800, "м", "под карниз"),
    ("karnizy", "Установка карниза", 1000, "м", ""),
    ("karnizy", "Установка электрокарниза", 4500, "шт", "моторизованный"),
    ("ventilyaciya", "Закладная под вытяжку/вентилятор", 500, "шт", "вентиляция"),
    ("ventilyaciya", "Установка вытяжки/вентилятора", 1200, "шт", ""),
    ("ventilyaciya", "Установка вентиляционной решётки", 500, "шт", "решётка"),
    ("ventilyaciya", "Демонтаж/монтаж пожарного датчика", 1000, "шт", "пожарный датчик"),
    ("obhody", "Обход трубы (до 32мм)", 300, "шт", "труба"),
    ("obhody", "Обход трубы (32-55мм)", 500, "шт", ""),
    ("obhody", "Обход трубы (55-110мм)", 850, "шт", ""),
    ("obhody", "Обход ригеля/балки", 5000, "шт", "ригель, балка"),
    ("obhody", "Обход колонны", 3000, "шт", "колонна"),
    ("slozhnosti", "Работа по кафелю", 150, "м", "плитка, сверление"),
    ("slozhnosti", "Работа по керамограниту", 500, "м", "керамогранит"),
    ("slozhnosti", "Крепление в металл", 500, "м", "металлоконструкция"),
    ("slozhnosti", "Работа на высоте (3-4м)", 100, "м²", "высокие потолки"),
    ("slozhnosti", "Работа на высоте (от 4м)", 200, "м²", "леса"),
    ("slozhnosti", "Усиление (конструктив)", 300, "м", "усиленная закладная"),
    ("slozhnosti", "Работа по ГКЛ (гипсокартон)", 200, "м", "гипсокартон"),
    ("slozhnosti", "Работа по утеплителю", 300, "м", "минвата, пенопласт"),
    ("demontazh", "Демонтаж полотна", 150, "м²", "снятие"),
    ("demontazh", "Демонтаж полотна (с сохранением)", 250, "м²", "аккуратный демонтаж"),
    ("demontazh", "Демонтаж профиля", 500, "м", ""),
    ("demontazh", "Демонтаж люстры", 500, "шт", ""),
    ("dopolnitelno", "Установка распаячной коробки", 200, "шт", ""),
    ("dopolnitelno", "Обеспыливание помещения", 100, "м²", "уборка, защита"),
    ("dopolnitelno", "Защита мебели плёнкой", 300, "шт", ""),
    ("dopolnitelno", "Вынос мусора", 500, "шт", ""),
    
    # === ОСВЕЩЕНИЕ (screenshot 3) ===
    ("tochechnye_gx53", "Светильник GX53 белый круглый", 150, "шт", "базовый"),
    ("tochechnye_gx53", "Светильник GX53 белый квадратный", 180, "шт", ""),
    ("tochechnye_gx53", "Светильник GX53 чёрный круглый", 200, "шт", ""),
    ("tochechnye_gx53", "Светильник GX53 хром круглый", 200, "шт", ""),
    ("tochechnye_gx53", "Светильник GX53 золото круглый", 200, "шт", ""),
    ("tochechnye_gx53", "Светильник GX53 с LED подсветкой", 350, "шт", "с декоративной подсветкой"),
    ("tochechnye_gx53", "Светильник GX53 влагозащищённый IP44", 250, "шт", "для ванной"),
    ("tochechnye_gx53", "Светильник GX53 накладной (спот)", 300, "шт", "накладной"),
    ("lampy_gx53", "Лампа GX53 LED 6W тёплый", 150, "шт", "3000K"),
    ("lampy_gx53", "Лампа GX53 LED 6W нейтральный", 150, "шт", "4000K"),
    ("lampy_gx53", "Лампа GX53 LED 6W холодный", 150, "шт", "6000K"),
    ("lampy_gx53", "Лампа GX53 LED 9W тёплый", 200, "шт", ""),
    ("lampy_gx53", "Лампа GX53 LED 9W нейтральный", 200, "шт", ""),
    ("lampy_gx53", "Лампа GX53 LED 12W тёплый", 250, "шт", "максимальная яркость"),
    ("lampy_gx53", "Лампа GX53 LED 12W нейтральный", 250, "шт", ""),
    ("tochechnye_mr16", "Светильник MR16 белый", 120, "шт", "GU5.3"),
    ("tochechnye_mr16", "Светильник MR16 чёрный", 150, "шт", ""),
    ("tochechnye_mr16", "Светильник MR16 хром", 180, "шт", ""),
    ("lampy_mr16", "Лампа MR16 LED 5W", 100, "шт", "GU5.3"),
    ("lampy_mr16", "Лампа MR16 LED 7W", 150, "шт", ""),
    ("trekovye", "Светильник трековый 10W белый", 1500, "шт", "для шинопровода"),
    ("trekovye", "Светильник трековый 10W чёрный", 1500, "шт", ""),
    ("trekovye", "Светильник трековый 20W белый", 2000, "шт", ""),
    ("trekovye", "Светильник трековый 20W чёрный", 2000, "шт", ""),
    ("trekovye", "Светильник трековый 30W", 2500, "шт", "мощный"),
    ("trekovye", "Светильник трековый поворотный", 2500, "шт", "с регулировкой"),
    ("nakladnye", "Светильник накладной круглый 12W", 800, "шт", "LED панель"),
    ("nakladnye", "Светильник накладной круглый 18W", 1000, "шт", ""),
    ("nakladnye", "Светильник накладной квадратный 12W", 1000, "шт", ""),
    ("nakladnye", "Светильник накладной квадратный 18W", 1200, "шт", ""),
    ("nakladnye", "Светильник-стакан GU10", 600, "шт", "декоративный"),
    ("nakladnye", "Светильник-цилиндр", 800, "шт", ""),
    ("lineynye", "Светильник линейный 60см 18W", 1200, "шт", "для офисов"),
    ("lineynye", "Светильник линейный 120см 36W", 1800, "шт", ""),
    ("lineynye", "Светильник встраиваемый прямоугольный", 1800, "шт", "армстронг"),
    ("led_lenta", "Лента LED 12V 60д/м тёплая", 200, "м", "SMD 2835, за метр"),
    ("led_lenta", "Лента LED 12V 60д/м нейтральная", 200, "м", ""),
    ("led_lenta", "Лента LED 12V 60д/м холодная", 200, "м", ""),
    ("led_lenta", "Лента LED 12V 120д/м тёплая", 350, "м", "яркая"),
    ("led_lenta", "Лента LED 24V 120д/м", 400, "м", "профессиональная"),
    ("led_lenta", "Лента LED RGB", 500, "м", "многоцветная"),
    ("led_lenta", "Лента LED RGBW", 700, "м", "RGB + белый"),
    ("bloki_pitaniya", "Блок питания 12V 36W", 500, "шт", "до 7м ленты"),
    ("bloki_pitaniya", "Блок питания 12V 60W", 700, "шт", "до 12м ленты"),
    ("bloki_pitaniya", "Блок питания 12V 100W", 1000, "шт", "до 20м ленты"),
    ("bloki_pitaniya", "Блок питания 12V 150W", 1300, "шт", ""),
    ("bloki_pitaniya", "Блок питания 24V 100W", 1200, "шт", ""),
    ("bloki_pitaniya", "Блок питания 24V 200W", 1800, "шт", ""),
    ("profili_led", "Профиль алюминиевый накладной", 200, "м", "за метр"),
    ("profili_led", "Профиль алюминиевый врезной", 300, "м", ""),
    ("profili_led", "Профиль алюминиевый угловой", 350, "м", ""),
    ("profili_led", "Рассеиватель матовый", 100, "м", "за метр"),
    ("profili_led", "Рассеиватель прозрачный", 80, "м", ""),
    ("profili_led", "Заглушка для профиля", 50, "шт", "пара"),
    ("lyustry", "Люстра LED современная 60W", 8000, "шт", "с пультом"),
    ("lyustry", "Люстра LED кольца 80W", 12000, "шт", "дизайнерская"),
    ("lyustry", "Люстра классическая 5 рожков", 5000, "шт", ""),
    ("lyustry", "Люстра хрустальная", 15000, "шт", "премиум"),
    ("komplektuyushie", "Закладная универсальная 50-90мм", 80, "шт", "пластиковая"),
    ("komplektuyushie", "Закладная универсальная 90-115мм", 100, "шт", ""),
    ("komplektuyushie", "Закладная под люстру", 150, "шт", ""),
    ("komplektuyushie", "Термокольцо 60мм", 30, "шт", ""),
    ("komplektuyushie", "Термокольцо 80мм", 35, "шт", ""),
    ("komplektuyushie", "Термокольцо 90мм", 40, "шт", ""),
    ("komplektuyushie", "Термокольцо 112мм", 50, "шт", ""),
    ("komplektuyushie", "Подвес для закладной", 30, "шт", ""),
    ("komplektuyushie", "Перфолента 12мм", 50, "м", "за метр"),
    
    # === ПРОФИЛИ (screenshot 4) ===
    ("profil_pvh", "Профиль ПВХ стеновой стартовый", 90, "м", "базовый монтаж"),
    ("profil_pvh", "Профиль ПВХ потолочный", 100, "м", "при низких потолках"),
    ("profil_pvh", "Маскировочная лента белая TL", 50, "м", "заглушка"),
    ("profil_pvh", "Маскировочная лента цветная", 80, "м", ""),
    ("tenevoy_profil", "EUROKRAAB стеновой", 350, "м", "теневой зазор 6мм"),
    ("tenevoy_profil", "EUROKRAAB Strong", 450, "м", "усиленный"),
    ("tenevoy_profil", "EUROKRAAB потолочный", 400, "м", ""),
    ("tenevoy_profil", "Угол EUROKRAAB внутренний", 200, "шт", "90°"),
    ("tenevoy_profil", "Угол EUROKRAAB внешний", 350, "шт", "90°"),
    ("tenevoy_profil", "Профиль Бизон теневой", 250, "м", "бюджетный теневой"),
    ("beshelevoy", "KRAAB 3.0", 300, "м", "без щели"),
    ("beshelevoy", "KRAAB GIPPS", 500, "м", "под гипсокартон"),
    ("paryashiy_potolok", "Парящий профиль с подсветкой", 600, "м", "LED внутри"),
    ("paryashiy_potolok", "Парящий профиль без подсветки", 400, "м", ""),
    ("svetovaya_liniya", "Профиль световой линии 30мм", 800, "м", "узкая"),
    ("световaya_liniya", "Профиль световой линии 50мм", 1000, "м", "стандарт"),
    ("svetovaya_liniya", "Профиль световой линии 80мм", 1200, "м", "широкая"),
    ("trek", "Трековый профиль встраиваемый", 2000, "м", "для шинопровода"),
    ("trek", "Магнитный трек встраиваемый", 3000, "м", "премиум"),
    ("karnizy", "ПК-5 карниз двухрядный", 700, "м", "эконом"),
    ("karnizy", "ПК-15 карниз двухрядный", 1200, "м", "стандарт"),
    ("karnizy", "SLOTT карниз", 1500, "м", "премиум"),
    ("karnizy", "Flexy GARDINA двухрядный", 1800, "м", "с бегунками"),
    ("razdelitel", "Разделительный профиль", 500, "м", "стык полотен"),
    ("razdelitel", "Профиль перехода уровней", 800, "м", "многоуровневый"),
    ("garpun", "Гарпун для ПВХ полотна", 25, "м", "расходник"),
    ("garpun", "Гарпун KRAAB", 35, "м", "для теневого"),
]


def get_or_create_category(db: Session, slug: str, name: str, sort_order: int) -> Category:
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        category = Category(name=name, slug=slug, sort_order=sort_order, is_system=False)
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"  Created category: {name}")
    return category


def import_all(company_id: int = DEFAULT_COMPANY_ID):
    db = SessionLocal()
    
    try:
        # Create categories
        print("\n=== Creating Categories ===")
        category_map = {}
        for i, cat_data in enumerate(CATEGORIES_DATA):
            cat = get_or_create_category(db, cat_data["slug"], cat_data["name"], i + 1)
            category_map[cat_data["slug"]] = cat.id
        
        # Create items
        print("\n=== Importing Items ===")
        imported = 0
        skipped = 0
        
        for cat_slug, name, price, unit, synonyms in ITEMS_DATA:
            # Skip if category not found
            if cat_slug not in category_map:
                print(f"  Warning: Category '{cat_slug}' not found for item '{name}'")
                continue
            
            # Check existing
            existing = db.query(PriceItem).filter(
                PriceItem.company_id == company_id,
                PriceItem.name == name
            ).first()
            
            if existing:
                print(f"  Skipped (exists): {name}")
                skipped += 1
                continue
            
            item = PriceItem(
                company_id=company_id,
                category_id=category_map[cat_slug],
                name=name,
                price=price,
                unit=unit,
                synonyms=synonyms,
                is_active=True,
                is_custom=True
            )
            db.add(item)
            db.commit()
            print(f"  Imported: {name} ({price} ₽/{unit})")
            imported += 1
        
        print(f"\n=== Import Complete ===")
        print(f"Categories: {len(category_map)}")
        print(f"Items imported: {imported}")
        print(f"Items skipped: {skipped}")
        
    finally:
        db.close()


if __name__ == '__main__':
    company_id = DEFAULT_COMPANY_ID
    if len(sys.argv) > 1:
        try:
            company_id = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"Importing prices for company_id={company_id}")
    import_all(company_id)
