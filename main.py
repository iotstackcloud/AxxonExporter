"""
Axxon One Referenzbild-Exporter
Main Application
"""

import flet as ft
from config_manager import ConfigManager
from views.connection_view import ConnectionView
from views.camera_view import CameraView
from views.project_view import ProjectView
from views.export_view import ExportView


class AxxonExporterApp:
    """Main application class"""

    def __init__(self, page: ft.Page):
        """
        Initialize application

        Args:
            page: Flet page instance
        """
        self.page = page
        self.page.title = "Axxon One Referenzbild-Exporter"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.window_resizable = True

        # Initialize config manager
        self.config = ConfigManager()

        # Initialize API client (will be set after connection)
        self.api_client = None

        # Initialize views
        self.connection_view = None
        self.camera_view = None
        self.project_view = None
        self.export_view = None

        # Navigation
        self.current_view_index = 0
        self.navigation_rail = None
        self.content_container = None

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Create views
        self.connection_view = ConnectionView(
            self.config,
            on_connection_success=self.on_connection_success
        )
        self.camera_view = CameraView()
        self.project_view = ProjectView(self.config)
        self.export_view = ExportView(
            self.config,
            camera_view=self.camera_view,
            project_view=self.project_view
        )

        # Navigation rail
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_REMOTE_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS_REMOTE,
                    label="Verbindung"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.VIDEOCAM_OUTLINED,
                    selected_icon=ft.Icons.VIDEOCAM,
                    label="Kameras"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INFO_OUTLINED,
                    selected_icon=ft.Icons.INFO,
                    label="Projekt"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                    selected_icon=ft.Icons.FILE_DOWNLOAD,
                    label="Export"
                ),
            ],
            on_change=self.on_navigation_change
        )

        # Content container - build initial view
        self.content_container = ft.Container(
            content=self.connection_view.build(),
            expand=True
        )

        # App bar
        app_bar = ft.AppBar(
            title=ft.Text("Axxon One Referenzbild-Exporter", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions=[
                ft.IconButton(
                    ft.Icons.INFO_OUTLINE,
                    tooltip="Über",
                    on_click=self.show_about_dialog
                )
            ]
        )

        # Main layout
        main_row = ft.Row(
            [
                self.navigation_rail,
                ft.VerticalDivider(width=1),
                self.content_container
            ],
            expand=True
        )

        # Add to page
        self.page.appbar = app_bar
        self.page.add(main_row)

    def on_navigation_change(self, e):
        """Handle navigation rail selection change"""
        selected_index = e.control.selected_index

        # Map index to view and build if not already built
        view_objects = [
            self.connection_view,
            self.camera_view,
            self.project_view,
            self.export_view
        ]

        view = view_objects[selected_index]
        # Build the view if it hasn't been built yet (container is None)
        if not hasattr(view, 'container') or view.container is None:
            content = view.build()
        else:
            content = view.container

        # Update content
        self.content_container.content = content
        self.current_view_index = selected_index
        self.page.update()

    def on_connection_success(self, api_client):
        """
        Handle successful connection

        Args:
            api_client: Connected AxxonAPIClient instance
        """
        self.api_client = api_client

        # Update other views with API client
        self.camera_view.set_api_client(api_client)
        self.export_view.set_api_client(api_client)

        # Show success snackbar
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("✓ Erfolgreich mit Axxon One verbunden!"),
            bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_about_dialog(self, e):
        """Show about dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Über Axxon One Referenzbild-Exporter"),
            content=ft.Column(
                [
                    ft.Text("Version 2.0", weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("Diese Anwendung ermöglicht den Export von Referenzbildern"),
                    ft.Text("aus Axxon One VMS in professionelle PDF-Reports."),
                    ft.Container(height=10),
                    ft.Text("Features:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Live- und Archivbilder", size=12),
                    ft.Text("• Mehrere Auflösungen", size=12),
                    ft.Text("• Projektdetails und Logo", size=12),
                    ft.Text("• Professionelle PDF-Reports", size=12),
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Schließen", on_click=lambda _: self.close_dialog())
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self):
        """Close the current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()


def main(page: ft.Page):
    """
    Main entry point

    Args:
        page: Flet page instance
    """
    app = AxxonExporterApp(page)


if __name__ == "__main__":
    ft.app(target=main)
