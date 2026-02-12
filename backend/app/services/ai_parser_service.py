import json
import re
import logging
import httpx
from decimal import Decimal
from typing import List, Dict, Any
from app.config import settings
from app.models import PriceItem
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class AIParserService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_PARSER_MODEL
    
    def parse_transcript(self, db: Session, company_id: int, transcript: str, user=None) -> Dict[str, Any]:
        # Get price items for matching
        price_items = db.query(PriceItem).filter(
            PriceItem.company_id == company_id,
            PriceItem.is_active == True
        ).all()
        
        logger.info(f"[PARSER] company_id={company_id}, found {len(price_items)} price items")
        logger.info(f"[PARSER] API key present: {bool(self.api_key)}, model: {self.model}")
        logger.info(f"[PARSER] Transcript: {transcript[:200]}...")
        
        # If API key not configured, use fallback regex parser
        if not self.api_key:
            logger.warning("[PARSER] No API key — using FALLBACK regex parser")
            return self._fallback_parse(transcript, price_items)
        
        # Use OpenRouter AI parser
        logger.info("[PARSER] Using AI parser (OpenRouter)")
        items_text = self._format_items_for_prompt(price_items)
        prompt = self._build_prompt(items_text, transcript)
        
        try:
            response_text, usage = self._call_openrouter(prompt)
            logger.info(f"[PARSER] AI response length: {len(response_text)} chars")
            logger.info(f"[PARSER] AI raw response: {response_text[:500]}")
            logger.info(f"[PARSER] Usage: {usage}")
            result = self._parse_response(response_text, price_items)
            
            rooms = result.get('rooms', [])
            total_items = sum(len(r.get('items', [])) for r in rooms)
            unknown = len(result.get('unknown_items', []))
            logger.info(f"[PARSER] Result: {len(rooms)} rooms, {total_items} items matched, {unknown} unknown")
            
            # Update user statistics if user provided (never crash the result)
            if user and usage:
                try:
                    tokens_used = usage.get("total_tokens") or 0
                    cost = tokens_used * 0.000002
                    
                    user.total_tokens_used = (user.total_tokens_used or 0) + tokens_used
                    user.total_api_cost = float(user.total_api_cost or 0) + cost
                    db.commit()
                except Exception as stats_err:
                    logger.warning(f"[PARSER] Stats update failed (non-critical): {stats_err}")
                    db.rollback()
            
            return result
        except Exception as e:
            logger.error(f"[PARSER] OpenRouter API ERROR: {e}", exc_info=True)
            logger.warning("[PARSER] Falling back to regex parser")
            return self._fallback_parse(transcript, price_items)

    def _call_openrouter(self, prompt: str) -> tuple:
        """Call OpenRouter API (OpenAI-compatible). Returns (response_text, usage_dict)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
            "X-Title": "Ceiling KP Generator"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return text, usage

    def _fallback_parse(self, transcript: str, price_items: List[PriceItem]) -> Dict[str, Any]:
        """Simple regex-based parser when AI is not available."""
        rooms = []
        unknown_items = []
        
        # Parse room and area patterns
        room_patterns = [
            r'(гостиная|кухня|спальня|ванная|коридор|холл|детская|кабинет|зал|комната)\s*[:\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:кв(?:адрат|\.?\s*м)|м2|м²|квадрат)?',
            r'(гостиная|кухня|спальня|ванная|коридор|холл|детская|кабинет|зал|комната)\s+(\d+(?:[.,]\d+)?)',
        ]
        
        text_lower = transcript.lower()
        found_rooms = {}
        
        # Track used text ranges to avoid double matching
        matched_ranges = []

        def is_overlapping(start, end):
            for s, e in matched_ranges:
                if max(start, s) < min(end, e):
                    return True
            return False

        # 1. Parse Rooms
        for pattern in room_patterns:
            for match in re.finditer(pattern, text_lower):
                start, end = match.span()
                if is_overlapping(start, end): continue
                
                room_name = match.group(1).capitalize()
                area_group = match.group(2)
                if not area_group and len(match.groups()) > 2: area_group = match.group(3)
                
                if area_group:
                    area = float(area_group.replace(',', '.'))
                    if room_name not in found_rooms:
                        found_rooms[room_name] = {'name': room_name, 'area': area, 'items': [], 'subtotal': 0}
                        matched_ranges.append((start, end))
        
        # If no rooms found, create default room
        if not found_rooms:
            found_rooms['Основная'] = {'name': 'Основная', 'area': 0, 'items': [], 'subtotal': 0}
        
        # 2. Build items map for price lookup
        # Sort keys by length desc to match longest phrases first
        items_map = {}
        keys_to_check = []
        
        for item in price_items:
            # Main name
            name_key = item.name.lower()
            items_map[name_key] = item
            keys_to_check.append(name_key)
            
            # Synonyms
            if item.synonyms:
                for syn in item.synonyms.split(','):
                    s = syn.strip().lower()
                    if s and len(s) > 2: # Ignore very short synonyms
                        items_map[s] = item
                        keys_to_check.append(s)
        
        # Sort keys: longest first
        keys_to_check = sorted(list(set(keys_to_check)), key=len, reverse=True)
        
        parsed_items = []

        # 3. Generic Item Parsing
        # Pattern A: Quantity + Key (e.g. "5 lamps")
        # Pattern B: Key + Quantity (e.g. "lamps 5")
        
        for key in keys_to_check:
            clean_key = re.escape(key)
            patterns = [
                # Qty ... Key
                r'(\d+(?:[.,]\d+)?)\s*(?:шт|пог\.?|м\.?|м2)?\s*[\-xх\*]?\s*' + clean_key + r'\b',
                # Key ... Qty
                r'\b' + clean_key + r'\b\s*[:\-]?\s*(\d+(?:[.,]\d+)?)'
            ]
            
            found_for_key = False
            for pat in patterns:
                for match in re.finditer(pat, text_lower):
                    start, end = match.span()
                    if is_overlapping(start, end): continue
                    
                    qty_str = match.group(1).replace(',', '.')
                    try:
                        quantity = float(qty_str)
                        price_item = items_map[key]
                        
                        # Check if we already have this item to aggregate?
                        # For now, append new
                        parsed_items.append(self._create_item(price_item.name, quantity, price_item))
                        matched_ranges.append((start, end))
                        found_for_key = True
                    except ValueError:
                        pass
            
            # Special case: Key mentioned without quantity? (Assume 1 or ignore?)
            # Usually strict parsing is safer, but "Люстра" usually means 1.
            # Let's skip valid overlap check for pure keyword if strict matching desired.
            # But let's support "Single mention = 1" if not matched yet
            pattern_single = r'\b' + clean_key + r'\b'
            if not found_for_key: 
                 for match in re.finditer(pattern_single, text_lower):
                    start, end = match.span()
                    if is_overlapping(start, end): continue
                    
                    # Assume 1
                    price_item = items_map[key]
                    parsed_items.append(self._create_item(price_item.name, 1.0, price_item))
                    matched_ranges.append((start, end))

        
        # 4. Add items to first room (Simple logic: all items go to first/only room)
        # Ideally we should split by context (items after room declaration), but this is a simple fallback.
        first_room_name = list(found_rooms.keys())[0]
        room_area = found_rooms[first_room_name].get('area', 0)
        
        for item in parsed_items:
            # If item is measured in m² and room has area, use room area as quantity
            if item.get('unit') == 'м²' and room_area > 0:
                item['quantity'] = room_area
                item['sum'] = round(room_area * item.get('price', 0), 2)
            
            found_rooms[first_room_name]['items'].append(item)
            found_rooms[first_room_name]['subtotal'] += item.get('sum', 0)
        
        rooms = list(found_rooms.values())
        total_area = sum(r.get('area', 0) for r in rooms)
        total_sum = sum(r.get('subtotal', 0) for r in rooms)
        
        return {
            'rooms': rooms,
            'unknown_items': unknown_items,
            'total_area': total_area,
            'total_sum': total_sum
        }

    def _create_item(self, name: str, quantity: float, price_item) -> Dict[str, Any]:
        """Helper to create item dict"""
        return {
            'name': name,
            'price_item_id': price_item.id if price_item else None,
            'unit': price_item.unit if price_item else 'шт',
            'quantity': quantity,
            'price': float(price_item.price) if price_item else 0,
            'sum': quantity * float(price_item.price) if price_item else 0
        }

    def _format_items_for_prompt(self, items: List[PriceItem]) -> str:
        lines = []
        for item in items:
            synonyms = f" (синонимы: {item.synonyms})" if item.synonyms else ""
            lines.append(f"- ID:{item.id} | {item.name} | {item.unit} | {item.price} руб{synonyms}")
        return "\n".join(lines)
    
    def _build_prompt(self, items_text: str, transcript: str) -> str:
        return f"""Ты — система для парсинга голосовых записей замерщиков натяжных потолков.

ПРАЙС-ЛИСТ (доступные позиции):
{items_text}

ТРАНСКРИПЦИЯ ЗАМЕРА:
"{transcript}"

ЗАДАЧА:
1. Извлеки все упомянутые комнаты и позиции
2. Сопоставь каждую позицию с прайс-листом по названию или синонимам
3. ВАЖНО: Если позиция упомянута, но НЕ найдена в прайс-листе — ОБЯЗАТЕЛЬНО добавь её в unknown_items с полем original_text

ФОРМАТ ОТВЕТА (строго JSON):
{{
  "rooms": [
    {{
      "name": "название комнаты",
      "area": площадь_число,
      "items": [
        {{
          "price_item_id": ID_из_прайса_или_null,
          "name": "название позиции",
          "unit": "ед.изм",
          "quantity": количество_число,
          "price": цена_число
        }}
      ]
    }}
  ],
  "unknown_items": [
    {{ "original_text": "Название ненайденной позиции" }}
  ]
}}

ПРИМЕР: Если упомянуто "полотно бауф" но в прайсе нет такой позиции, добавь:
"unknown_items": [{{"original_text": "полотно бауф"}}]
"""

    def _parse_response(self, response_text: str, price_items: List[PriceItem]) -> Dict[str, Any]:
        clean_text = response_text.strip()
        if "```json" in clean_text:
             clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
             clean_text = clean_text.split("```")[1].split("```")[0].strip()

        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError:
            return {"rooms": [], "unknown_items": [], "error": "Failed to parse AI response"}
            
        # Sanitize unknown_items (convert strings to objects if needed)
        unknown_items = data.get("unknown_items", [])
        sanitized_unknown = []
        for item in unknown_items:
            if isinstance(item, str):
                sanitized_unknown.append({"original_text": item})
            elif isinstance(item, dict):
                sanitized_unknown.append(item)
        data["unknown_items"] = sanitized_unknown
            
        # Calculate totals
        total_area = 0
        total_sum = 0
        items_map = {item.id: item for item in price_items}

        for room in data.get("rooms", []):
            room_subtotal = 0
            area_val = room.get("area")
            total_area += float(area_val) if area_val is not None else 0
            for item in room.get("items", []):
                if item.get("price_item_id") and item["price_item_id"] in items_map:
                    price_item = items_map[item["price_item_id"]]
                    item["price"] = float(price_item.price)
                    item["name"] = price_item.name
                    item["unit"] = price_item.unit
                
                qty = item.get("quantity")
                price = item.get("price")
                item["sum"] = round((float(qty) if qty is not None else 0) * (float(price) if price is not None else 0), 2)
                room_subtotal += item["sum"]
            
            room["subtotal"] = room_subtotal
            total_sum += room_subtotal
            
        data["total_area"] = total_area
        data["total_sum"] = total_sum
        return data

ai_parser_service = AIParserService()
