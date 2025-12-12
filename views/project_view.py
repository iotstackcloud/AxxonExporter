"""
Project Details View
UI for entering project information
"""

import flet as ft
from flet import FilePickerResultEvent
import os


class ProjectView:
    """View for project details"""

    def __init__(self, config_manager):
        """
        Initialize project view

        Args:
            config_manager: Configuration manager instance
        """
        super().__init__()
        self.config = config_manager

        # Input fields
        self.project_name_field = None
        self.location_field = None
        self.technician_field = None
        self.company_field = None
        self.logo_path_field = None
        self.logo_preview = None
        self.file_picker = None
        self.status_text = None

    def build(self):
        """Build the view"""
        # Load saved configuration
        project_config = self.config.get_project_config()

        self.project_name_field = ft.TextField(
            label="Projektname",
            value=project_config.get('name', ''),
            hint_text="z.B. Videoüberwachung Gebäude A",
            width=500
        )

        self.location_field = ft.TextField(
            label="Standort / Adresse",
            value=project_config.get('location', ''),
            hint_text="z.B. Hauptstraße 123, 12345 Musterstadt",
            width=500,
            multiline=True,
            min_lines=2,
            max_lines=3
        )

        self.technician_field = ft.TextField(
            label="Techniker",
            value=project_config.get('technician', ''),
            hint_text="z.B. Max Mustermann",
            width=500
        )

        self.company_field = ft.TextField(
            label="Firma / Unternehmen",
            value=project_config.get('company', ''),
            hint_text="z.B. Musterfirma GmbH",
            width=500
        )

        self.logo_path_field = ft.TextField(
            label="Logo-Pfad",
            value=project_config.get('logo_path', ''),
            read_only=True,
            width=400
        )

        # File picker for logo
        self.file_picker = ft.FilePicker(on_result=self.on_logo_selected)

        # Logo preview
        self.logo_preview = ft.Image(
            src=project_config.get('logo_path', ''),
            width=200,
            height=100,
            fit=ft.ImageFit.CONTAIN,
            visible=bool(project_config.get('logo_path', ''))
        )

        self.status_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD
        )

        self.container = ft.Container(
            content=ft.Column(
                [
                    self.file_picker,
                    ft.Text("Projektdetails", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "Geben Sie die Projektinformationen ein, die im PDF-Report angezeigt werden:",
                        size=14
                    ),
                    ft.Container(height=10),
                    self.project_name_field,
                    self.location_field,
                    self.technician_field,
                    self.company_field,
                    ft.Container(height=20),
                    ft.Text("Logo (optional)", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.logo_path_field,
                            ft.ElevatedButton(
                                "Logo auswählen",
                                icon=ft.Icons.IMAGE,
                                on_click=lambda _: self.file_picker.pick_files(
                                    allowed_extensions=["png", "jpg", "jpeg"],
                                    dialog_title="Logo auswählen"
                                )
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLEAR,
                                tooltip="Logo entfernen",
                                on_click=self.clear_logo
                            )
                        ],
                        spacing=10
                    ),
                    ft.Container(
                        content=self.logo_preview,
                        padding=10,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=5,
                        visible=self.logo_preview.visible
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Speichern",
                        icon=ft.Icons.SAVE,
                        on_click=self.save_config
                    ),
                    ft.Container(height=10),
                    self.status_text,
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20
        )

        return self.container

    def on_logo_selected(self, e: FilePickerResultEvent):
        """Handle logo file selection"""
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            self.logo_path_field.value = file_path
            self.logo_preview.src = file_path
            self.logo_preview.visible = True
            self.logo_preview.parent.visible = True
            self.container.update()

    def clear_logo(self, e):
        """Clear logo selection"""
        self.logo_path_field.value = ""
        self.logo_preview.src = ""
        self.logo_preview.visible = False
        self.logo_preview.parent.visible = False
        self.container.update()

    def save_config(self, e):
        """Save project configuration"""
        try:
            self.config.set('project.name', self.project_name_field.value)
            self.config.set('project.location', self.location_field.value)
            self.config.set('project.technician', self.technician_field.value)
            self.config.set('project.company', self.company_field.value)
            self.config.set('project.logo_path', self.logo_path_field.value)
            self.config.save_config()

            self.status_text.value = "✓ Projektdetails gespeichert"
            self.status_text.color = ft.Colors.GREEN
            self.container.update()

        except Exception as ex:
            self.status_text.value = f"✗ Fehler beim Speichern: {str(ex)}"
            self.status_text.color = ft.Colors.RED
            self.container.update()

    def get_project_info(self) -> dict:
        """
        Get current project information

        Returns:
            Dictionary with project information
        """
        # Check if UI elements are initialized
        if not self.project_name_field:
            return {
                'name': '',
                'location': '',
                'technician': '',
                'company': '',
                'logo_path': ''
            }

        return {
            'name': self.project_name_field.value or '',
            'location': self.location_field.value or '',
            'technician': self.technician_field.value or '',
            'company': self.company_field.value or '',
            'logo_path': self.logo_path_field.value or ''
        }
