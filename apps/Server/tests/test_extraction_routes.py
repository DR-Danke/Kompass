"""Unit tests for the extraction API routes."""

import io
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.extraction_routes import (
    _create_job,
    _complete_job,
    _fail_job,
    _get_job,
    _job_store,
)
from app.models.extraction_dto import (
    ExtractedProduct,
    HsCodeSuggestion,
    ImageOperation,
    ImageProcessingResult,
)
from app.models.extraction_job_dto import (
    ExtractionJobStatus,
)
from app.api.dependencies import get_current_user
from main import app


@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_viewer_user():
    """Create a mock viewer user (should be denied upload/confirm)."""
    return {
        "id": str(uuid4()),
        "email": "viewer@example.com",
        "role": "viewer",
        "is_active": True,
    }


@pytest.fixture(autouse=True)
def clear_job_store():
    """Clear the job store before each test."""
    _job_store.clear()
    yield
    _job_store.clear()


@pytest.fixture
def authenticated_client(mock_auth_user):
    """Create a test client with mocked authentication."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def viewer_client(mock_viewer_user):
    """Create a test client with viewer role authentication."""
    app.dependency_overrides[get_current_user] = lambda: mock_viewer_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client():
    """Create a test client without authentication."""
    app.dependency_overrides.clear()
    return TestClient(app)


class TestJobStore:
    """Tests for in-memory job store functions."""

    def test_create_job(self):
        """Test creating a new job."""
        job = _create_job(3)

        assert job.job_id is not None
        assert job.status == ExtractionJobStatus.PENDING
        assert job.total_files == 3
        assert job.processed_files == 0
        assert job.progress == 0
        assert len(job.extracted_products) == 0
        assert len(job.errors) == 0

    def test_get_job(self):
        """Test retrieving a job."""
        job = _create_job(2)

        retrieved = _get_job(str(job.job_id))

        assert retrieved is not None
        assert retrieved.job_id == job.job_id

    def test_get_nonexistent_job(self):
        """Test retrieving a nonexistent job."""
        result = _get_job(str(uuid4()))

        assert result is None

    def test_complete_job(self):
        """Test completing a job."""
        job = _create_job(1)
        products = [
            ExtractedProduct(sku="TEST-001", name="Test Product"),
        ]

        _complete_job(str(job.job_id), products, ["minor warning"])

        updated = _get_job(str(job.job_id))
        assert updated.status == ExtractionJobStatus.COMPLETED
        assert updated.progress == 100
        assert len(updated.extracted_products) == 1
        assert updated.extracted_products[0].sku == "TEST-001"

    def test_fail_job(self):
        """Test failing a job."""
        job = _create_job(1)

        _fail_job(str(job.job_id), "Processing failed")

        updated = _get_job(str(job.job_id))
        assert updated.status == ExtractionJobStatus.FAILED
        assert "Processing failed" in updated.errors


class TestUploadEndpoint:
    """Tests for the upload endpoint."""

    def test_upload_no_files_returns_422(self, authenticated_client):
        """Test that uploading no files returns 422 (validation error)."""
        response = authenticated_client.post("/api/extract/upload", files=[])

        # FastAPI returns 422 when required multipart field is empty
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_upload_invalid_file_type_returns_400(self, authenticated_client):
        """Test that uploading invalid file types returns 400."""
        # Create a fake .txt file (not allowed)
        file_content = b"This is a text file"
        files = [("files", ("test.txt", io.BytesIO(file_content), "text/plain"))]

        response = authenticated_client.post("/api/extract/upload", files=files)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not allowed" in response.json()["detail"]

    @patch("app.api.extraction_routes._process_files_background")
    def test_upload_valid_file_creates_job(
        self, mock_process, authenticated_client
    ):
        """Test that uploading valid files creates a job."""
        # Create a fake PDF file
        file_content = b"%PDF-1.4 fake pdf content"
        files = [("files", ("test.pdf", io.BytesIO(file_content), "application/pdf"))]

        response = authenticated_client.post("/api/extract/upload", files=files)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data

        # Verify job was created
        job = _get_job(data["job_id"])
        assert job is not None

    def test_upload_oversized_file_returns_400(self, authenticated_client):
        """Test that uploading oversized files returns 400."""
        # Create a file larger than 20MB
        file_content = b"x" * (21 * 1024 * 1024)  # 21MB
        files = [("files", ("large.pdf", io.BytesIO(file_content), "application/pdf"))]

        response = authenticated_client.post("/api/extract/upload", files=files)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "exceeds maximum size" in response.json()["detail"]


class TestJobStatusEndpoint:
    """Tests for the job status endpoint."""

    def test_get_job_status_returns_job(self, authenticated_client):
        """Test getting job status returns the job."""
        # Create a job
        job = _create_job(2)

        response = authenticated_client.get(f"/api/extract/{job.job_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == str(job.job_id)
        assert data["status"] == "pending"
        assert data["total_files"] == 2

    def test_get_nonexistent_job_returns_404(self, authenticated_client):
        """Test that getting nonexistent job returns 404."""
        fake_id = uuid4()
        response = authenticated_client.get(f"/api/extract/{fake_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestResultsEndpoint:
    """Tests for the results endpoint."""

    def test_get_results_completed_job(self, authenticated_client):
        """Test getting results for a completed job."""
        # Create and complete a job
        job = _create_job(1)
        products = [
            ExtractedProduct(
                sku="RES-001",
                name="Result Product",
                price_fob_usd=Decimal("25.00"),
            ),
        ]
        _complete_job(str(job.job_id), products, [])

        response = authenticated_client.get(f"/api/extract/{job.job_id}/results")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["extracted_products"]) == 1
        assert data["extracted_products"][0]["sku"] == "RES-001"

    def test_get_results_noncompleted_job_returns_400(self, authenticated_client):
        """Test that getting results for non-completed job returns 400."""
        # Create a job (still pending)
        job = _create_job(1)

        response = authenticated_client.get(f"/api/extract/{job.job_id}/results")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not completed" in response.json()["detail"]


class TestConfirmImportEndpoint:
    """Tests for the confirm import endpoint."""

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_import_all_products(
        self, mock_bulk_create, authenticated_client
    ):
        """Test confirming and importing all products."""
        # Mock bulk create response
        mock_response = MagicMock()
        mock_response.success_count = 2
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        # Create and complete a job
        job = _create_job(1)
        products = [
            ExtractedProduct(sku="IMP-001", name="Import Product 1"),
            ExtractedProduct(sku="IMP-002", name="Import Product 2"),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["imported_count"] == 2
        assert data["failed_count"] == 0

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_import_selected_products(
        self, mock_bulk_create, authenticated_client
    ):
        """Test confirming and importing selected products by index."""
        # Mock bulk create response
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        # Create and complete a job
        job = _create_job(1)
        products = [
            ExtractedProduct(sku="SEL-001", name="Selected Product 1"),
            ExtractedProduct(sku="SEL-002", name="Selected Product 2"),
            ExtractedProduct(sku="SEL-003", name="Selected Product 3"),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
                "product_indices": [1],  # Only import the second product
            },
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify only 1 product was passed to bulk_create
        mock_bulk_create.assert_called_once()
        call_args = mock_bulk_create.call_args[0][0]
        assert len(call_args) == 1

    def test_confirm_import_invalid_index_returns_error(self, authenticated_client):
        """Test that invalid product indices return error."""
        # Create and complete a job
        job = _create_job(1)
        products = [ExtractedProduct(sku="INV-001", name="Product")]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
                "product_indices": [999],  # Invalid index
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Invalid product index" in data["errors"][0]

    def test_confirm_import_noncompleted_job_returns_400(self, authenticated_client):
        """Test that confirming import for non-completed job returns 400."""
        # Create a job (still pending)
        job = _create_job(1)

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestConfirmImportFieldMapping:
    """Tests for confirm import field mapping (unit_of_measure, material, category_id)."""

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_maps_unit_of_measure(
        self, mock_bulk_create, authenticated_client
    ):
        """Test unit_of_measure from ExtractedProduct flows to ProductCreateDTO."""
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        job = _create_job(1)
        products = [
            ExtractedProduct(
                sku="UOM-001",
                name="UOM Product",
                unit_of_measure="m2",
            ),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        call_args = mock_bulk_create.call_args[0][0]
        assert call_args[0].unit_of_measure == "m2"

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_appends_material_to_description(
        self, mock_bulk_create, authenticated_client
    ):
        """Test material is appended as '\\nMaterial: {material}' in description."""
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        job = _create_job(1)
        products = [
            ExtractedProduct(
                sku="MAT-001",
                name="Material Product",
                description="A product",
                material="Porcelain",
            ),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        call_args = mock_bulk_create.call_args[0][0]
        assert "A product" in call_args[0].description
        assert "\nMaterial: Porcelain" in call_args[0].description

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_passes_category_id(
        self, mock_bulk_create, authenticated_client
    ):
        """Test category_id from request is passed to all created products."""
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        job = _create_job(1)
        products = [
            ExtractedProduct(sku="CAT-001", name="Category Product"),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        category_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
                "category_id": str(category_id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        call_args = mock_bulk_create.call_args[0][0]
        assert call_args[0].category_id == category_id

    @patch("app.services.product_service.product_service.bulk_create_products")
    def test_confirm_handles_none_material(
        self, mock_bulk_create, authenticated_client
    ):
        """Test no material appendage when material is None."""
        mock_response = MagicMock()
        mock_response.success_count = 1
        mock_response.failure_count = 0
        mock_response.failed = []
        mock_bulk_create.return_value = mock_response

        job = _create_job(1)
        products = [
            ExtractedProduct(
                sku="NOMAT-001",
                name="No Material Product",
                description="Just a description",
                material=None,
            ),
        ]
        _complete_job(str(job.job_id), products, [])

        supplier_id = uuid4()
        response = authenticated_client.post(
            f"/api/extract/{job.job_id}/confirm",
            json={
                "job_id": str(job.job_id),
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_200_OK
        call_args = mock_bulk_create.call_args[0][0]
        assert call_args[0].description == "Just a description"
        assert "Material:" not in call_args[0].description


class TestImageProcessEndpoint:
    """Tests for the image process endpoint."""

    @patch("app.services.extraction_service.extraction_service.remove_background")
    def test_process_image_returns_result(
        self, mock_remove_bg, authenticated_client
    ):
        """Test processing an image returns result."""
        mock_remove_bg.return_value = ImageProcessingResult(
            original_url="https://example.com/image.jpg",
            processed_url="https://example.com/processed.jpg",
            operation=ImageOperation.REMOVE_BG,
        )

        response = authenticated_client.post(
            "/api/extract/image/process",
            json={"image_url": "https://example.com/image.jpg"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["original_url"] == "https://example.com/image.jpg"
        assert data["operation"] == "remove_bg"


class TestHsCodeSuggestEndpoint:
    """Tests for the HS code suggest endpoint."""

    @patch("app.services.extraction_service.extraction_service.suggest_hs_code")
    def test_suggest_hs_code_returns_suggestion(
        self, mock_suggest, authenticated_client
    ):
        """Test suggesting HS code returns suggestion."""
        mock_suggest.return_value = HsCodeSuggestion(
            code="6204.42.00",
            description="Women's dresses of cotton",
            confidence_score=0.85,
            reasoning="Cotton dress classification",
        )

        response = authenticated_client.post(
            "/api/extract/hs-code/suggest",
            json={"description": "Cotton dress for women"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "6204.42.00"
        assert data["confidence_score"] == 0.85

    def test_suggest_hs_code_empty_description_returns_400(self, authenticated_client):
        """Test that empty description returns 400."""
        response = authenticated_client.post(
            "/api/extract/hs-code/suggest",
            json={"description": "   "},  # Whitespace only
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAuthentication:
    """Tests for authentication requirements."""

    def test_upload_requires_auth(self, unauthenticated_client):
        """Test that upload endpoint requires authentication."""
        file_content = b"%PDF-1.4 fake pdf"
        files = [("files", ("test.pdf", io.BytesIO(file_content), "application/pdf"))]

        response = unauthenticated_client.post("/api/extract/upload", files=files)

        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_job_status_requires_auth(self, unauthenticated_client):
        """Test that job status endpoint requires authentication."""
        response = unauthenticated_client.get(f"/api/extract/{uuid4()}")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_results_requires_auth(self, unauthenticated_client):
        """Test that results endpoint requires authentication."""
        response = unauthenticated_client.get(f"/api/extract/{uuid4()}/results")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_confirm_requires_auth(self, unauthenticated_client):
        """Test that confirm endpoint requires authentication."""
        response = unauthenticated_client.post(
            f"/api/extract/{uuid4()}/confirm",
            json={"job_id": str(uuid4()), "supplier_id": str(uuid4())},
        )

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_image_process_requires_auth(self, unauthenticated_client):
        """Test that image process endpoint requires authentication."""
        response = unauthenticated_client.post(
            "/api/extract/image/process",
            json={"image_url": "https://example.com/image.jpg"},
        )

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_hs_code_suggest_requires_auth(self, unauthenticated_client):
        """Test that HS code suggest endpoint requires authentication."""
        response = unauthenticated_client.post(
            "/api/extract/hs-code/suggest",
            json={"description": "Test product"},
        )

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


class TestRBAC:
    """Tests for role-based access control."""

    def test_viewer_denied_upload(self, viewer_client):
        """Test that viewer role is denied upload access."""
        file_content = b"%PDF-1.4 fake pdf"
        files = [("files", ("test.pdf", io.BytesIO(file_content), "application/pdf"))]

        response = viewer_client.post("/api/extract/upload", files=files)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestExtractionJobDTO:
    """Tests for extraction job DTOs."""

    def test_extraction_job_status_enum(self):
        """Test ExtractionJobStatus enum values."""
        assert ExtractionJobStatus.PENDING.value == "pending"
        assert ExtractionJobStatus.PROCESSING.value == "processing"
        assert ExtractionJobStatus.COMPLETED.value == "completed"
        assert ExtractionJobStatus.FAILED.value == "failed"
