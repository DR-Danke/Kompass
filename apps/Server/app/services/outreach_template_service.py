"""Service layer for outreach template management."""

from typing import Dict, List, Optional, Tuple
from uuid import UUID

from app.repository.outreach_template_repository import outreach_template_repository
from app.services.email_service import OUTREACH_TEMPLATES


AVAILABLE_PLACEHOLDERS = [
    "{contact_name}", "{company_name}", "{fair_name}", "{sender_name}"
]


class OutreachTemplateService:
    """Business logic for outreach template CRUD and rendering."""

    def _enrich_template(self, template: dict) -> dict:
        """Add body_preview and available_placeholders to a template dict."""
        body = template.get("body", "")
        template["body_preview"] = (body[:150] + "...") if len(body) > 150 else body
        template["available_placeholders"] = AVAILABLE_PLACEHOLDERS
        return template

    def list_templates(self, active_only: bool = True) -> List[Dict]:
        """List templates from database, falling back to hardcoded defaults.

        Args:
            active_only: If True, only return active templates

        Returns:
            List of enriched template dicts
        """
        try:
            templates = outreach_template_repository.list_templates(active_only=active_only)
            if templates:
                return [self._enrich_template(t) for t in templates]
        except Exception as e:
            print(f"WARN [OutreachTemplateService]: DB read failed, using defaults: {e}")

        # Fallback to hardcoded defaults
        result = []
        for key, tmpl in OUTREACH_TEMPLATES.items():
            result.append(self._enrich_template({
                "id": None,
                "key": key,
                "name": tmpl["name"],
                "subject": tmpl["subject"],
                "body": tmpl["body"],
                "is_active": True,
                "sort_order": 0,
            }))
        return result

    def get_template(self, key: str) -> Dict:
        """Get a template by key with DB fallback.

        Args:
            key: Template key

        Returns:
            Template dict

        Raises:
            ValueError: If template not found anywhere
        """
        template = outreach_template_repository.get_by_key(key)
        if template:
            return self._enrich_template(template)

        # Fallback to hardcoded
        if key in OUTREACH_TEMPLATES:
            tmpl = OUTREACH_TEMPLATES[key]
            return self._enrich_template({
                "id": None,
                "key": key,
                "name": tmpl["name"],
                "subject": tmpl["subject"],
                "body": tmpl["body"],
                "is_active": True,
                "sort_order": 0,
            })

        raise ValueError(f"Template '{key}' not found")

    def get_template_by_id(self, template_id: UUID) -> Dict:
        """Get a template by UUID.

        Args:
            template_id: Template UUID

        Returns:
            Enriched template dict

        Raises:
            ValueError: If not found
        """
        template = outreach_template_repository.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with id '{template_id}' not found")
        return self._enrich_template(template)

    def update_template(self, template_id: UUID, updates: Dict) -> Dict:
        """Update a template.

        Args:
            template_id: Template UUID
            updates: Fields to update

        Returns:
            Updated enriched template dict

        Raises:
            ValueError: If not found
        """
        result = outreach_template_repository.update(template_id, updates)
        if not result:
            raise ValueError(f"Template with id '{template_id}' not found")
        print(f"INFO [OutreachTemplateService]: Updated template {template_id}")
        return self._enrich_template(result)

    def reset_template(self, template_id: UUID) -> Dict:
        """Reset a template to its hardcoded default values.

        Args:
            template_id: Template UUID

        Returns:
            Reset enriched template dict

        Raises:
            ValueError: If template not found or no default exists
        """
        # Get the template to find its key
        template = outreach_template_repository.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template with id '{template_id}' not found")

        key = template["key"]
        if key not in OUTREACH_TEMPLATES:
            raise ValueError(f"No default template found for key '{key}'")

        default = OUTREACH_TEMPLATES[key]
        result = outreach_template_repository.reset_to_default(
            template_id,
            {
                "name": default["name"],
                "subject": default["subject"],
                "body": default["body"],
            },
        )
        if not result:
            raise ValueError("Failed to reset template")

        print(f"INFO [OutreachTemplateService]: Reset template {template_id} to default")
        return self._enrich_template(result)

    def get_template_body_rendered(
        self, key: str, context: Dict[str, str]
    ) -> Tuple[str, str]:
        """Get a template with placeholders substituted.

        Args:
            key: Template key
            context: Dict mapping placeholder names to values

        Returns:
            Tuple of (rendered_subject, rendered_body)
        """
        template = self.get_template(key)
        subject = template["subject"].format(**context)
        body = template["body"].format(**context)
        return subject, body


# Singleton instance
outreach_template_service = OutreachTemplateService()
