# Feature: Supabase Storage for Audit File Uploads

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Feature Description
Integrate Supabase Storage for uploading and storing supplier audit PDF documents. This replaces the current local file storage approach (`file://` URLs) with proper cloud storage that returns HTTPS URLs, enabling reliable PDF processing in production environments like Render.

## Problem Statement
The current implementation stores uploaded audit PDFs as local temp files with `file://` URLs. This causes issues:
1. **Local files are ephemeral** - Lost on server restart/redeployment
2. **file:// URLs don't work with httpx** - Required a workaround to read local files
3. **Not production-ready** - Render and other cloud platforms don't persist local files
4. **poppler-utils still needed** - Requires a Dockerfile for the system dependency

## Solution Statement
1. **Integrate Supabase Storage** for file uploads in `audit_routes.py`
2. **Store HTTPS URLs** in the database instead of `file://` URLs
3. **Create a Dockerfile** for Render deployment with `poppler-utils`
4. **Add storage bucket configuration** via environment variables

## Architecture

### Current Flow (Local Files)
```
Upload PDF → Save to /tmp/audit_xxx.pdf → Store "file:///tmp/..." URL → Read local file
```

### New Flow (Supabase Storage)
```
Upload PDF → Upload to Supabase Storage → Get HTTPS URL → Store URL in DB
                                                ↓
Background job → Fetch PDF via HTTPS → pdf2image → AI extraction
```

## Relevant Files

### Files to Modify
- `apps/Server/app/api/audit_routes.py` - Replace local file storage with Supabase upload
- `apps/Server/app/services/audit_service.py` - Remove local file:// handling (keep for backwards compatibility)
- `apps/Server/app/config/settings.py` - Add Supabase Storage configuration
- `apps/Server/requirements.txt` - Add `supabase` Python SDK
- `.env.sample` - Add Supabase Storage environment variables

### New Files to Create
- `apps/Server/app/services/storage_service.py` - Supabase Storage service wrapper
- `apps/Server/Dockerfile` - Docker image with poppler-utils for Render
- `apps/Server/render.yaml` - Render deployment configuration (optional)

## Environment Variables

Add to `apps/Server/.env`:
```bash
# Supabase Storage
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=audits
```

Note: Use `SUPABASE_SERVICE_KEY` (service role) instead of anon key for server-side uploads with full access.

## Step by Step Tasks

### Step 1: Add Supabase Python SDK to requirements.txt
- Open `apps/Server/requirements.txt`
- Add `supabase>=2.0.0` to the dependencies
- This provides the official Supabase client for Python

### Step 2: Add Supabase Storage settings
- Open `apps/Server/app/config/settings.py`
- Add the following settings:
  ```python
  # Supabase Storage
  SUPABASE_URL: Optional[str] = None
  SUPABASE_SERVICE_KEY: Optional[str] = None
  SUPABASE_STORAGE_BUCKET: str = "audits"
  ```

### Step 3: Create Storage Service
- Create `apps/Server/app/services/storage_service.py`
- Implement a `StorageService` class with methods:
  ```python
  class StorageService:
      def __init__(self):
          self._client = None

      def _get_client(self):
          """Lazily initialize Supabase client."""
          if self._client is None:
              from supabase import create_client
              settings = get_settings()
              if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
                  self._client = create_client(
                      settings.SUPABASE_URL,
                      settings.SUPABASE_SERVICE_KEY
                  )
          return self._client

      def upload_file(
          self,
          file_content: bytes,
          file_name: str,
          content_type: str = "application/pdf",
          folder: str = "audits"
      ) -> str:
          """Upload file to Supabase Storage and return public URL."""
          client = self._get_client()
          if not client:
              raise RuntimeError("Supabase Storage not configured")

          # Generate unique path
          import uuid
          unique_name = f"{folder}/{uuid.uuid4().hex}_{file_name}"

          # Upload to storage
          bucket = get_settings().SUPABASE_STORAGE_BUCKET
          result = client.storage.from_(bucket).upload(
              unique_name,
              file_content,
              {"content-type": content_type}
          )

          # Get public URL
          url = client.storage.from_(bucket).get_public_url(unique_name)
          return url

      def delete_file(self, file_path: str) -> bool:
          """Delete file from Supabase Storage."""
          # Extract path from URL and delete
          pass

      def is_configured(self) -> bool:
          """Check if Supabase Storage is properly configured."""
          settings = get_settings()
          return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)

  # Singleton
  storage_service = StorageService()
  ```

### Step 4: Update audit_routes.py to use Supabase Storage
- Open `apps/Server/app/api/audit_routes.py`
- Import the storage service
- Modify the `upload_audit` endpoint:
  ```python
  from app.services.storage_service import storage_service

  @router.post("/{supplier_id}/audits", ...)
  async def upload_audit(...):
      # ... validation code ...

      # Read file content
      content = await file.read()

      # Upload to Supabase Storage (or fallback to local for dev)
      if storage_service.is_configured():
          document_url = storage_service.upload_file(
              file_content=content,
              file_name=file.filename or "audit.pdf",
              content_type="application/pdf",
              folder=f"suppliers/{supplier_id}/audits"
          )
      else:
          # Fallback to local file for development
          import tempfile
          import os
          ext = os.path.splitext(file.filename or "")[1].lower()
          with tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix="audit_") as tmp:
              tmp.write(content)
              document_url = f"file://{tmp.name}"
          print("WARN [AuditRoutes]: Supabase Storage not configured, using local file")

      # Create audit record with URL
      audit = audit_service.upload_audit(
          supplier_id=supplier_id,
          document_url=document_url,
          document_name=file.filename or "audit.pdf",
          file_size_bytes=len(content),
          audit_type=audit_type,
      )
      # ... rest of the code ...
  ```

### Step 5: Create Dockerfile for Render
- Create `apps/Server/Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim

  # Install system dependencies for PDF processing
  RUN apt-get update && apt-get install -y \
      poppler-utils \
      && rm -rf /var/lib/apt/lists/*

  # Set working directory
  WORKDIR /app

  # Copy requirements first for better caching
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy application code
  COPY . .

  # Expose port
  EXPOSE 8000

  # Run the application
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

### Step 6: Update .env.sample
- Add Supabase Storage variables:
  ```bash
  # Supabase Storage (for audit file uploads)
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_SERVICE_KEY=your-service-role-key
  SUPABASE_STORAGE_BUCKET=audits
  ```

### Step 7: Create Supabase Storage Bucket
- Log into Supabase Dashboard
- Navigate to Storage
- Create a new bucket named "audits"
- Set bucket to "Public" (for PDF viewing) or configure signed URLs
- Add RLS policies if needed

### Step 8: Update Render deployment settings
- In Render dashboard, change environment from "Python" to "Docker"
- Or create `render.yaml` for infrastructure-as-code:
  ```yaml
  services:
    - type: web
      name: kompass-api
      env: docker
      dockerfilePath: ./apps/Server/Dockerfile
      dockerContext: ./apps/Server
      envVars:
        - key: DATABASE_URL
          sync: false
        - key: SUPABASE_URL
          sync: false
        - key: SUPABASE_SERVICE_KEY
          sync: false
        - key: SUPABASE_STORAGE_BUCKET
          value: audits
  ```

### Step 9: Test the integration
- Set up Supabase Storage bucket locally
- Configure environment variables
- Upload a test PDF
- Verify URL is an HTTPS Supabase URL
- Verify PDF can be fetched and processed
- Verify extraction works end-to-end

### Step 10: Run validation commands
- Execute all validation commands to ensure no regressions

## Validation Commands

```bash
# Verify supabase package is in requirements
grep -q "supabase" apps/Server/requirements.txt && echo "supabase found" || echo "supabase MISSING"

# Install dependencies
cd apps/Server && pip install -r requirements.txt

# Run Server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run audit-specific tests
cd apps/Server && .venv/bin/pytest tests/api/test_audit_routes.py -v --tb=short
cd apps/Server && .venv/bin/pytest tests/test_audit_service.py -v --tb=short

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build

# Test Docker build locally
cd apps/Server && docker build -t kompass-api .
docker run --rm kompass-api which pdftoppm  # Should find poppler
```

## Supabase Storage Bucket Setup

### Via Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the sidebar
3. Click **New bucket**
4. Name: `audits`
5. Public bucket: **Yes** (for direct PDF viewing)
6. Click **Create bucket**

### Storage Policies (Optional)
If you want more control, add RLS policies:
```sql
-- Allow authenticated uploads
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'audits');

-- Allow public reads
CREATE POLICY "Allow public reads"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'audits');
```

## File Structure After Implementation

```
apps/Server/
├── Dockerfile                          # NEW - Docker image with poppler
├── requirements.txt                    # MODIFIED - Added supabase
├── app/
│   ├── config/
│   │   └── settings.py                 # MODIFIED - Added Supabase settings
│   ├── api/
│   │   └── audit_routes.py             # MODIFIED - Use storage service
│   └── services/
│       ├── storage_service.py          # NEW - Supabase Storage wrapper
│       └── audit_service.py            # (unchanged, file:// fallback kept)
```

## Rollback Plan

If issues arise:
1. Remove Supabase Storage configuration from `.env`
2. The code will fallback to local file storage automatically
3. Revert Render to Python environment (remove Docker)

## Notes

1. **Service Role Key**: Use `SUPABASE_SERVICE_KEY` (not anon key) for server-side uploads to bypass RLS
2. **Public vs Private Buckets**: Public bucket allows direct PDF viewing; private requires signed URLs
3. **File Cleanup**: Consider adding a cleanup job for old/orphaned files
4. **File Size Limits**: Supabase free tier has 1GB storage limit; Pro has 100GB
5. **Backwards Compatibility**: The local file:// fallback is kept for local development without Supabase
6. **Docker Build Time**: First build may take a few minutes; subsequent builds use cache
7. **Render Pricing**: Docker deployments may use more resources; check Render pricing
