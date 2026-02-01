"""Enhanced PDF generation service for portfolios and quotations.

This service provides professional-grade PDF generation with:
- Cover pages with Kompass branding
- Product pages with images (placeholders)
- QR codes linking to digital versions
- Page numbers on all pages
- Professional headers and footers
- Pricing breakdowns for quotations
"""

import io
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import qrcode
from qrcode.image.pil import PilImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# =============================================================================
# BRANDING CONSTANTS
# =============================================================================

# Colors (Material Design palette matching frontend)
PRIMARY_COLOR = colors.HexColor("#1976d2")
PRIMARY_DARK = colors.HexColor("#1565c0")
SECONDARY_COLOR = colors.HexColor("#424242")
TEXT_PRIMARY = colors.HexColor("#212121")
TEXT_SECONDARY = colors.HexColor("#757575")
BACKGROUND_LIGHT = colors.HexColor("#f5f5f5")
BORDER_COLOR = colors.HexColor("#e0e0e0")
SUCCESS_COLOR = colors.HexColor("#4caf50")
WHITE = colors.white

# Page layout
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 0.75 * inch
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)

# Font sizes
FONT_TITLE = 28
FONT_SUBTITLE = 16
FONT_HEADING = 14
FONT_BODY = 10
FONT_SMALL = 9
FONT_FOOTER = 8

# Company branding
COMPANY_NAME = "Kompass"
COMPANY_TAGLINE = "Your Global Trade Partner"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_qr_code(url: str, size: int = 100) -> io.BytesIO:
    """Generate a QR code image for the given URL.

    Args:
        url: The URL to encode in the QR code
        size: Size of the QR code in pixels

    Returns:
        BytesIO buffer containing the QR code PNG image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")

    # Resize to requested size
    img = img.resize((size, size))

    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def create_styles() -> Dict[str, ParagraphStyle]:
    """Create a consistent set of paragraph styles for PDF documents.

    Returns:
        Dictionary of named ParagraphStyle objects
    """
    base_styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "PDFTitle",
            parent=base_styles["Heading1"],
            fontSize=FONT_TITLE,
            spaceAfter=12,
            textColor=PRIMARY_COLOR,
            alignment=1,  # Center
        ),
        "subtitle": ParagraphStyle(
            "PDFSubtitle",
            parent=base_styles["Normal"],
            fontSize=FONT_SUBTITLE,
            spaceAfter=8,
            textColor=TEXT_SECONDARY,
            alignment=1,  # Center
        ),
        "heading": ParagraphStyle(
            "PDFHeading",
            parent=base_styles["Heading2"],
            fontSize=FONT_HEADING,
            spaceBefore=16,
            spaceAfter=10,
            textColor=TEXT_PRIMARY,
        ),
        "body": ParagraphStyle(
            "PDFBody",
            parent=base_styles["Normal"],
            fontSize=FONT_BODY,
            spaceAfter=6,
            textColor=TEXT_PRIMARY,
        ),
        "small": ParagraphStyle(
            "PDFSmall",
            parent=base_styles["Normal"],
            fontSize=FONT_SMALL,
            spaceAfter=4,
            textColor=TEXT_SECONDARY,
        ),
        "footer": ParagraphStyle(
            "PDFFooter",
            parent=base_styles["Normal"],
            fontSize=FONT_FOOTER,
            textColor=TEXT_SECONDARY,
            alignment=1,  # Center
        ),
        "centered": ParagraphStyle(
            "PDFCentered",
            parent=base_styles["Normal"],
            fontSize=FONT_BODY,
            alignment=1,  # Center
            textColor=TEXT_PRIMARY,
        ),
        "right": ParagraphStyle(
            "PDFRight",
            parent=base_styles["Normal"],
            fontSize=FONT_BODY,
            alignment=2,  # Right
            textColor=TEXT_PRIMARY,
        ),
        "bold": ParagraphStyle(
            "PDFBold",
            parent=base_styles["Normal"],
            fontSize=FONT_BODY,
            fontName="Helvetica-Bold",
            textColor=TEXT_PRIMARY,
        ),
        "grand_total": ParagraphStyle(
            "PDFGrandTotal",
            parent=base_styles["Normal"],
            fontSize=FONT_HEADING,
            fontName="Helvetica-Bold",
            textColor=PRIMARY_COLOR,
        ),
    }


def _truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to a maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def _safe_get(data: Dict[str, Any], key: str, default: Any = "") -> Any:
    """Safely get a value from a dictionary with a default.

    Args:
        data: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found or value is None

    Returns:
        The value or default
    """
    value = data.get(key)
    return value if value is not None else default


# =============================================================================
# PORTFOLIO PDF GENERATOR
# =============================================================================


class PortfolioPDFGenerator:
    """Generate enhanced PDF documents for portfolios.

    Features:
    - Cover page with portfolio name, niche, and Kompass branding
    - Product listing pages with name, SKU, description
    - QR code linking to share URL
    - Page numbers on all pages
    """

    def __init__(self, portfolio: Dict[str, Any], share_url: Optional[str] = None):
        """Initialize the portfolio PDF generator.

        Args:
            portfolio: Portfolio data dictionary with items
            share_url: Optional URL for the portfolio share link (for QR code)
        """
        self.portfolio = portfolio
        self.share_url = share_url
        self.styles = create_styles()
        self.page_count = 0

    def _create_cover_page(self) -> List:
        """Create the cover page elements.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []

        # Top spacer for centering
        elements.append(Spacer(1, 2 * inch))

        # Company branding
        elements.append(Paragraph(COMPANY_NAME, self.styles["title"]))
        elements.append(Paragraph(COMPANY_TAGLINE, self.styles["subtitle"]))
        elements.append(Spacer(1, inch))

        # Portfolio name
        portfolio_name = _safe_get(self.portfolio, "name", "Portfolio")
        title_style = ParagraphStyle(
            "CoverTitle",
            parent=self.styles["title"],
            fontSize=32,
            textColor=TEXT_PRIMARY,
        )
        elements.append(Paragraph(portfolio_name, title_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Niche name if available
        niche_name = _safe_get(self.portfolio, "niche_name")
        if niche_name:
            elements.append(Paragraph(f"Niche: {niche_name}", self.styles["subtitle"]))

        # Description
        description = _safe_get(self.portfolio, "description")
        if description:
            elements.append(Spacer(1, 0.5 * inch))
            desc_style = ParagraphStyle(
                "CoverDescription",
                parent=self.styles["body"],
                alignment=1,  # Center
                textColor=TEXT_SECONDARY,
            )
            elements.append(Paragraph(description, desc_style))

        elements.append(Spacer(1, inch))

        # Product count
        items = _safe_get(self.portfolio, "items", [])
        item_count = len(items)
        elements.append(
            Paragraph(f"{item_count} Product{'s' if item_count != 1 else ''}", self.styles["subtitle"])
        )

        # Generation date
        elements.append(Spacer(1, 0.5 * inch))
        timestamp = datetime.utcnow().strftime("%B %d, %Y")
        elements.append(Paragraph(f"Generated: {timestamp}", self.styles["small"]))

        # QR code if share URL available
        if self.share_url:
            elements.append(Spacer(1, 0.5 * inch))
            try:
                qr_buffer = create_qr_code(self.share_url, size=80)
                qr_image = Image(qr_buffer, width=1 * inch, height=1 * inch)
                # Wrap in table for centering
                qr_table = Table([[qr_image]], colWidths=[CONTENT_WIDTH])
                qr_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
                elements.append(qr_table)
                elements.append(Paragraph("Scan for digital version", self.styles["small"]))
            except Exception as e:
                print(f"WARN [PDFService]: Failed to generate QR code: {e}")

        # Page break for content
        elements.append(PageBreak())

        return elements

    def _create_product_pages(self) -> List:
        """Create the product listing pages.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        items = _safe_get(self.portfolio, "items", [])

        if not items:
            elements.append(Paragraph("Products", self.styles["heading"]))
            elements.append(
                Paragraph("No products have been added to this portfolio yet.", self.styles["body"])
            )
            return elements

        # Section header
        elements.append(Paragraph("Products", self.styles["heading"]))
        elements.append(Spacer(1, 0.25 * inch))

        # Table header
        table_data = [["#", "Product Name", "SKU", "Description"]]

        # Table rows
        for idx, item in enumerate(items, 1):
            product_name = _truncate_text(_safe_get(item, "product_name", "N/A"), 40)
            product_sku = _safe_get(item, "product_sku", "N/A")
            description = _truncate_text(_safe_get(item, "notes", "-"), 50)

            table_data.append([str(idx), product_name, product_sku, description])

        # Create table
        col_widths = [0.4 * inch, 2.5 * inch, 1.2 * inch, 2.4 * inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    # Header styling
                    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("TOPPADDING", (0, 0), (-1, 0), 10),
                    # Data row styling
                    ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                    ("TOPPADDING", (0, 1), (-1, -1), 8),
                    # Alternating row colors
                    *[
                        ("BACKGROUND", (0, i), (-1, i), BACKGROUND_LIGHT)
                        for i in range(2, len(table_data), 2)
                    ],
                    # Grid
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    # Alignment
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 0), (2, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(table)

        return elements

    def _page_header_footer(
        self, canvas: Any, doc: Any
    ) -> None:
        """Draw page header and footer with page numbers.

        Args:
            canvas: ReportLab canvas object
            doc: ReportLab document object
        """
        canvas.saveState()

        # Footer with page number
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.setFont("Helvetica", FONT_FOOTER)
        canvas.setFillColor(TEXT_SECONDARY)
        canvas.drawCentredString(PAGE_WIDTH / 2, 0.5 * inch, footer_text)

        # Header with company name (except cover page)
        if page_num > 1:
            canvas.setFont("Helvetica", FONT_SMALL)
            canvas.setFillColor(TEXT_SECONDARY)
            canvas.drawString(MARGIN, PAGE_HEIGHT - 0.5 * inch, COMPANY_NAME)

            # Portfolio name on right
            portfolio_name = _safe_get(self.portfolio, "name", "")
            if portfolio_name:
                canvas.drawRightString(
                    PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 0.5 * inch, portfolio_name
                )

        canvas.restoreState()

    def generate(self) -> bytes:
        """Generate the complete portfolio PDF.

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )

        # Build elements
        elements = []
        elements.extend(self._create_cover_page())
        elements.extend(self._create_product_pages())

        # Build PDF with page numbers
        doc.build(elements, onFirstPage=self._page_header_footer, onLaterPages=self._page_header_footer)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        items = _safe_get(self.portfolio, "items", [])
        print(
            f"INFO [PDFService]: Generated portfolio PDF "
            f"({len(pdf_bytes)} bytes, {len(items)} products)"
        )

        return pdf_bytes


# =============================================================================
# QUOTATION PDF GENERATOR
# =============================================================================


class QuotationPDFGenerator:
    """Generate enhanced PDF documents for quotations (Proforma Invoice).

    Features:
    - Professional header with company branding
    - Client information section
    - Quotation metadata (number, date, validity)
    - Product table with quantities and prices
    - Pricing breakdown (subtotal, freight, insurance, total)
    - Terms and conditions section
    - Footer with contact information and timestamp
    - Page numbers on all pages
    """

    def __init__(self, quotation: Dict[str, Any]):
        """Initialize the quotation PDF generator.

        Args:
            quotation: Quotation data dictionary with items
        """
        self.quotation = quotation
        self.styles = create_styles()

    def _create_header(self) -> List:
        """Create the document header section.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []

        # Company logo placeholder and title in a table
        header_data = [
            [
                Paragraph(COMPANY_NAME, self.styles["title"]),
                Paragraph("PROFORMA INVOICE", self.styles["heading"]),
            ]
        ]
        header_table = Table(header_data, colWidths=[3 * inch, 3.5 * inch])
        header_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(header_table)
        elements.append(Spacer(1, 0.25 * inch))

        # Quotation info and client info side by side
        quotation_number = _safe_get(self.quotation, "quotation_number", "N/A")
        status = _safe_get(self.quotation, "status", "draft").title()
        valid_from = _safe_get(self.quotation, "valid_from", "N/A")
        valid_until = _safe_get(self.quotation, "valid_until", "N/A")
        incoterm = _safe_get(self.quotation, "incoterm", "N/A")

        # Format dates if they are date objects
        if hasattr(valid_from, "strftime"):
            valid_from = valid_from.strftime("%Y-%m-%d")
        if hasattr(valid_until, "strftime"):
            valid_until = valid_until.strftime("%Y-%m-%d")

        # Left side: Quotation details
        left_content = [
            Paragraph(f"<b>Quotation #:</b> {quotation_number}", self.styles["body"]),
            Paragraph(f"<b>Status:</b> {status}", self.styles["body"]),
            Paragraph(f"<b>Incoterm:</b> {incoterm}", self.styles["body"]),
            Paragraph(f"<b>Valid From:</b> {valid_from}", self.styles["body"]),
            Paragraph(f"<b>Valid Until:</b> {valid_until}", self.styles["body"]),
        ]

        # Right side: Client details
        client_name = _safe_get(self.quotation, "client_name", "N/A")
        client_email = _safe_get(self.quotation, "client_email", "")
        client_phone = _safe_get(self.quotation, "client_phone", "")
        client_address = _safe_get(self.quotation, "client_address", "")

        right_content = [
            Paragraph("<b>Bill To:</b>", self.styles["body"]),
            Paragraph(client_name, self.styles["bold"]),
        ]
        if client_email:
            right_content.append(Paragraph(client_email, self.styles["small"]))
        if client_phone:
            right_content.append(Paragraph(client_phone, self.styles["small"]))
        if client_address:
            right_content.append(Paragraph(client_address, self.styles["small"]))

        # Combine left and right in a table
        info_table = Table(
            [[left_content, right_content]],
            colWidths=[3.25 * inch, 3.25 * inch],
        )
        info_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ]
            )
        )
        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * inch))

        return elements

    def _create_items_table(self) -> List:
        """Create the line items table.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        items = _safe_get(self.quotation, "items", [])
        currency = _safe_get(self.quotation, "currency", "USD")

        elements.append(Paragraph("Line Items", self.styles["heading"]))
        elements.append(Spacer(1, 0.15 * inch))

        if not items:
            elements.append(
                Paragraph("No line items have been added to this quotation.", self.styles["body"])
            )
            return elements

        # Table header
        table_data = [["#", "Product", "Qty", "Unit", "Unit Price", "Total"]]

        # Table rows
        for idx, item in enumerate(items, 1):
            product_name = _truncate_text(_safe_get(item, "product_name", "N/A"), 35)
            quantity = _safe_get(item, "quantity", 0)
            unit = _safe_get(item, "unit_of_measure", "piece")
            unit_price = _safe_get(item, "unit_price", Decimal("0.00"))
            line_total = _safe_get(item, "line_total", Decimal("0.00"))

            # Format prices
            unit_price_str = f"{currency} {float(unit_price):,.2f}"
            line_total_str = f"{currency} {float(line_total):,.2f}"

            table_data.append(
                [str(idx), product_name, str(quantity), unit, unit_price_str, line_total_str]
            )

        # Create table
        col_widths = [0.35 * inch, 2.3 * inch, 0.5 * inch, 0.6 * inch, 1.2 * inch, 1.2 * inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    # Header styling
                    ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    # Data row styling
                    ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                    ("TOPPADDING", (0, 1), (-1, -1), 6),
                    # Alternating row colors
                    *[
                        ("BACKGROUND", (0, i), (-1, i), BACKGROUND_LIGHT)
                        for i in range(2, len(table_data), 2)
                    ],
                    # Grid
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    # Alignment
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 0), (3, -1), "CENTER"),
                    ("ALIGN", (4, 0), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(table)

        return elements

    def _create_pricing_breakdown(self) -> List:
        """Create the pricing breakdown section.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        currency = _safe_get(self.quotation, "currency", "USD")

        elements.append(Spacer(1, 0.25 * inch))

        # Get pricing values
        subtotal = _safe_get(self.quotation, "subtotal", Decimal("0.00"))
        freight = _safe_get(self.quotation, "freight_cost", Decimal("0.00"))
        insurance = _safe_get(self.quotation, "insurance_cost", Decimal("0.00"))
        other = _safe_get(self.quotation, "other_costs", Decimal("0.00"))
        total = _safe_get(self.quotation, "total", Decimal("0.00"))
        discount_percent = _safe_get(self.quotation, "discount_percent", Decimal("0.00"))
        discount_amount = _safe_get(self.quotation, "discount_amount", Decimal("0.00"))
        grand_total = _safe_get(self.quotation, "grand_total", Decimal("0.00"))

        # Build pricing rows
        pricing_data = [
            ["Subtotal:", f"{currency} {float(subtotal):,.2f}"],
            ["Freight:", f"{currency} {float(freight):,.2f}"],
            ["Insurance:", f"{currency} {float(insurance):,.2f}"],
            ["Other Costs:", f"{currency} {float(other):,.2f}"],
            ["Total:", f"{currency} {float(total):,.2f}"],
        ]

        if float(discount_percent) > 0:
            pricing_data.append(
                [f"Discount ({float(discount_percent):.1f}%):", f"-{currency} {float(discount_amount):,.2f}"]
            )

        pricing_data.append(["Grand Total:", f"{currency} {float(grand_total):,.2f}"])

        # Create pricing table (right-aligned)
        pricing_table = Table(pricing_data, colWidths=[2 * inch, 1.5 * inch])
        pricing_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -2), FONT_BODY),
                    ("FONTSIZE", (0, -1), (-1, -1), FONT_HEADING),
                    ("TEXTCOLOR", (0, -1), (-1, -1), PRIMARY_COLOR),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("LINEABOVE", (0, -1), (-1, -1), 1.5, PRIMARY_COLOR),
                ]
            )
        )

        # Wrap in outer table for right alignment
        wrapper = Table([[None, pricing_table]], colWidths=[3 * inch, 3.5 * inch])
        wrapper.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT")]))
        elements.append(wrapper)

        return elements

    def _create_terms_section(self) -> List:
        """Create the terms and conditions section.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        terms = _safe_get(self.quotation, "terms_and_conditions")
        notes = _safe_get(self.quotation, "notes")
        payment_terms = _safe_get(self.quotation, "payment_terms")

        if payment_terms:
            elements.append(Spacer(1, 0.25 * inch))
            elements.append(Paragraph("Payment Terms", self.styles["heading"]))
            elements.append(Paragraph(payment_terms, self.styles["body"]))

        if terms:
            elements.append(Spacer(1, 0.25 * inch))
            elements.append(Paragraph("Terms and Conditions", self.styles["heading"]))
            elements.append(Paragraph(terms, self.styles["body"]))

        if notes:
            elements.append(Spacer(1, 0.25 * inch))
            elements.append(Paragraph("Notes", self.styles["heading"]))
            elements.append(Paragraph(notes, self.styles["body"]))

        return elements

    def _create_footer_section(self) -> List:
        """Create the footer section with contact info and timestamp.

        Returns:
            List of ReportLab flowable elements
        """
        elements = []

        elements.append(Spacer(1, 0.5 * inch))

        # Horizontal line
        line_table = Table([[""]], colWidths=[CONTENT_WIDTH])
        line_table.setStyle(
            TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER_COLOR)])
        )
        elements.append(line_table)

        elements.append(Spacer(1, 0.15 * inch))

        # Timestamp and item count
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        items = _safe_get(self.quotation, "items", [])
        incoterm = _safe_get(self.quotation, "incoterm", "N/A")

        footer_text = f"Generated on {timestamp} | Incoterm: {incoterm} | {len(items)} item(s)"
        elements.append(Paragraph(footer_text, self.styles["footer"]))

        elements.append(Spacer(1, 0.1 * inch))

        # Company contact
        elements.append(
            Paragraph(f"{COMPANY_NAME} - {COMPANY_TAGLINE}", self.styles["footer"])
        )

        return elements

    def _page_header_footer(self, canvas: Any, doc: Any) -> None:
        """Draw page header and footer with page numbers.

        Args:
            canvas: ReportLab canvas object
            doc: ReportLab document object
        """
        canvas.saveState()

        # Footer with page number
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.setFont("Helvetica", FONT_FOOTER)
        canvas.setFillColor(TEXT_SECONDARY)
        canvas.drawCentredString(PAGE_WIDTH / 2, 0.4 * inch, footer_text)

        canvas.restoreState()

    def generate(self) -> bytes:
        """Generate the complete quotation PDF.

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=0.6 * inch,  # Extra space for page number
        )

        # Build elements
        elements = []
        elements.extend(self._create_header())
        elements.extend(self._create_items_table())
        elements.extend(self._create_pricing_breakdown())
        elements.extend(self._create_terms_section())
        elements.extend(self._create_footer_section())

        # Build PDF with page numbers
        doc.build(elements, onFirstPage=self._page_header_footer, onLaterPages=self._page_header_footer)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        items = _safe_get(self.quotation, "items", [])
        quotation_number = _safe_get(self.quotation, "quotation_number", "N/A")
        print(
            f"INFO [PDFService]: Generated quotation PDF for {quotation_number} "
            f"({len(pdf_bytes)} bytes, {len(items)} items)"
        )

        return pdf_bytes


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def generate_portfolio_pdf(
    portfolio: Dict[str, Any], share_url: Optional[str] = None
) -> bytes:
    """Generate a PDF for a portfolio.

    Args:
        portfolio: Portfolio data dictionary
        share_url: Optional URL for QR code

    Returns:
        PDF content as bytes
    """
    generator = PortfolioPDFGenerator(portfolio, share_url)
    return generator.generate()


def generate_quotation_pdf(quotation: Dict[str, Any]) -> bytes:
    """Generate a PDF for a quotation.

    Args:
        quotation: Quotation data dictionary

    Returns:
        PDF content as bytes
    """
    generator = QuotationPDFGenerator(quotation)
    return generator.generate()
