import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
            fontSize=18,
            leading=22,
            alignment=1,
            spaceAfter=20
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

        # 1. Шапка компании
        company_name = company.name if company.name else "Коммерческое предложение"
        elements.append(Paragraph(company_name, self.styles['RussianTitle']))
        
        company_info = []
        if company.phone:
            company_info.append(f"Тел: {company.phone}")
        if company.city:
            company_info.append(f"Город: {company.city}")
        
        date_str = estimate.created_at.strftime('%d.%m.%Y') if estimate.created_at else datetime.now().strftime('%d.%m.%Y')
        company_info.append(f"Дата: {date_str}")
        
        for info in company_info:
            elements.append(Paragraph(info, self.styles['RussianSmall']))
        
        elements.append(Spacer(1, 0.5*cm))

        # 2. Данные клиента
        elements.append(Paragraph("Заказчик:", self.styles['RussianBold']))
        elements.append(Paragraph(f"ФИО: {estimate.client_name or '-'}", self.styles['RussianBody']))
        if estimate.client_phone:
            elements.append(Paragraph(f"Телефон: {estimate.client_phone}", self.styles['RussianBody']))
        if estimate.client_address:
            elements.append(Paragraph(f"Адрес: {estimate.client_address}", self.styles['RussianBody']))
        
        elements.append(Spacer(1, 1*cm))

        # 3. Таблицы по комнатам
        rooms = list(estimate.rooms) if estimate.rooms else []
        
        if not rooms:
            elements.append(Paragraph("Нет позиций в смете", self.styles['RussianBody']))
        else:
            for room in rooms:
                room_area = float(room.area) if room.area else 0
                elements.append(Paragraph(
                    f"Комната: {room.name} (Площадь: {room_area:.1f} м²)",
                    self.styles['RussianBold']
                ))
                elements.append(Spacer(1, 0.2*cm))

                items = list(room.items) if room.items else []
                
                if items:
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
                    
                    room_subtotal = float(room.subtotal) if room.subtotal else 0
                    data.append(['', '', '', 'Итого:', f"{room_subtotal:,.0f}".replace(',', ' ')])

                    table = Table(data, colWidths=[8*cm, 2*cm, 1.5*cm, 2.5*cm, 3*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                        ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
                        ('FONTNAME', (0,-1), (-1,-1), FONT_BOLD),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('BOTTOMPADDING', (0,0), (-1,0), 8),
                        ('BACKGROUND', (0,-1), (-1,-1), colors.whitesmoke),
                        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
                        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
                    ]))
                    elements.append(table)
                else:
                    elements.append(Paragraph("Нет позиций", self.styles['RussianSmall']))
                    
                elements.append(Spacer(1, 0.5*cm))

        elements.append(Spacer(1, 0.5*cm))

        # 4. Итого
        total_sum = float(estimate.total_sum) if estimate.total_sum else 0
        summary_data = [
            [Paragraph(f"<b>ОБЩАЯ СУММА: {total_sum:,.0f} руб.</b>".replace(',', ' '), self.styles['RussianTitle'])]
        ]
        summary_table = Table(summary_data, colWidths=[17*cm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,-1), colors.lightyellow),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 1*cm))

        # 5. Блок гарантий
        warranty_material = company.warranty_material if company.warranty_material else 15
        warranty_work = company.warranty_work if company.warranty_work else 3
        validity_days = company.validity_days if company.validity_days else 14
        discount = float(company.discount) if company.discount else 5
        
        elements.append(Paragraph("Гарантийные обязательства:", self.styles['RussianBold']))
        elements.append(Paragraph(f"- Гарантия на полотно и материалы: {warranty_material} лет", self.styles['RussianBody']))
        elements.append(Paragraph(f"- Гарантия на монтажные работы: {warranty_work} лет", self.styles['RussianBody']))
        elements.append(Paragraph(f"- Срок действия предложения: {validity_days} дней", self.styles['RussianBody']))
        
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Paragraph(
            f"<b>При заключении договора в день замера — дополнительная скидка {discount:.0f}%!</b>",
            self.styles['RussianBold']
        ))

        elements.append(Spacer(1, 2*cm))

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

        # Build PDF
        doc.build(elements)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

pdf_service = PDFService()
