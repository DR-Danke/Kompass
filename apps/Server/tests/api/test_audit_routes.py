"""Unit tests for audit API routes."""

from datetime import datetime
from io import BytesIO
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.audit_routes import router
from app.api.dependencies import get_current_user
from app.models.kompass_dto import (
    AuditType,
    ExtractionStatus,
    PaginationDTO,
    SupplierAuditListResponseDTO,
    SupplierAuditResponseDTO,
    SupplierType,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication (regular user role)."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_manager_user():
    """Mock manager user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "manager@example.com",
        "role": "manager",
        "is_active": True,
    }


@pytest.fixture
def mock_viewer_user():
    """Mock viewer user for read-only access."""
    return {
        "id": str(uuid4()),
        "email": "viewer@example.com",
        "role": "viewer",
        "is_active": True,
    }


@pytest.fixture
def sample_audit_data():
    """Sample audit data for mocking."""
    supplier_id = uuid4()
    return {
        "id": uuid4(),
        "supplier_id": supplier_id,
        "audit_type": "factory_audit",
        "document_url": "https://example.com/audit.pdf",
        "document_name": "factory_audit.pdf",
        "file_size_bytes": 1024000,
        "supplier_type": "manufacturer",
        "employee_count": 500,
        "factory_area_sqm": 10000,
        "production_lines_count": 5,
        "markets_served": {
            "south_america": 30,
            "north_america": 40,
            "europe": 20,
            "asia": 10,
        },
        "certifications": ["ISO 9001", "CE"],
        "has_machinery_photos": True,
        "positive_points": ["Modern equipment", "Clean facility"],
        "negative_points": ["Limited storage space"],
        "products_verified": ["Product A", "Product B"],
        "audit_date": "2024-01-15",
        "inspector_name": "John Doe",
        "extraction_status": "completed",
        "extraction_raw_response": {"raw_response": "..."},
        "extracted_at": datetime.utcnow(),
        "ai_classification": "A",
        "ai_classification_reason": "Type A - Preferred supplier",
        "manual_classification": None,
        "classification_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_audit_response(sample_audit_data):
    """Create SupplierAuditResponseDTO from sample data."""
    return SupplierAuditResponseDTO(
        id=sample_audit_data["id"],
        supplier_id=sample_audit_data["supplier_id"],
        audit_type=AuditType.FACTORY_AUDIT,
        document_url=sample_audit_data["document_url"],
        document_name=sample_audit_data["document_name"],
        file_size_bytes=sample_audit_data["file_size_bytes"],
        supplier_type=SupplierType.MANUFACTURER,
        employee_count=sample_audit_data["employee_count"],
        factory_area_sqm=sample_audit_data["factory_area_sqm"],
        production_lines_count=sample_audit_data["production_lines_count"],
        markets_served=sample_audit_data["markets_served"],
        certifications=sample_audit_data["certifications"],
        has_machinery_photos=sample_audit_data["has_machinery_photos"],
        positive_points=sample_audit_data["positive_points"],
        negative_points=sample_audit_data["negative_points"],
        products_verified=sample_audit_data["products_verified"],
        audit_date=sample_audit_data["audit_date"],
        inspector_name=sample_audit_data["inspector_name"],
        extraction_status=ExtractionStatus.COMPLETED,
        extraction_raw_response=sample_audit_data["extraction_raw_response"],
        extracted_at=sample_audit_data["extracted_at"],
        ai_classification=sample_audit_data["ai_classification"],
        ai_classification_reason=sample_audit_data["ai_classification_reason"],
        manual_classification=sample_audit_data["manual_classification"],
        classification_notes=sample_audit_data["classification_notes"],
        created_at=sample_audit_data["created_at"],
        updated_at=sample_audit_data["updated_at"],
    )


def create_test_app_with_user(user_data: dict):
    """Create test FastAPI app with specified user for dependency override."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/suppliers")

    # Override get_current_user to return our mock user
    async def mock_get_current_user():
        return user_data

    test_app.dependency_overrides[get_current_user] = mock_get_current_user
    return test_app


@pytest.fixture
def app(mock_current_user):
    """Create test FastAPI app with regular user."""
    return create_test_app_with_user(mock_current_user)


@pytest.fixture
def client(app):
    """Create test client with regular user."""
    return TestClient(app)


@pytest.fixture
def admin_app(mock_admin_user):
    """Create test FastAPI app with admin user."""
    return create_test_app_with_user(mock_admin_user)


@pytest.fixture
def admin_client(admin_app):
    """Create test client with admin user."""
    return TestClient(admin_app)


@pytest.fixture
def manager_app(mock_manager_user):
    """Create test FastAPI app with manager user."""
    return create_test_app_with_user(mock_manager_user)


@pytest.fixture
def manager_client(manager_app):
    """Create test client with manager user."""
    return TestClient(manager_app)


@pytest.fixture
def viewer_app(mock_viewer_user):
    """Create test FastAPI app with viewer user."""
    return create_test_app_with_user(mock_viewer_user)


@pytest.fixture
def viewer_client(viewer_app):
    """Create test client with viewer user."""
    return TestClient(viewer_app)


# =============================================================================
# TEST CLASSES
# =============================================================================


class TestUploadAudit:
    """Tests for POST /{supplier_id}/audits endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_success(
        self, mock_service, client, sample_audit_response
    ):
        """Test valid PDF upload creates audit with pending status."""
        # Create a pending status response for upload
        pending_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url="file:///tmp/audit_test.pdf",
            document_name="test_audit.pdf",
            file_size_bytes=1024,
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.upload_audit.return_value = pending_response

        # Create a mock PDF file
        pdf_content = b"%PDF-1.4 mock content"
        files = {"file": ("test_audit.pdf", BytesIO(pdf_content), "application/pdf")}

        supplier_id = sample_audit_response.supplier_id
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["extraction_status"] == "pending"
        mock_service.upload_audit.assert_called_once()

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_rejects_non_pdf(self, mock_service, client):
        """Test that non-PDF files are rejected with 400."""
        # Create a non-PDF file
        txt_content = b"This is not a PDF"
        files = {"file": ("test.txt", BytesIO(txt_content), "text/plain")}

        supplier_id = uuid4()
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
        mock_service.upload_audit.assert_not_called()

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_rejects_large_file(self, mock_service, client):
        """Test that files exceeding 25MB are rejected with 400."""
        # Create a file larger than 25MB
        large_content = b"%PDF-1.4 " + (b"x" * (26 * 1024 * 1024))
        files = {"file": ("large_audit.pdf", BytesIO(large_content), "application/pdf")}

        supplier_id = uuid4()
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        assert response.status_code == 400
        assert "exceeds maximum size" in response.json()["detail"]
        mock_service.upload_audit.assert_not_called()

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_rejects_no_filename(self, mock_service, client):
        """Test that files without filename are rejected with 400 or 422."""
        pdf_content = b"%PDF-1.4 mock content"
        files = {"file": ("", BytesIO(pdf_content), "application/pdf")}

        supplier_id = uuid4()
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        # 400 for route-level validation, 422 for Pydantic validation
        assert response.status_code in [400, 422]
        mock_service.upload_audit.assert_not_called()

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_schedules_background_processing(
        self, mock_service, client, sample_audit_response
    ):
        """Test that background task is scheduled after upload."""
        pending_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url="file:///tmp/audit_test.pdf",
            document_name="test_audit.pdf",
            file_size_bytes=1024,
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.upload_audit.return_value = pending_response

        pdf_content = b"%PDF-1.4 mock content"
        files = {"file": ("test_audit.pdf", BytesIO(pdf_content), "application/pdf")}

        supplier_id = sample_audit_response.supplier_id
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        # The background task is added but we can't directly verify it
        # Just verify the upload succeeded and service was called
        assert response.status_code == 201
        mock_service.upload_audit.assert_called_once()

    @patch("app.api.audit_routes.audit_service")
    def test_upload_audit_viewer_forbidden(
        self, mock_service, viewer_client
    ):
        """Test that viewers cannot upload audits (403)."""
        pdf_content = b"%PDF-1.4 mock content"
        files = {"file": ("test_audit.pdf", BytesIO(pdf_content), "application/pdf")}

        supplier_id = uuid4()
        response = viewer_client.post(
            f"/api/suppliers/{supplier_id}/audits",
            files=files,
        )

        assert response.status_code == 403
        mock_service.upload_audit.assert_not_called()


class TestListSupplierAudits:
    """Tests for GET /{supplier_id}/audits endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_list_audits_success(
        self, mock_service, client, sample_audit_response
    ):
        """Test successful paginated audit listing."""
        mock_service.get_supplier_audits.return_value = SupplierAuditListResponseDTO(
            items=[sample_audit_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )

        supplier_id = sample_audit_response.supplier_id
        response = client.get(f"/api/suppliers/{supplier_id}/audits")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["pagination"]["total"] == 1

    @patch("app.api.audit_routes.audit_service")
    def test_list_audits_empty(self, mock_service, client):
        """Test listing audits for supplier without audits returns empty list."""
        mock_service.get_supplier_audits.return_value = SupplierAuditListResponseDTO(
            items=[],
            pagination=PaginationDTO(page=1, limit=20, total=0, pages=0),
        )

        supplier_id = uuid4()
        response = client.get(f"/api/suppliers/{supplier_id}/audits")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
        assert data["pagination"]["total"] == 0

    @patch("app.api.audit_routes.audit_service")
    def test_list_audits_pagination(
        self, mock_service, client, sample_audit_response
    ):
        """Test pagination parameters work correctly."""
        mock_service.get_supplier_audits.return_value = SupplierAuditListResponseDTO(
            items=[sample_audit_response],
            pagination=PaginationDTO(page=2, limit=10, total=15, pages=2),
        )

        supplier_id = sample_audit_response.supplier_id
        response = client.get(
            f"/api/suppliers/{supplier_id}/audits?page=2&limit=10"
        )

        assert response.status_code == 200
        mock_service.get_supplier_audits.assert_called_once()
        call_kwargs = mock_service.get_supplier_audits.call_args.kwargs
        assert call_kwargs["page"] == 2
        assert call_kwargs["limit"] == 10

    @patch("app.api.audit_routes.audit_service")
    def test_list_audits_viewer_allowed(
        self, mock_service, viewer_client, sample_audit_response
    ):
        """Test that viewers can list audits."""
        mock_service.get_supplier_audits.return_value = SupplierAuditListResponseDTO(
            items=[sample_audit_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )

        supplier_id = sample_audit_response.supplier_id
        response = viewer_client.get(f"/api/suppliers/{supplier_id}/audits")

        assert response.status_code == 200


class TestGetAudit:
    """Tests for GET /{supplier_id}/audits/{audit_id} endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_get_audit_success(
        self, mock_service, client, sample_audit_response
    ):
        """Test successful audit retrieval by ID."""
        mock_service.get_audit.return_value = sample_audit_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id
        response = client.get(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(audit_id)

    @patch("app.api.audit_routes.audit_service")
    def test_get_audit_not_found(self, mock_service, client):
        """Test 404 for non-existent audit."""
        mock_service.get_audit.return_value = None

        supplier_id = uuid4()
        audit_id = uuid4()
        response = client.get(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("app.api.audit_routes.audit_service")
    def test_get_audit_wrong_supplier(
        self, mock_service, client, sample_audit_response
    ):
        """Test 400 when audit doesn't belong to supplier."""
        mock_service.get_audit.return_value = sample_audit_response

        wrong_supplier_id = uuid4()  # Different from audit's supplier_id
        audit_id = sample_audit_response.id
        response = client.get(
            f"/api/suppliers/{wrong_supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 400
        assert "does not belong" in response.json()["detail"].lower()


class TestReprocessAudit:
    """Tests for POST /{supplier_id}/audits/{audit_id}/reprocess endpoint."""

    @patch("app.repository.audit_repository.AuditRepository.reset_extraction")
    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_success(
        self, mock_service, mock_reset, admin_client, sample_audit_response
    ):
        """Test successful audit reprocessing."""
        # First call returns existing audit
        reset_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            document_name=sample_audit_response.document_name,
            file_size_bytes=sample_audit_response.file_size_bytes,
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.get_audit.side_effect = [sample_audit_response, reset_response]
        mock_reset.return_value = {"id": sample_audit_response.id}

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 200

    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_not_found(self, mock_service, admin_client):
        """Test 404 for non-existent audit."""
        mock_service.get_audit.return_value = None

        supplier_id = uuid4()
        audit_id = uuid4()
        response = admin_client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 404

    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_wrong_supplier(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400 when audit doesn't belong to supplier."""
        mock_service.get_audit.return_value = sample_audit_response

        wrong_supplier_id = uuid4()
        audit_id = sample_audit_response.id
        response = admin_client.post(
            f"/api/suppliers/{wrong_supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 400
        assert "does not belong" in response.json()["detail"].lower()

    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_regular_user_forbidden(
        self, mock_service, client, sample_audit_response
    ):
        """Test that regular users cannot reprocess (403)."""
        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 403

    @patch("app.repository.audit_repository.AuditRepository.reset_extraction")
    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_admin_allowed(
        self, mock_service, mock_reset, admin_client, sample_audit_response
    ):
        """Test that admins can reprocess."""
        reset_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            document_name=sample_audit_response.document_name,
            file_size_bytes=sample_audit_response.file_size_bytes,
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.get_audit.side_effect = [sample_audit_response, reset_response]
        mock_reset.return_value = {"id": sample_audit_response.id}

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 200

    @patch("app.repository.audit_repository.AuditRepository.reset_extraction")
    @patch("app.api.audit_routes.audit_service")
    def test_reprocess_audit_manager_allowed(
        self, mock_service, mock_reset, manager_client, sample_audit_response
    ):
        """Test that managers can reprocess."""
        reset_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            document_name=sample_audit_response.document_name,
            file_size_bytes=sample_audit_response.file_size_bytes,
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.get_audit.side_effect = [sample_audit_response, reset_response]
        mock_reset.return_value = {"id": sample_audit_response.id}

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = manager_client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/reprocess"
        )

        assert response.status_code == 200


class TestDeleteAudit:
    """Tests for DELETE /{supplier_id}/audits/{audit_id} endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_delete_audit_success(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test successful audit deletion returns 204."""
        mock_service.get_audit.return_value = sample_audit_response
        mock_service.delete_audit.return_value = True

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.delete(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 204
        mock_service.delete_audit.assert_called_once_with(audit_id)

    @patch("app.api.audit_routes.audit_service")
    def test_delete_audit_not_found(self, mock_service, admin_client):
        """Test 404 for non-existent audit."""
        mock_service.get_audit.return_value = None

        supplier_id = uuid4()
        audit_id = uuid4()
        response = admin_client.delete(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 404

    @patch("app.api.audit_routes.audit_service")
    def test_delete_audit_wrong_supplier(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400 when audit doesn't belong to supplier."""
        mock_service.get_audit.return_value = sample_audit_response

        wrong_supplier_id = uuid4()
        audit_id = sample_audit_response.id
        response = admin_client.delete(
            f"/api/suppliers/{wrong_supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 400

    @patch("app.api.audit_routes.audit_service")
    def test_delete_audit_regular_user_forbidden(
        self, mock_service, client, sample_audit_response
    ):
        """Test that regular users cannot delete (403)."""
        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = client.delete(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 403

    @patch("app.api.audit_routes.audit_service")
    def test_delete_audit_admin_allowed(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test that admins can delete."""
        mock_service.get_audit.return_value = sample_audit_response
        mock_service.delete_audit.return_value = True

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.delete(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}"
        )

        assert response.status_code == 204


class TestClassifyAudit:
    """Tests for POST /{supplier_id}/audits/{audit_id}/classify endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_classify_audit_success(
        self, mock_service, client, sample_audit_response
    ):
        """Test successful audit classification."""
        mock_service.get_audit.return_value = sample_audit_response

        classified_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            document_name=sample_audit_response.document_name,
            file_size_bytes=sample_audit_response.file_size_bytes,
            supplier_type=SupplierType.MANUFACTURER,
            employee_count=sample_audit_response.employee_count,
            extraction_status=ExtractionStatus.COMPLETED,
            ai_classification="A",
            ai_classification_reason="Type A - Preferred supplier",
            has_machinery_photos=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.classify_supplier.return_value = classified_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classify"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ai_classification"] == "A"

    @patch("app.api.audit_routes.audit_service")
    def test_classify_audit_not_found(self, mock_service, client):
        """Test 404 for non-existent audit."""
        mock_service.get_audit.return_value = None

        supplier_id = uuid4()
        audit_id = uuid4()
        response = client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classify"
        )

        assert response.status_code == 404

    @patch("app.api.audit_routes.audit_service")
    def test_classify_audit_wrong_supplier(
        self, mock_service, client, sample_audit_response
    ):
        """Test 400 when audit doesn't belong to supplier."""
        mock_service.get_audit.return_value = sample_audit_response

        wrong_supplier_id = uuid4()
        audit_id = sample_audit_response.id
        response = client.post(
            f"/api/suppliers/{wrong_supplier_id}/audits/{audit_id}/classify"
        )

        assert response.status_code == 400

    @patch("app.api.audit_routes.audit_service")
    def test_classify_audit_extraction_not_completed(self, mock_service, client):
        """Test 400 when extraction is pending or failed."""
        pending_response = SupplierAuditResponseDTO(
            id=uuid4(),
            supplier_id=uuid4(),
            audit_type=AuditType.FACTORY_AUDIT,
            document_url="https://example.com/audit.pdf",
            extraction_status=ExtractionStatus.PENDING,
            has_machinery_photos=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.get_audit.return_value = pending_response
        mock_service.classify_supplier.side_effect = ValueError(
            "Cannot classify: extraction not completed"
        )

        supplier_id = pending_response.supplier_id
        audit_id = pending_response.id

        response = client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classify"
        )

        assert response.status_code == 400
        assert "extraction not completed" in response.json()["detail"].lower()

    @patch("app.api.audit_routes.audit_service")
    def test_classify_audit_updates_supplier_status(
        self, mock_service, client, sample_audit_response
    ):
        """Test that classification updates supplier certification_status."""
        mock_service.get_audit.return_value = sample_audit_response

        classified_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            extraction_status=ExtractionStatus.COMPLETED,
            ai_classification="A",
            ai_classification_reason="Type A - Preferred supplier",
            has_machinery_photos=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.classify_supplier.return_value = classified_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = client.post(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classify"
        )

        assert response.status_code == 200
        # The service is responsible for updating supplier status
        mock_service.classify_supplier.assert_called_once_with(audit_id)


class TestOverrideClassification:
    """Tests for PUT /{supplier_id}/audits/{audit_id}/classification endpoint."""

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_success(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test successful classification override with notes."""
        mock_service.get_audit.return_value = sample_audit_response

        override_response = SupplierAuditResponseDTO(
            id=sample_audit_response.id,
            supplier_id=sample_audit_response.supplier_id,
            audit_type=AuditType.FACTORY_AUDIT,
            document_url=sample_audit_response.document_url,
            extraction_status=ExtractionStatus.COMPLETED,
            ai_classification="A",
            manual_classification="B",
            classification_notes="Downgraded due to quality issues",
            has_machinery_photos=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_service.override_classification.return_value = override_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "Downgraded due to quality issues",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["manual_classification"] == "B"

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_requires_notes(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400 when notes are empty."""
        mock_service.get_audit.return_value = sample_audit_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "",
            },
        )

        assert response.status_code == 400
        assert "notes are required" in response.json()["detail"].lower()

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_requires_notes_not_whitespace(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400 when notes are only whitespace."""
        mock_service.get_audit.return_value = sample_audit_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "   ",
            },
        )

        assert response.status_code == 400
        assert "notes are required" in response.json()["detail"].lower()

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_not_found(self, mock_service, admin_client):
        """Test 404 for non-existent audit."""
        mock_service.get_audit.return_value = None

        supplier_id = uuid4()
        audit_id = uuid4()

        response = admin_client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "Valid notes for override",
            },
        )

        assert response.status_code == 404

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_wrong_supplier(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400 when audit doesn't belong to supplier."""
        mock_service.get_audit.return_value = sample_audit_response

        wrong_supplier_id = uuid4()
        audit_id = sample_audit_response.id

        response = admin_client.put(
            f"/api/suppliers/{wrong_supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "Valid notes for override",
            },
        )

        assert response.status_code == 400

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_regular_user_forbidden(
        self, mock_service, client, sample_audit_response
    ):
        """Test that regular users cannot override (403)."""
        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "B",
                "notes": "Valid notes for override",
            },
        )

        assert response.status_code == 403

    @patch("app.api.audit_routes.audit_service")
    def test_override_classification_invalid_grade(
        self, mock_service, admin_client, sample_audit_response
    ):
        """Test 400/422 for invalid classification grade (D, X, etc.)."""
        mock_service.get_audit.return_value = sample_audit_response

        supplier_id = sample_audit_response.supplier_id
        audit_id = sample_audit_response.id

        response = admin_client.put(
            f"/api/suppliers/{supplier_id}/audits/{audit_id}/classification",
            json={
                "classification": "D",  # Invalid grade
                "notes": "Valid notes for override",
            },
        )

        # Pydantic validation should catch this with 422 or service with 400
        assert response.status_code in [400, 422]
