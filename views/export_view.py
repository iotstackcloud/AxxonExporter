"""
Export View
UI for export settings and execution
"""

import flet as ft
from datetime import datetime, timedelta
from typing import List, Dict
import os
import threading


class ExportView:
    """View for export settings and execution"""

    def __init__(self, config_manager, api_client=None, camera_view=None, project_view=None):
        """
        Initialize export view

        Args:
            config_manager: Configuration manager instance
            api_client: AxxonAPIClient instance
            camera_view: CameraView instance
            project_view: ProjectView instance
        """
        super().__init__()
        self.config = config_manager
        self.api_client = api_client
        self.camera_view = camera_view
        self.project_view = project_view

        # UI components
        self.include_archive_switch = None
        self.archive_date_field = None
        self.archive_time_field = None
        self.resolution_dropdown = None
        self.output_path_field = None
        self.export_button = None
        self.progress_bar = None
        self.progress_text = None
        self.status_text = None
        self.file_picker = None

    def build(self):
        """Build the view"""
        # Load saved configuration
        export_config = self.config.get_export_config()

        self.include_archive_switch = ft.Switch(
            label="Archivbilder hinzufügen",
            value=export_config.get('include_archive', True),
            on_change=self.toggle_archive_settings
        )

        # Default archive time: 24 hours ago
        hours_ago = export_config.get('default_archive_hours_ago', 24)
        default_time = datetime.now() - timedelta(hours=hours_ago)

        self.archive_date_field = ft.TextField(
            label="Archiv Datum",
            value=default_time.strftime("%Y-%m-%d"),
            hint_text="YYYY-MM-DD",
            width=200,
            disabled=not self.include_archive_switch.value
        )

        self.archive_time_field = ft.TextField(
            label="Archiv Uhrzeit",
            value=default_time.strftime("%H:%M:%S"),
            hint_text="HH:MM:SS",
            width=200,
            disabled=not self.include_archive_switch.value
        )

        self.resolution_dropdown = ft.Dropdown(
            label="Auflösung",
            value=export_config.get('resolution', '1920x1080'),
            options=[
                ft.dropdown.Option("Original", "Original (Kamera-Auflösung)"),
                ft.dropdown.Option("1920x1080", "Full HD (1920x1080)"),
                ft.dropdown.Option("3840x2160", "4K UHD (3840x2160)"),
                ft.dropdown.Option("1280x720", "HD (1280x720)")
            ],
            width=300
        )

        # Default output path
        default_output = os.path.join(
            os.path.expanduser("~"),
            "Desktop",
            f"Axxon_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        self.output_path_field = ft.TextField(
            label="Ausgabe-Datei",
            value=default_output,
            read_only=True,
            width=500
        )

        self.file_picker = ft.FilePicker(on_result=self.on_output_selected)

        self.export_button = ft.ElevatedButton(
            "PDF exportieren",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self.start_export,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN
            )
        )

        self.progress_bar = ft.ProgressBar(
            width=500,
            visible=False
        )

        self.progress_text = ft.Text(
            "",
            size=12,
            visible=False
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
                    ft.Text("Export-Einstellungen", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "Konfigurieren Sie die Export-Einstellungen und starten Sie den Export:",
                        size=14
                    ),
                    ft.Container(height=10),
                    self.include_archive_switch,
                    ft.Container(height=10),
                    ft.Text("Archiv-Zeitpunkt", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.archive_date_field,
                            self.archive_time_field
                        ],
                        spacing=10
                    ),
                    ft.Container(height=20),
                    self.resolution_dropdown,
                    ft.Container(height=20),
                    ft.Text("Ausgabe", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.output_path_field,
                            ft.ElevatedButton(
                                "Speicherort wählen",
                                icon=ft.Icons.FOLDER,
                                on_click=lambda _: self.file_picker.save_file(
                                    file_name=f"Axxon_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    allowed_extensions=["pdf"],
                                    dialog_title="PDF speichern unter"
                                )
                            )
                        ],
                        spacing=10
                    ),
                    ft.Container(height=30),
                    self.export_button,
                    ft.Container(height=10),
                    self.progress_bar,
                    self.progress_text,
                    ft.Container(height=10),
                    self.status_text,
                    ft.Container(height=20),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Hinweis:", weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        "• Stellen Sie sicher, dass Sie Kameras ausgewählt haben",
                                        size=12
                                    ),
                                    ft.Text(
                                        "• Der Export kann je nach Anzahl der Kameras einige Minuten dauern",
                                        size=12
                                    ),
                                    ft.Text(
                                        "• Bei 'Original' Auflösung wird die native Kameraauflösung verwendet",
                                        size=12
                                    ),
                                ]
                            ),
                            padding=15
                        )
                    )
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20
        )

        return self.container

    def toggle_archive_settings(self, e):
        """Toggle archive settings visibility"""
        enabled = e.control.value
        self.archive_date_field.disabled = not enabled
        self.archive_time_field.disabled = not enabled
        self.container.update()

    def on_output_selected(self, e):
        """Handle output file selection"""
        if e.path:
            self.output_path_field.value = e.path
            self.container.update()

    def set_api_client(self, api_client):
        """Set API client"""
        self.api_client = api_client

    def set_camera_view(self, camera_view):
        """Set camera view reference"""
        self.camera_view = camera_view

    def set_project_view(self, project_view):
        """Set project view reference"""
        self.project_view = project_view

    def start_export(self, e):
        """Start the export process"""
        # Validate inputs
        if not self.api_client:
            self.show_error("Keine Verbindung zum Server. Bitte zuerst verbinden.")
            return

        if not self.camera_view:
            self.show_error("Kameraauswahl nicht verfügbar.")
            return

        selected_cameras = self.camera_view.get_selected_cameras()
        if not selected_cameras:
            self.show_error("Bitte wählen Sie mindestens eine Kamera aus.")
            return

        # Disable export button during export
        self.export_button.disabled = True
        self.progress_bar.visible = True
        self.progress_text.visible = True
        self.status_text.value = ""
        self.container.update()

        # Start export in separate thread to keep UI responsive
        thread = threading.Thread(target=self.export_process, args=(selected_cameras,))
        thread.daemon = True
        thread.start()

    def export_process(self, selected_cameras: List[Dict]):
        """
        Execute the export process

        Args:
            selected_cameras: List of selected camera dictionaries
        """
        from pdf_generator import PDFGenerator

        try:
            # Get export settings
            include_archive = self.include_archive_switch.value
            resolution_str = self.resolution_dropdown.value
            output_path = self.output_path_field.value

            # Parse resolution
            if resolution_str == "Original":
                width, height = None, None
            else:
                width, height = map(int, resolution_str.split('x'))

            # Parse archive timestamp
            archive_timestamp = None
            if include_archive:
                try:
                    date_str = self.archive_date_field.value
                    time_str = self.archive_time_field.value
                    archive_timestamp = datetime.strptime(
                        f"{date_str} {time_str}",
                        "%Y-%m-%d %H:%M:%S"
                    )
                except Exception:
                    self.show_error("Ungültiges Datum/Uhrzeit-Format für Archivbilder.")
                    return

            # Fetch images for all cameras
            total_cameras = len(selected_cameras)
            cameras_data = []

            for idx, camera in enumerate(selected_cameras):
                camera_name = camera['name']
                video_source = camera['accessPoint']

                # Update progress
                progress = (idx + 1) / total_cameras
                self.update_progress(
                    progress,
                    f"Lade Bilder für {camera_name} ({idx + 1}/{total_cameras})..."
                )

                try:
                    # Get live snapshot
                    live_image = self.api_client.get_live_snapshot(
                        video_source,
                        width,
                        height
                    )

                    # Get archive snapshot if enabled
                    archive_image = None
                    if include_archive and archive_timestamp:
                        try:
                            archive_image = self.api_client.get_archive_snapshot(
                                video_source,
                                archive_timestamp,
                                width,
                                height
                            )
                        except Exception as e:
                            print(f"Warning: Could not get archive image for {camera_name}: {e}")

                    cameras_data.append({
                        'name': camera_name,
                        'live_image': live_image,
                        'archive_image': archive_image,
                        'archive_timestamp': archive_timestamp
                    })

                except Exception as e:
                    print(f"Error fetching images for {camera_name}: {e}")
                    self.show_error(f"Fehler beim Laden der Bilder für {camera_name}: {str(e)}")

            # Generate PDF
            self.update_progress(1.0, "Erstelle PDF...")

            project_info = self.project_view.get_project_info() if self.project_view else {}

            pdf_gen = PDFGenerator(output_path)
            pdf_gen.generate_report(
                cameras_data,
                project_info,
                include_archive
            )

            # Success
            self.show_success(f"✓ PDF erfolgreich erstellt: {output_path}")

        except Exception as e:
            self.show_error(f"Fehler beim Export: {str(e)}")
        finally:
            self.export_button.disabled = False
            self.progress_bar.visible = False
            self.progress_text.visible = False
            self.container.update()

    def update_progress(self, value: float, text: str):
        """Update progress bar and text"""
        self.progress_bar.value = value
        self.progress_text.value = text
        self.container.update()

    def show_error(self, message: str):
        """Show error message"""
        self.status_text.value = f"✗ {message}"
        self.status_text.color = ft.Colors.RED
        self.export_button.disabled = False
        self.progress_bar.visible = False
        self.progress_text.visible = False
        self.container.update()

    def show_success(self, message: str):
        """Show success message"""
        self.status_text.value = message
        self.status_text.color = ft.Colors.GREEN
        self.container.update()
