"""Unit tests for PDF generation service."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.services.pdf_service import (
    PortfolioPDFGenerator,
    QuotationPDFGenerator,
    create_qr_code,
    create_styles,
    generate_portfolio_pdf,
    generate_quotation_pdf,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_portfolio():
    """Sample portfolio data for testing."""
    return {
        "id": uuid4(),
        "name": "Ceramic Tiles Collection",
        "description": "Premium ceramic tiles for residential and commercial use.",
        "niche_id": uuid4(),
        "niche_name": "Construction Materials",
        "is_active": True,
        "items": [
            {
                "id": uuid4(),
                "product_id": uuid4(),
                "product_name": "White Marble Tile 60x60",
                "product_sku": "CER-WM-6060",
                "sort_order": 0,
                "notes": "High-gloss finish",
            },
            {
                "id": uuid4(),
                "product_id": uuid4(),
                "product_name": "Gray Granite Tile 45x45",
                "product_sku": "CER-GG-4545",
                "sort_order": 1,
                "notes": "Matte finish, anti-slip",
            },
            {
                "id": uuid4(),
                "product_id": uuid4(),
                "product_name": "Beige Porcelain Tile 30x60",
                "product_sku": "CER-BP-3060",
                "sort_order": 2,
                "notes": None,
            },
        ],
        "item_count": 3,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def sample_portfolio_empty():
    """Sample portfolio with no items."""
    return {
        "id": uuid4(),
        "name": "Empty Portfolio",
        "description": "A portfolio with no products yet.",
        "niche_id": None,
        "niche_name": None,
        "is_active": True,
        "items": [],
        "item_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def sample_quotation():
    """Sample quotation data for testing."""
    return {
        "id": uuid4(),
        "quotation_number": "QT-2024-0001",
        "client_id": uuid4(),
        "client_name": "Acme Corporation",
        "client_email": "purchasing@acme.com",
        "client_phone": "+1 555 123 4567",
        "client_address": "123 Business Ave, Commerce City, CA 90210",
        "status": "sent",
        "incoterm": "FOB",
        "currency": "USD",
        "subtotal": Decimal("5000.00"),
        "freight_cost": Decimal("450.00"),
        "insurance_cost": Decimal("75.00"),
        "other_costs": Decimal("25.00"),
        "total": Decimal("5550.00"),
        "discount_percent": Decimal("5.00"),
        "discount_amount": Decimal("277.50"),
        "grand_total": Decimal("5272.50"),
        "notes": "Please review and confirm availability.",
        "terms_and_conditions": "Payment due within 30 days of invoice.",
        "payment_terms": "Net 30",
        "valid_from": date.today(),
        "valid_until": date.today(),
        "created_by": uuid4(),
        "items": [
            {
                "id": uuid4(),
                "quotation_id": uuid4(),
                "product_id": uuid4(),
                "product_name": "White Marble Tile 60x60",
                "product_sku": "CER-WM-6060",
                "quantity": 100,
                "unit_of_measure": "sqm",
                "unit_price": Decimal("25.00"),
                "line_total": Decimal("2500.00"),
            },
            {
                "id": uuid4(),
                "quotation_id": uuid4(),
                "product_id": uuid4(),
                "product_name": "Gray Granite Tile 45x45",
                "product_sku": "CER-GG-4545",
                "quantity": 200,
                "unit_of_measure": "sqm",
                "unit_price": Decimal("12.50"),
                "line_total": Decimal("2500.00"),
            },
        ],
        "item_count": 2,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def sample_quotation_empty():
    """Sample quotation with no items."""
    return {
        "id": uuid4(),
        "quotation_number": "QT-2024-0002",
        "client_id": uuid4(),
        "client_name": "Empty Client",
        "client_email": None,
        "client_phone": None,
        "client_address": None,
        "status": "draft",
        "incoterm": "EXW",
        "currency": "EUR",
        "subtotal": Decimal("0.00"),
        "freight_cost": Decimal("0.00"),
        "insurance_cost": Decimal("0.00"),
        "other_costs": Decimal("0.00"),
        "total": Decimal("0.00"),
        "discount_percent": Decimal("0.00"),
        "discount_amount": Decimal("0.00"),
        "grand_total": Decimal("0.00"),
        "notes": None,
        "terms_and_conditions": None,
        "payment_terms": None,
        "valid_from": None,
        "valid_until": None,
        "created_by": uuid4(),
        "items": [],
        "item_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


# =============================================================================
# QR CODE TESTS
# =============================================================================


class TestQRCodeGeneration:
    """Tests for QR code generation utility."""

    def test_create_qr_code_returns_bytes(self):
        """Test that QR code generation returns a BytesIO buffer."""
        url = "https://example.com/portfolio/share/abc123"
        result = create_qr_code(url)

        assert result is not None
        assert hasattr(result, "read")
        # Should be a valid PNG (starts with PNG magic bytes)
        content = result.read()
        assert content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_create_qr_code_with_custom_size(self):
        """Test QR code generation with custom size."""
        url = "https://example.com/test"
        result = create_qr_code(url, size=200)

        assert result is not None
        content = result.read()
        assert len(content) > 0

    def test_create_qr_code_with_long_url(self):
        """Test QR code generation with a very long URL."""
        url = "https://example.com/" + "a" * 500
        result = create_qr_code(url)

        assert result is not None
        content = result.read()
        assert len(content) > 0


# =============================================================================
# STYLES TESTS
# =============================================================================


class TestCreateStyles:
    """Tests for style creation utility."""

    def test_create_styles_returns_dict(self):
        """Test that create_styles returns a dictionary."""
        styles = create_styles()

        assert isinstance(styles, dict)
        assert len(styles) > 0

    def test_create_styles_contains_expected_keys(self):
        """Test that styles contains all expected style keys."""
        styles = create_styles()

        expected_keys = [
            "title",
            "subtitle",
            "heading",
            "body",
            "small",
            "footer",
            "centered",
            "right",
            "bold",
            "grand_total",
        ]
        for key in expected_keys:
            assert key in styles, f"Missing style: {key}"


# =============================================================================
# PORTFOLIO PDF GENERATOR TESTS
# =============================================================================


class TestPortfolioPDFGenerator:
    """Tests for PortfolioPDFGenerator class."""

    def test_generate_returns_bytes(self, sample_portfolio):
        """Test that PDF generation returns bytes."""
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_starts_with_pdf_header(self, sample_portfolio):
        """Test that generated PDF has proper PDF header."""
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        # PDF files start with %PDF-
        assert result[:5] == b"%PDF-"

    def test_pdf_size_reflects_content(self, sample_portfolio):
        """Test that PDF with content is larger than empty PDF."""
        generator_with_items = PortfolioPDFGenerator(sample_portfolio)
        result_with_items = generator_with_items.generate()

        empty_portfolio = sample_portfolio.copy()
        empty_portfolio["items"] = []
        generator_empty = PortfolioPDFGenerator(empty_portfolio)
        result_empty = generator_empty.generate()

        # PDF with items should have different size (likely larger)
        assert len(result_with_items) != len(result_empty)

    def test_pdf_with_multiple_products(self, sample_portfolio):
        """Test PDF generation with multiple products."""
        assert len(sample_portfolio["items"]) == 3
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 1000  # Should be reasonably sized

    def test_pdf_with_empty_portfolio(self, sample_portfolio_empty):
        """Test PDF generation with empty portfolio."""
        generator = PortfolioPDFGenerator(sample_portfolio_empty)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result[:5] == b"%PDF-"

    def test_pdf_with_share_url_is_larger(self, sample_portfolio):
        """Test that providing a share URL produces a larger PDF (includes QR code)."""
        generator_without_qr = PortfolioPDFGenerator(sample_portfolio, share_url=None)
        result_without_qr = generator_without_qr.generate()

        share_url = "https://example.com/portfolios/share/test-token"
        generator_with_qr = PortfolioPDFGenerator(sample_portfolio, share_url=share_url)
        result_with_qr = generator_with_qr.generate()

        # PDF with QR code should be larger
        assert len(result_with_qr) > len(result_without_qr)

    def test_pdf_with_niche_name(self, sample_portfolio):
        """Test that PDF generates successfully with niche name."""
        assert sample_portfolio["niche_name"] == "Construction Materials"
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_generation_completes(self, sample_portfolio):
        """Test that PDF generation completes without error."""
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        # PDF should have proper footer marker
        assert b"%%EOF" in result


class TestGeneratePortfolioPDF:
    """Tests for generate_portfolio_pdf convenience function."""

    def test_generate_portfolio_pdf_returns_bytes(self, sample_portfolio):
        """Test convenience function returns bytes."""
        result = generate_portfolio_pdf(sample_portfolio)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_portfolio_pdf_with_share_url(self, sample_portfolio):
        """Test convenience function with share URL."""
        share_url = "https://example.com/share/abc"
        result = generate_portfolio_pdf(sample_portfolio, share_url=share_url)

        assert isinstance(result, bytes)
        assert len(result) > 0


# =============================================================================
# QUOTATION PDF GENERATOR TESTS
# =============================================================================


class TestQuotationPDFGenerator:
    """Tests for QuotationPDFGenerator class."""

    def test_generate_returns_bytes(self, sample_quotation):
        """Test that PDF generation returns bytes."""
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_starts_with_pdf_header(self, sample_quotation):
        """Test that generated PDF has proper PDF header."""
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert result[:5] == b"%PDF-"

    def test_pdf_with_quotation_data(self, sample_quotation):
        """Test that PDF is generated with quotation data."""
        assert sample_quotation["quotation_number"] == "QT-2024-0001"
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 1000  # Should be reasonably sized

    def test_pdf_with_client_info(self, sample_quotation):
        """Test that PDF generates with client information."""
        assert sample_quotation["client_name"] == "Acme Corporation"
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_size_with_line_items(self, sample_quotation):
        """Test that PDF with items differs from empty PDF."""
        generator_with_items = QuotationPDFGenerator(sample_quotation)
        result_with_items = generator_with_items.generate()

        empty_quotation = sample_quotation.copy()
        empty_quotation["items"] = []
        generator_empty = QuotationPDFGenerator(empty_quotation)
        result_empty = generator_empty.generate()

        # PDF with items should be different size
        assert len(result_with_items) != len(result_empty)

    def test_pdf_generation_produces_valid_pdf(self, sample_quotation):
        """Test that generated PDF has proper structure."""
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        # Should have proper PDF markers
        assert result[:5] == b"%PDF-"
        assert b"%%EOF" in result

    def test_pdf_with_empty_quotation(self, sample_quotation_empty):
        """Test PDF generation with empty quotation (no items)."""
        generator = QuotationPDFGenerator(sample_quotation_empty)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0
        assert result[:5] == b"%PDF-"

    def test_pdf_with_terms_and_conditions(self, sample_quotation):
        """Test that PDF generates with terms and conditions."""
        assert sample_quotation["terms_and_conditions"] is not None
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_with_pricing_data(self, sample_quotation):
        """Test that PDF generates with pricing breakdown."""
        assert sample_quotation["subtotal"] == Decimal("5000.00")
        assert sample_quotation["grand_total"] == Decimal("5272.50")
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_generation_completes(self, sample_quotation):
        """Test that PDF generation completes without error."""
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        # PDF should have proper structure
        assert b"%%EOF" in result


class TestGenerateQuotationPDF:
    """Tests for generate_quotation_pdf convenience function."""

    def test_generate_quotation_pdf_returns_bytes(self, sample_quotation):
        """Test convenience function returns bytes."""
        result = generate_quotation_pdf(sample_quotation)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_quotation_pdf_empty(self, sample_quotation_empty):
        """Test convenience function with empty quotation."""
        result = generate_quotation_pdf(sample_quotation_empty)

        assert isinstance(result, bytes)
        assert len(result) > 0


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_portfolio_with_long_product_names(self, sample_portfolio):
        """Test PDF generation with very long product names."""
        sample_portfolio["items"][0]["product_name"] = "A" * 200
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_portfolio_with_special_characters(self, sample_portfolio):
        """Test PDF generation with special characters in text."""
        sample_portfolio["name"] = "Portfolio with <special> & \"characters\""
        sample_portfolio["description"] = "Contains ampersand & angle brackets < >"
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_quotation_with_zero_discount(self, sample_quotation):
        """Test PDF generation with zero discount."""
        sample_quotation["discount_percent"] = Decimal("0.00")
        sample_quotation["discount_amount"] = Decimal("0.00")
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_quotation_with_missing_optional_fields(self, sample_quotation):
        """Test PDF generation with missing optional fields."""
        sample_quotation["client_email"] = None
        sample_quotation["client_phone"] = None
        sample_quotation["client_address"] = None
        sample_quotation["notes"] = None
        sample_quotation["terms_and_conditions"] = None
        sample_quotation["payment_terms"] = None
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_portfolio_with_many_items(self, sample_portfolio):
        """Test PDF generation with many items (pagination)."""
        # Add 50 items to test pagination
        for i in range(50):
            sample_portfolio["items"].append({
                "id": uuid4(),
                "product_id": uuid4(),
                "product_name": f"Product {i + 4}",
                "product_sku": f"SKU-{i + 4:04d}",
                "sort_order": i + 3,
                "notes": f"Notes for product {i + 4}",
            })
        generator = PortfolioPDFGenerator(sample_portfolio)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_quotation_with_many_items(self, sample_quotation):
        """Test PDF generation with many line items."""
        # Add 50 items to test pagination
        for i in range(50):
            sample_quotation["items"].append({
                "id": uuid4(),
                "quotation_id": sample_quotation["id"],
                "product_id": uuid4(),
                "product_name": f"Line Item {i + 3}",
                "product_sku": f"LI-{i + 3:04d}",
                "quantity": i + 1,
                "unit_of_measure": "piece",
                "unit_price": Decimal("10.00"),
                "line_total": Decimal(str((i + 1) * 10)),
            })
        generator = QuotationPDFGenerator(sample_quotation)
        result = generator.generate()

        assert isinstance(result, bytes)
        assert len(result) > 0
