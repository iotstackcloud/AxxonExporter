"""
Connection View
UI for configuring Axxon One server connection
"""

import flet as ft
from typing import Callable


class ConnectionView:
    """View for server connection configuration"""

    def __init__(self, config_manager, on_connection_success: Callable = None):
        """
        Initialize connection view

        Args:
            config_manager: Configuration manager instance
            on_connection_success: Callback when connection is successful
        """
        self.config = config_manager
        self.on_connection_success = on_connection_success
        self.api_client = None

        # Input fields
        self.host_field = None
        self.port_field = None
        self.username_field = None
        self.password_field = None
        self.https_switch = None
        self.status_text = None
        self.test_button = None
        self.container = None

    def build(self):
        """Build the view"""
        # Load saved configuration
        conn_config = self.config.get_connection_config()

        self.host_field = ft.TextField(
            label="Server IP-Adresse",
            value=conn_config.get('host', ''),
            hint_text="z.B. 192.168.1.100",
            width=300
        )

        self.port_field = ft.TextField(
            label="Port",
            value=str(conn_config.get('port', 8000)),
            hint_text="Standard: 8000 (Linux) oder 80 (Windows)",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.username_field = ft.TextField(
            label="Benutzername",
            value=conn_config.get('username', 'root'),
            width=300
        )

        self.password_field = ft.TextField(
            label="Passwort",
            value=conn_config.get('password', ''),
            password=True,
            can_reveal_password=True,
            width=300
        )

        self.https_switch = ft.Switch(
            label="HTTPS verwenden",
            value=conn_config.get('use_https', False)
        )

        self.test_button = ft.ElevatedButton(
            "Verbindung testen",
            icon=ft.Icons.WIFI_FIND,
            on_click=self.test_connection
        )

        self.status_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.BOLD
        )

        self.container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Axxon One Server-Verbindung", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(
                        "Geben Sie die Verbindungsdaten zu Ihrem Axxon One Server ein:",
                        size=14
                    ),
                    ft.Container(height=20),
                    self.host_field,
                    self.port_field,
                    self.username_field,
                    self.password_field,
                    ft.Container(height=10),
                    self.https_switch,
                    ft.Container(height=20),
                    ft.Row(
                        [
                            self.test_button,
                            ft.ElevatedButton(
                                "Speichern",
                                icon=ft.Icons.SAVE,
                                on_click=self.save_config
                            )
                        ],
                        spacing=10
                    ),
                    ft.Container(height=10),
                    self.status_text,
                    ft.Container(height=20),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Hinweis:", weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        "• Standardport: 8000 (Linux) oder 80 (Windows)",
                                        size=12
                                    ),
                                    ft.Text(
                                        "• Standard-Benutzername: root",
                                        size=12
                                    ),
                                    ft.Text(
                                        "• Stellen Sie sicher, dass der Server erreichbar ist",
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

    def test_connection(self, e):
        """Test connection to server"""
        from api_client import AxxonAPIClient

        # Check if UI elements are initialized
        if not self.test_button or not self.status_text or not self.container:
            return

        # Update status
        self.test_button.disabled = True
        self.status_text.value = "Verbindung wird getestet..."
        self.status_text.color = ft.Colors.BLUE
        self.container.update()

        try:
            # Create API client
            port = int(self.port_field.value) if self.port_field.value else 8000
            self.api_client = AxxonAPIClient(
                host=self.host_field.value,
                port=port,
                username=self.username_field.value,
                password=self.password_field.value,
                use_https=self.https_switch.value
            )

            # Test connection
            success, message = self.api_client.test_connection()

            if success:
                self.status_text.value = f"✓ {message}"
                self.status_text.color = ft.Colors.GREEN
                # Auto-save on successful connection
                self.save_config(None)
                # Notify success
                if self.on_connection_success:
                    self.on_connection_success(self.api_client)
            else:
                self.status_text.value = f"✗ {message}"
                self.status_text.color = ft.Colors.RED

        except ValueError:
            self.status_text.value = "✗ Ungültiger Port. Bitte geben Sie eine Zahl ein."
            self.status_text.color = ft.Colors.RED
        except Exception as ex:
            self.status_text.value = f"✗ Fehler: {str(ex)}"
            self.status_text.color = ft.Colors.RED
        finally:
            if self.test_button:
                self.test_button.disabled = False
            if self.container:
                self.container.update()

    def save_config(self, e):
        """Save connection configuration"""
        # Check if UI elements are initialized
        if not self.port_field or not self.host_field or not self.username_field:
            return
        if not self.password_field or not self.https_switch:
            return

        try:
            port = int(self.port_field.value) if self.port_field.value else 8000
            self.config.set('connection.host', self.host_field.value)
            self.config.set('connection.port', port)
            self.config.set('connection.username', self.username_field.value)
            self.config.set('connection.password', self.password_field.value)
            self.config.set('connection.use_https', self.https_switch.value)
            self.config.save_config()

            # Show success message only if not called from test_connection
            if e is not None and self.status_text and self.container:
                self.status_text.value = "✓ Konfiguration gespeichert"
                self.status_text.color = ft.Colors.GREEN
                self.container.update()

        except Exception as ex:
            if self.status_text and self.container:
                self.status_text.value = f"✗ Fehler beim Speichern: {str(ex)}"
                self.status_text.color = ft.Colors.RED
                self.container.update()

    def get_api_client(self):
        """Get the current API client instance"""
        return self.api_client
