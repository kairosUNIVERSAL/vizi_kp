import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from app.models import Estimate, Company
import os
import logging

logger = logging.getLogger(__name__)

# Регистрация шрифтов для поддержки кириллицы
FONT_NAME = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

try:
    # Путь в Docker контейнере (Debian/Ubuntu)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",  # Alpine
        "C:\\Windows\\Fonts\\arial.ttf"  # Windows
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        bold_path = font_path.replace('.ttf', '-Bold.ttf')
        if os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
            FONT_BOLD = 'DejaVuSans-Bold'
        else:
            FONT_BOLD = 'DejaVuSans'
        FONT_NAME = 'DejaVuSans'
        logger.info(f"Loaded font from: {font_path}")
    else:
        logger.warning("DejaVu fonts not found, using Helvetica")
except Exception as e:
    logger.exception(f"Error registering fonts: {e}")

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='RussianTitle',
            fontName=FONT_BOLD,
            fontSize=16,
            leading=20,
            alignment=1,
            spaceAfter=15,
            textColor=colors.HexColor('#1e40af') # Dark blue
        ))
        self.styles.add(ParagraphStyle(
            name='RussianHeader',
            fontName=FONT_BOLD,
            fontSize=12,
            leading=14,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='RussianBody',
            fontName=FONT_NAME,
            fontSize=10,
            leading=12
        ))
        self.styles.add(ParagraphStyle(
            name='RussianBold',
            fontName=FONT_BOLD,
            fontSize=10,
            leading=12
        ))
        self.styles.add(ParagraphStyle(
            name='RussianSmall',
            fontName=FONT_NAME,
            fontSize=8,
            leading=10,
            textColor=colors.grey
        ))

    def generate(self, estimate: Estimate, company: Company) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        elements = []

        # 1. Заголовок и Логотип
        self._add_header(elements, company)

        # 2. Данные клиента
        self._add_client_info(elements, estimate)
        
        # 3. Разделение позиций на категории
        main_items_by_room = {} # room_name: [items]
        equip_items_by_room = {} # room_name: [items]
        
        rooms = list(estimate.rooms) if estimate.rooms else []
        for room in rooms:
            if not room.items: continue
            
            m_items = []
            e_items = []
            
            for item in room.items:
                is_equipment = False
                if item.price_item and item.price_item.category and item.price_item.category.is_equipment:
                    is_equipment = True
                
                if is_equipment:
                    e_items.append(item)
                else:
                    m_items.append(item)
            
            if m_items:
                main_items_by_room[room] = m_items
            if e_items:
                equip_items_by_room[room] = e_items

        # 4. Основной блок (Потолки и работы)
        subtotal_main = 0
        if main_items_by_room:
            elements.append(Paragraph("ОСНОВНОЙ БЛОК (Потолки и работы)", self.styles['RussianHeader']))
            elements.append(Spacer(1, 0.2*cm))
            subtotal_main = self._add_items_table(elements, main_items_by_room)
            elements.append(Spacer(1, 0.5*cm))

        # 5. Блок оборудования
        subtotal_equip = 0
        if equip_items_by_room:
            elements.append(Paragraph("ДОПОЛНИТЕЛЬНОЕ ОБОРУДОВАНИЕ И ОСВЕЩЕНИЕ", self.styles['RussianHeader']))
            elements.append(Spacer(1, 0.2*cm))
            subtotal_equip = self._add_items_table(elements, equip_items_by_room)
            elements.append(Spacer(1, 0.5*cm))

        # 6. Расчет итогов со скидками
        discount_main_percent = float(estimate.discount_pr_work or 0)
        discount_equip_percent = float(estimate.discount_equipment or 0)
        
        subtotal_main = float(subtotal_main)
        subtotal_equip = float(subtotal_equip)
        
        discount_main_sum = subtotal_main * (discount_main_percent / 100)
        discount_equip_sum = subtotal_equip * (discount_equip_percent / 100)
        
        total_main = subtotal_main - discount_main_sum
        total_equip = subtotal_equip - discount_equip_sum
        
        grand_total = total_main + total_equip

        # 7. Итоговая таблица
        self._add_summary(elements, subtotal_main, discount_main_percent, discount_main_sum, 
                          subtotal_equip, discount_equip_percent, discount_equip_sum, grand_total)

        # 8. Блок гарантий и реквизитов
        self._add_footer(elements, company)

        # Build PDF
        doc.build(elements)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def _add_header(self, elements, company):
        # Логотип (если есть)
        logo = None
        if company.logo_path and os.path.exists(company.logo_path):
            try:
                logo = Image(company.logo_path)
                # Масштабирование логотипа (макс. ширина 4см, макс. высота 2см)
                aspect = logo.imageWidth / logo.imageHeight
                logo.drawHeight = 2.0*cm
                logo.drawWidth = 2.0*cm * aspect
                if logo.drawWidth > 5.0*cm: # Если слишком широкий
                    logo.drawWidth = 5.0*cm
                    logo.drawHeight = 5.0*cm / aspect
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
                logo = None

        # Формирование информации о компании
        company_address = company.address or company.city or ""
        company_phone = company.phone or ""
        company_email = company.user.email if (company.user and hasattr(company.user, 'email')) else ""
        
        company_info_text = f"<b>{company.name or 'Ceiling KP'}</b><br/>"
        if company_address:
            company_info_text += f"{company_address}<br/>"
        if company_phone:
            company_info_text += f"Тел: {company_phone}<br/>"
        if company_email:
            company_info_text += f"Email: {company_email}<br/>"
        if company.website:
            company_info_text += f"Сайт: {company.website}<br/>"
            
        # Мессенджеры
        if company.messenger_contact:
            m_type = company.messenger_type.capitalize() if company.messenger_type else "Contact"
            company_info_text += f"{m_type}: {company.messenger_contact}"

        info_paragraph = Paragraph(company_info_text, self.styles['RussianBody'])
        
        # Таблица для шапки
        if logo:
            header_table_data = [[logo, info_paragraph]]
            header_table = Table(header_table_data, colWidths=[6*cm, 11*cm])
        else:
            header_table_data = [[info_paragraph]]
            header_table = Table(header_table_data, colWidths=[17*cm])
            
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0.5*cm),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.5*cm))

        # Заголовок документа
        elements.append(Paragraph("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", self.styles['RussianTitle']))
        elements.append(Spacer(1, 0.5*cm))

    def _add_client_info(self, elements, estimate):
        client_data = [
            [Paragraph("<b>Заказчик:</b>", self.styles['RussianBody']), 
             Paragraph(estimate.client_name or "-", self.styles['RussianBody'])],
            [Paragraph("<b>Телефон:</b>", self.styles['RussianBody']), 
             Paragraph(estimate.client_phone or "-", self.styles['RussianBody'])],
            [Paragraph("<b>Адрес:</b>", self.styles['RussianBody']), 
             Paragraph(estimate.client_address or "-", self.styles['RussianBody'])],
            [Paragraph("<b>Дата:</b>", self.styles['RussianBody']), 
             Paragraph(estimate.created_at.strftime('%d.%m.%Y') if estimate.created_at else datetime.now().strftime('%d.%m.%Y'), self.styles['RussianBody'])]
        ]
        client_table = Table(client_data, colWidths=[3*cm, 14*cm])
        client_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.white), # Невидимая сетка для отступов
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        elements.append(client_table)
        elements.append(Spacer(1, 1*cm))

    def _add_items_table(self, elements, items_by_room):
        block_subtotal = 0
        
        for room, items in items_by_room.items():
            # Room Header
            room_area = float(room.area) if room.area else 0
            # Calculate sum for this block's items
            room_block_sum = sum(float(i.sum) if i.sum else float(i.quantity)*float(i.price) for i in items)
            block_subtotal += room_block_sum
            
            elements.append(Paragraph(
                f"Комната: {room.name} (Площадь: {room_area:.1f} м²)",
                self.styles['RussianBold']
            ))
            elements.append(Spacer(1, 0.2*cm))

            # Items Table
            data = [['Наименование', 'Кол-во', 'Ед.', 'Цена', 'Сумма']]
            for item in items:
                quantity = float(item.quantity) if item.quantity else 0
                price = float(item.price) if item.price else 0
                item_sum = float(item.sum) if item.sum else quantity * price
                
                data.append([
                    str(item.name or '-'),
                    f"{quantity:.1f}",
                    str(item.unit or 'шт'),
                    f"{price:,.0f}".replace(',', ' '),
                    f"{item_sum:,.0f}".replace(',', ' ')
                ])
            
            # Room Subtotal for this block
            data.append(['', '', '', 'Подытог:', f"{room_block_sum:,.0f}".replace(',', ' ')])

            table = Table(data, colWidths=[8*cm, 2*cm, 1.5*cm, 2.5*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')), # Dark blue
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
                ('FONTNAME', (0,-1), (-1,-1), FONT_BOLD),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#cbd5e1')), # Light grey border
                ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#1e40af')),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.5*cm))
        
        return block_subtotal

    def _add_summary(self, elements, subtotal_main, discount_main_pct, discount_main_sum, 
                     subtotal_equip, discount_equip_pct, discount_equip_sum, grand_total):
        
        summary_data = []
        
        # Main Block Summary
        if subtotal_main > 0:
            summary_data.append(['Сумма по основным работам:', f"{subtotal_main:,.0f} руб.".replace(',', ' ')])
            if discount_main_pct > 0:
                 summary_data.append([f'Скидка на работы ({discount_main_pct:g}%):', f"-{discount_main_sum:,.0f} руб.".replace(',', ' ')])
                 summary_data.append(['Итого работы со скидкой:', f"{(subtotal_main - discount_main_sum):,.0f} руб.".replace(',', ' ')])

        # Equipment Block Summary
        if subtotal_equip > 0:
            summary_data.append(['Сумма по оборудованию:', f"{subtotal_equip:,.0f} руб.".replace(',', ' ')])
            if discount_equip_pct > 0:
                 summary_data.append([f'Скидка на оборудование ({discount_equip_pct:g}%):', f"-{discount_equip_sum:,.0f} руб.".replace(',', ' ')])
                 summary_data.append(['Итого оборудование со скидкой:', f"{(subtotal_equip - discount_equip_sum):,.0f} руб.".replace(',', ' ')])

        # Grand Total
        summary_data.append(['ВСЕГО К ОПЛАТЕ:', f"{grand_total:,.0f} руб.".replace(',', ' ')])

        summary_table = Table(summary_data, colWidths=[12*cm, 5*cm])
        
        # Apply style based on rows
        table_style = [
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]
        
        # Bold and Font size for the last row (Grand Total)
        last_row_idx = len(summary_data) - 1
        table_style.append(('FONTNAME', (0, last_row_idx), (-1, last_row_idx), FONT_BOLD))
        table_style.append(('FONTSIZE', (0, last_row_idx), (-1, last_row_idx), 14))
        table_style.append(('TEXTCOLOR', (0, last_row_idx), (-1, last_row_idx), colors.HexColor('#1e40af')))
        
        # Background and Box
        table_style.append(('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')))
        table_style.append(('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e40af')))
        table_style.append(('TOPPADDING', (0,0), (-1,-1), 10))
        table_style.append(('BOTTOMPADDING', (0,0), (-1,-1), 10))

        summary_table.setStyle(TableStyle(table_style))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Spacer(1, 1*cm))

    def _add_footer(self, elements, company):
        bottom_elements = []
        
        # Гарантии
        warranty_material = company.warranty_material if company.warranty_material else 15
        warranty_work = company.warranty_work if company.warranty_work else 3
        validity_days = company.validity_days if company.validity_days else 14
        discount = float(company.discount) if company.discount else 5
        
        bottom_elements.append(Paragraph("Гарантийные обязательства:", self.styles['RussianBold']))
        bottom_elements.append(Paragraph(f"- Гарантия на полотно и материалы: {warranty_material} лет", self.styles['RussianBody']))
        bottom_elements.append(Paragraph(f"- Гарантия на монтажные работы: {warranty_work} лет", self.styles['RussianBody']))
        bottom_elements.append(Paragraph(f"- Срок действия предложения: {validity_days} дней", self.styles['RussianBody']))
        bottom_elements.append(Spacer(1, 0.3*cm))
        # Remove old discount generic text if we now have specific discounts?
        # Maybe keep it as "Additional discount for quick decision" text, but remove hard number?
        # Or keep it as generic marketing. The user asked for specific fields.
        # "При заключении договора в день замера — дополнительная скидка..."
        # This seems to be a marketing text, separate from the calculation.
        bottom_elements.append(Paragraph(
            f"<b>При заключении договора в день замера — дополнительная скидка {discount:.0f}%!</b>",
            self.styles['RussianBold']
        ))
        
        # Реквизиты
        if any([company.inn, company.bank_name, company.bank_account]):
            bottom_elements.append(Spacer(1, 0.5*cm))
            bottom_elements.append(Paragraph("РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:", self.styles['RussianBold']))
            
            pay_text = ""
            if company.inn: pay_text += f"ИНН: {company.inn} "
            if company.kpp: pay_text += f" КПП: {company.kpp}"
            if pay_text: pay_text += "<br/>"
            
            if company.bank_name: pay_text += f"Банк: {company.bank_name}<br/>"
            if company.bank_bik: pay_text += f"БИК: {company.bank_bik} "
            if company.bank_corr: pay_text += f" Корр.счет: {company.bank_corr}<br/>"
            if company.bank_account: pay_text += f"Расчетный счет: {company.bank_account}"
            
            bottom_elements.append(Paragraph(pay_text, self.styles['RussianSmall']))

        elements.append(KeepTogether(bottom_elements))
        elements.append(Spacer(1, 1.5*cm))

        # 6. Подписи
        sig_data = [
            ['Заказчик: __________________', 'Исполнитель: __________________'],
            ['(подпись / ФИО)', '(подпись / ФИО)']
        ]
        sig_table = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('ALIGN', (0,1), (0,1), 'LEFT'),
            ('ALIGN', (1,1), (1,1), 'RIGHT'),
            ('FONTSIZE', (0,1), (-1,1), 8),
            ('TOPPADDING', (0,1), (-1,1), 0),
        ]))
        elements.append(sig_table)


pdf_service = PDFService()
