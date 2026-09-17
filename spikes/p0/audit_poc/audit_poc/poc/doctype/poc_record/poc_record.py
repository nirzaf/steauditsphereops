try:
    import frappe
    from frappe.model.document import Document
except ImportError:  # pragma: no cover - imported only inside a Frappe site
    frappe = None

    class Document:  # type: ignore[no-redef]
        pass


class POCRecord(Document):
    """Small scoped record used only for generic API/permission experiments."""

    def validate(self) -> None:
        if not self.client_id or not self.period:
            raise ValueError("client_id and period are required for a scoped POC record")
        if self.generation < 0 or self.revision < 0:
            raise ValueError("generation and revision must be non-negative")
