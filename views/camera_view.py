"""
Camera Selection View
UI for selecting cameras to export
"""

import flet as ft
from typing import List, Dict


class CameraView:
    """View for camera selection"""

    def __init__(self, api_client=None):
        """
        Initialize camera view

        Args:
            api_client: AxxonAPIClient instance
        """
        super().__init__()
        self.api_client = api_client
        self.cameras: List[Dict] = []
        self.selected_cameras: List[Dict] = []

        # UI components
        self.camera_list = None
        self.status_text = None
        self.refresh_button = None
        self.select_all_button = None
        self.deselect_all_button = None
        self.search_field = None
        self.camera_checkboxes = {}
        self.container = None

    def build(self):
        """Build the view"""
        self.search_field = ft.TextField(
            label="Kamera suchen",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.filter_cameras,
            width=400
        )

        self.refresh_button = ft.ElevatedButton(
            "Kameras laden",
            icon=ft.Icons.REFRESH,
            on_click=self.load_cameras
        )

        self.select_all_button = ft.TextButton(
            "Alle auswählen",
            icon=ft.Icons.CHECK_BOX,
            on_click=self.select_all
        )

        self.deselect_all_button = ft.TextButton(
            "Alle abwählen",
            icon=ft.Icons.CHECK_BOX_OUTLINE_BLANK,
            on_click=self.deselect_all
        )

        self.status_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD
        )

        self.camera_list = ft.Column(
            [],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            height=400
        )

        self.container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Kameraauswahl", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "Wählen Sie die Kameras aus, die in den PDF-Export aufgenommen werden sollen:",
                        size=14
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            self.refresh_button,
                            self.select_all_button,
                            self.deselect_all_button
                        ],
                        spacing=10
                    ),
                    ft.Container(height=10),
                    self.search_field,
                    ft.Container(height=10),
                    self.status_text,
                    ft.Container(height=10),
                    ft.Container(
                        content=self.camera_list,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=5,
                        padding=10
                    )
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20
        )

        return self.container

    def set_api_client(self, api_client):
        """
        Set API client and load cameras

        Args:
            api_client: AxxonAPIClient instance
        """
        self.api_client = api_client
        self.load_cameras(None)

    def load_cameras(self, e):
        """Load cameras from server"""
        # Check if UI elements are initialized
        if not self.status_text or not self.container or not self.refresh_button:
            return

        if not self.api_client:
            self.status_text.value = "✗ Keine Verbindung zum Server. Bitte zuerst verbinden."
            self.status_text.color = ft.Colors.RED
            self.container.update()
            return

        self.refresh_button.disabled = True
        self.status_text.value = "Lade Kameras..."
        self.status_text.color = ft.Colors.BLUE
        self.container.update()

        try:
            self.cameras = self.api_client.get_camera_list()

            if not self.cameras:
                self.status_text.value = "⚠ Keine Kameras gefunden"
                self.status_text.color = ft.Colors.ORANGE
            else:
                self.status_text.value = f"✓ {len(self.cameras)} Kamera(s) gefunden"
                self.status_text.color = ft.Colors.GREEN

            self.display_cameras()

        except Exception as ex:
            self.status_text.value = f"✗ Fehler: {str(ex)}"
            self.status_text.color = ft.Colors.RED
        finally:
            if self.refresh_button:
                self.refresh_button.disabled = False
            if self.container:
                self.container.update()

    def display_cameras(self, filter_text: str = ""):
        """
        Display cameras in list

        Args:
            filter_text: Optional filter text
        """
        self.camera_list.controls.clear()
        self.camera_checkboxes.clear()

        if not self.cameras:
            self.camera_list.controls.append(
                ft.Text("Keine Kameras verfügbar. Bitte 'Kameras laden' klicken.", italic=True)
            )
        else:
            for camera in self.cameras:
                camera_name = camera['name']
                camera_ip = camera.get('ipAddress', 'N/A')

                # Apply filter
                if filter_text and filter_text.lower() not in camera_name.lower():
                    continue

                # Create checkbox
                checkbox = ft.Checkbox(
                    label=f"{camera_name} ({camera_ip})",
                    value=camera in self.selected_cameras,
                    on_change=lambda e, cam=camera: self.toggle_camera(e, cam)
                )

                self.camera_checkboxes[camera['id']] = checkbox

                # Create card for camera
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.VIDEOCAM, size=20),
                                ft.Column(
                                    [
                                        checkbox,
                                        ft.Text(
                                            f"ID: {camera['accessPoint']}",
                                            size=10,
                                            color=ft.Colors.GREY
                                        )
                                    ],
                                    spacing=2
                                )
                            ],
                            spacing=10
                        ),
                        padding=10
                    )
                )

                self.camera_list.controls.append(card)

        if self.container:
            self.container.update()

    def toggle_camera(self, e, camera):
        """
        Toggle camera selection

        Args:
            e: Event
            camera: Camera dictionary
        """
        if e.control.value:
            if camera not in self.selected_cameras:
                self.selected_cameras.append(camera)
        else:
            if camera in self.selected_cameras:
                self.selected_cameras.remove(camera)

        self.update_status()

    def select_all(self, e):
        """Select all cameras"""
        self.selected_cameras = self.cameras.copy()
        for checkbox in self.camera_checkboxes.values():
            checkbox.value = True
        self.update_status()
        self.container.update()

    def deselect_all(self, e):
        """Deselect all cameras"""
        self.selected_cameras.clear()
        for checkbox in self.camera_checkboxes.values():
            checkbox.value = False
        self.update_status()
        self.container.update()

    def filter_cameras(self, e):
        """Filter cameras by search text"""
        self.display_cameras(e.control.value)

    def update_status(self):
        """Update status text with selection count"""
        count = len(self.selected_cameras)
        total = len(self.cameras)
        self.status_text.value = f"✓ {count} von {total} Kamera(s) ausgewählt"
        self.status_text.color = ft.Colors.GREEN if count > 0 else ft.Colors.GREY

    def get_selected_cameras(self) -> List[Dict]:
        """
        Get list of selected cameras

        Returns:
            List of selected camera dictionaries
        """
        return self.selected_cameras
