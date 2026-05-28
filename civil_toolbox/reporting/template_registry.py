"""In-memory registry for report templates.

Provides simple template storage and retrieval without external persistence.

Example:
    >>> from civil_toolbox.reporting.template_registry import ReportTemplateRegistry
    >>> from civil_toolbox.reporting.report_templates import ReportTemplate
    >>> registry = ReportTemplateRegistry()
    >>> registry.register(my_template)
    >>> template = registry.get("my_template_id")
"""

from __future__ import annotations

from civil_toolbox.reporting.report_templates import ReportTemplate


class TemplateNotFoundError(KeyError):
    """Raised when a template is not found in the registry."""

    def __init__(self, template_id: str):
        self.template_id = template_id
        super().__init__(f"Template not found: {template_id}")


class ReportTemplateRegistry:
    """In-memory registry for report templates.

    Stores templates by ID for retrieval during report building.
    Does not persist templates externally.
    """

    def __init__(self) -> None:
        self._templates: dict[str, ReportTemplate] = {}

    def register(
        self,
        template: ReportTemplate,
        overwrite: bool = False,
    ) -> None:
        """Register a template.

        Args:
            template: The template to register.
            overwrite: If True, replace existing template with same ID.

        Raises:
            ValueError: If template ID exists and overwrite is False.
        """
        if template.id in self._templates and not overwrite:
            raise ValueError(
                f"Template with ID '{template.id}' already registered. "
                "Use overwrite=True to replace."
            )
        self._templates[template.id] = template

    def get(self, template_id: str) -> ReportTemplate:
        """Get a template by ID.

        Args:
            template_id: The template identifier.

        Returns:
            The registered template.

        Raises:
            TemplateNotFoundError: If template not found.
        """
        if template_id not in self._templates:
            raise TemplateNotFoundError(template_id)
        return self._templates[template_id]

    def has_template(self, template_id: str) -> bool:
        """Check if a template is registered.

        Args:
            template_id: The template identifier.

        Returns:
            True if template exists.
        """
        return template_id in self._templates

    def list_templates(self) -> list[ReportTemplate]:
        """List all registered templates.

        Returns:
            List of templates sorted by ID.
        """
        return sorted(self._templates.values(), key=lambda t: t.id)

    def unregister(self, template_id: str) -> None:
        """Remove a template from the registry.

        Args:
            template_id: The template identifier.

        Raises:
            TemplateNotFoundError: If template not found.
        """
        if template_id not in self._templates:
            raise TemplateNotFoundError(template_id)
        del self._templates[template_id]

    def clear(self) -> None:
        """Remove all templates from the registry."""
        self._templates.clear()

    def __len__(self) -> int:
        """Return number of registered templates."""
        return len(self._templates)

    def __contains__(self, template_id: str) -> bool:
        """Check if template ID is registered."""
        return template_id in self._templates
