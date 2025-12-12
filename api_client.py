"""
Axxon One API Client
Handles communication with Axxon One VMS API
"""

import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from io import BytesIO
from requests.auth import HTTPBasicAuth


class AxxonAPIClient:
    """Client for interacting with Axxon One API"""

    def __init__(self, host: str, port: int, username: str, password: str, use_https: bool = False):
        """
        Initialize API client

        Args:
            host: Server IP address
            port: Server port
            username: API username
            password: API password
            use_https: Use HTTPS instead of HTTP
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.protocol = "https" if use_https else "http"
        self.base_url = f"{self.protocol}://{host}:{port}"
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Axxon One server

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            response = self.session.get(
                f"{self.base_url}/camera/list",
                timeout=10
            )
            if response.status_code == 200:
                return True, "Verbindung erfolgreich!"
            elif response.status_code == 401:
                return False, "Authentifizierung fehlgeschlagen. Bitte überprüfen Sie Benutzername und Passwort."
            else:
                return False, f"Verbindungsfehler: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"Verbindung zu {self.host}:{self.port} fehlgeschlagen. Server nicht erreichbar."
        except requests.exceptions.Timeout:
            return False, "Zeitüberschreitung bei der Verbindung."
        except Exception as e:
            return False, f"Fehler: {str(e)}"

    def get_camera_list(self) -> List[Dict]:
        """
        Get list of all available cameras

        Returns:
            List of camera dictionaries with id, name, and accessPoint
        """
        try:
            response = self.session.get(
                f"{self.base_url}/camera/list",
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            cameras = []

            # Parse camera data from API response
            # API returns cameras as direct array or under 'cameras' key
            camera_list = data if isinstance(data, list) else data.get('cameras', [])

            for camera in camera_list:
                # Extract video source access point from videoStreams
                video_streams = camera.get('videoStreams', [])
                if video_streams:
                    access_point = video_streams[0].get('accessPoint', '')
                    cameras.append({
                        'id': camera.get('displayId', camera.get('id', '')),
                        'name': camera.get('displayName', camera.get('displayId', 'Unbekannte Kamera')),
                        'accessPoint': access_point,
                        'ipAddress': camera.get('ipAddress', 'N/A')
                    })

            return cameras

        except requests.exceptions.RequestException as e:
            raise Exception(f"Fehler beim Abrufen der Kameraliste: {str(e)}")

    def get_live_snapshot(self, video_source_id: str, width: Optional[int] = None,
                         height: Optional[int] = None) -> bytes:
        """
        Get live snapshot from camera

        Args:
            video_source_id: Camera video source ID (accessPoint)
            width: Optional image width in pixels
            height: Optional image height in pixels

        Returns:
            Image bytes (JPEG)
        """
        # Remove 'hosts/' prefix if present (API expects format: SERVER/DeviceIpint.X/...)
        if video_source_id.startswith('hosts/'):
            video_source_id = video_source_id[6:]  # Remove 'hosts/'

        url = f"{self.base_url}/live/media/snapshot/{video_source_id}"

        params = {}
        if width and height:
            params['w'] = width
            params['h'] = height

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"Fehler beim Abrufen des Live-Snapshots: {str(e)}")

    def get_archive_snapshot(self, video_source_id: str, timestamp: datetime,
                            width: Optional[int] = None, height: Optional[int] = None) -> bytes:
        """
        Get archive snapshot from camera at specific time

        Args:
            video_source_id: Camera video source ID (accessPoint)
            timestamp: Time to retrieve snapshot from
            width: Optional image width in pixels
            height: Optional image height in pixels

        Returns:
            Image bytes (JPEG)
        """
        # Remove 'hosts/' prefix if present (API expects format: SERVER/DeviceIpint.X/...)
        if video_source_id.startswith('hosts/'):
            video_source_id = video_source_id[6:]  # Remove 'hosts/'

        # Format timestamp to ISO format: YYYYMMDDTHHMMSS.mmm
        time_str = timestamp.strftime("%Y%m%dT%H%M%S.000")

        url = f"{self.base_url}/archive/media/{video_source_id}/{time_str}"

        params = {
            'format': 'mjpeg'
        }
        if width and height:
            params['w'] = width
            params['h'] = height

        try:
            # First request returns JSON with stream URLs
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            # For MJPEG format, we might get the image directly or a JSON response
            content_type = response.headers.get('Content-Type', '')

            if 'image' in content_type or 'jpeg' in content_type:
                # Direct image response
                return response.content
            elif 'json' in content_type:
                # JSON response with stream URL - extract first frame
                data = response.json()
                # Try to get httpproxy URL for easier access
                stream_url = data.get('httpproxy', data.get('http', ''))
                if stream_url:
                    # Get the stream and extract first JPEG frame
                    stream_response = self.session.get(stream_url, timeout=30, stream=True)
                    stream_response.raise_for_status()

                    # Extract first JPEG from MJPEG stream
                    return self._extract_first_jpeg_frame(stream_response)
                else:
                    raise Exception("Keine Bild-URL in der Antwort gefunden")
            else:
                # Unknown response type, try to use it as image
                return response.content

        except requests.exceptions.RequestException as e:
            raise Exception(f"Fehler beim Abrufen des Archiv-Snapshots: {str(e)}")

    def _extract_first_jpeg_frame(self, stream_response) -> bytes:
        """
        Extract first JPEG frame from MJPEG stream

        Args:
            stream_response: Response object with MJPEG stream

        Returns:
            JPEG image bytes
        """
        boundary = None
        image_data = BytesIO()
        in_image = False

        for chunk in stream_response.iter_content(chunk_size=8192):
            if not chunk:
                continue

            # Look for JPEG start marker (FFD8)
            if b'\xff\xd8' in chunk:
                in_image = True
                start_idx = chunk.find(b'\xff\xd8')
                image_data.write(chunk[start_idx:])
            elif in_image:
                image_data.write(chunk)

                # Look for JPEG end marker (FFD9)
                if b'\xff\xd9' in chunk:
                    # Found complete JPEG
                    break

        result = image_data.getvalue()
        if len(result) < 100:  # Too small to be a valid JPEG
            raise Exception("Kein gültiges JPEG-Bild im Stream gefunden")

        return result

    def close(self):
        """Close the session"""
        self.session.close()
