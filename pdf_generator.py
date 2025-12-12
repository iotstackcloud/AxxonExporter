"""
PDF Generator
Creates professional PDF reports with camera snapshots - Optimized Layout
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from PIL import Image
from io import BytesIO
from datetime import datetime
from typing import Optional, List, Dict
import os


class PDFGenerator:
    """Generates PDF reports with camera snapshots"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.page_width, self.page_height = A4
        self.margin = 1 * cm
        self.c = canvas.Canvas(output_path, pagesize=A4)

    def add_title_page(self, project_name: str, location: str, technician: str,
                      company: str, logo_path: Optional[str] = None):
        """Add title page with project details"""
        y_pos = self.page_height - self.margin

        # Logo
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                aspect = img.width / img.height
                logo_height = 2 * cm
                logo_width = logo_height * aspect

                self.c.drawImage(
                    ImageReader(logo_path),
                    self.margin, y_pos - logo_height,
                    width=logo_width, height=logo_height,
                    preserveAspectRatio=True
                )
                y_pos -= logo_height + 1.5 * cm
            except:
                y_pos -= 1 * cm
        else:
            y_pos -= 1 * cm

        # Title
        self.c.setFont("Helvetica-Bold", 24)
        self.c.setFillColor(colors.black)
        self.c.drawString(self.margin, y_pos, "Kamera-Referenzbilder")

        # Orange underline
        self.c.setStrokeColor(colors.HexColor("#E65100"))
        self.c.setLineWidth(2)
        self.c.line(self.margin, y_pos - 3*mm, self.margin + 7*cm, y_pos - 3*mm)

        y_pos -= 1.5 * cm

        # Project info
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(self.margin, y_pos, "Projektinformationen")
        y_pos -= 0.8 * cm

        details = [
            ("Projekt:", project_name),
            ("Standort:", location),
            ("Techniker:", technician),
            ("Firma:", company),
            ("Datum:", datetime.now().strftime("%d.%m.%Y %H:%M"))
        ]

        for label, value in details:
            if value:
                self.c.setFont("Helvetica-Bold", 10)
                self.c.setFillColor(colors.HexColor("#333333"))
                self.c.drawString(self.margin, y_pos, label)
                self.c.setFont("Helvetica", 10)
                self.c.drawString(self.margin + 2.5*cm, y_pos, str(value))
                y_pos -= 0.5 * cm

        # Footer
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(colors.grey)
        self.c.drawString(self.margin, self.margin, "Axxon Exporter V2.0")

        self.c.showPage()

    def _draw_camera_image(self, image_bytes: bytes, x: float, y: float,
                           max_width: float, max_height: float,
                           camera_name: str, timestamp: str = None):
        """Draw a camera image optimized for 16:9 aspect ratio"""
        try:
            img = Image.open(BytesIO(image_bytes))
            img_width, img_height = img.size
            aspect = img_width / img_height

            # Calculate size to fill available space
            if aspect > max_width / max_height:
                draw_width = max_width
                draw_height = max_width / aspect
            else:
                draw_height = max_height
                draw_width = max_height * aspect

            # Position image at top of cell, no centering vertically
            img_y = y + max_height - draw_height

            # Draw thin border
            self.c.setStrokeColor(colors.HexColor("#DDDDDD"))
            self.c.setLineWidth(0.5)
            self.c.rect(x, img_y, draw_width, draw_height)

            # Draw image
            self.c.drawImage(
                ImageReader(BytesIO(image_bytes)),
                x, img_y,
                width=draw_width, height=draw_height
            )

            # Camera name below image
            self.c.setFont("Helvetica-Bold", 8)
            self.c.setFillColor(colors.black)
            self.c.drawString(x, img_y - 3.5*mm, camera_name[:35])

            # Timestamp
            if timestamp:
                self.c.setFont("Helvetica", 7)
                self.c.setFillColor(colors.grey)
                self.c.drawRightString(x + draw_width, img_y - 3.5*mm, timestamp)

        except Exception as e:
            self.c.setFont("Helvetica", 8)
            self.c.setFillColor(colors.red)
            self.c.drawString(x, y + max_height/2, f"Fehler: {str(e)[:30]}")

    def add_cameras_page_grid(self, cameras: List[Dict], cols: int = 2, rows: int = 3):
        """Add page with cameras in a grid - optimized for 16:9 images"""
        available_width = self.page_width - 2 * self.margin
        available_height = self.page_height - 2 * self.margin - 0.5*cm

        gap_x = 0.4 * cm
        gap_y = 0.8 * cm  # More vertical gap for camera name

        cell_width = (available_width - (cols - 1) * gap_x) / cols
        cell_height = (available_height - (rows - 1) * gap_y) / rows

        # Reserve space for text below image
        image_height = cell_height - 5*mm

        for idx, camera in enumerate(cameras[:cols * rows]):
            col = idx % cols
            row = idx // cols

            x = self.margin + col * (cell_width + gap_x)
            y = self.page_height - self.margin - (row + 1) * cell_height - row * gap_y + 5*mm

            live_image = camera.get('live_image')
            if live_image:
                timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
                self._draw_camera_image(
                    live_image, x, y, cell_width, image_height,
                    camera.get('name', 'Kamera'), timestamp
                )

        # Page number
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(colors.grey)
        self.c.drawRightString(self.page_width - self.margin, self.margin/2,
                               f"Seite {self.c.getPageNumber()}")
        self.c.showPage()

    def add_cameras_page_with_archive(self, cameras: List[Dict]):
        """Add page with 3 cameras, each with live + archive side by side"""
        available_width = self.page_width - 2 * self.margin
        available_height = self.page_height - 2 * self.margin - 0.5*cm

        rows = 3
        gap_y = 0.6 * cm
        gap_x = 0.3 * cm

        row_height = (available_height - (rows - 1) * gap_y) / rows
        image_width = (available_width - gap_x) / 2
        image_height = row_height - 6*mm  # Space for labels

        for idx, camera in enumerate(cameras[:3]):
            row = idx
            y_base = self.page_height - self.margin - (row + 1) * row_height - row * gap_y

            # Camera name header
            self.c.setFont("Helvetica-Bold", 9)
            self.c.setFillColor(colors.black)
            self.c.drawString(self.margin, y_base + row_height - 1*mm, camera.get('name', 'Kamera'))

            y_img = y_base + 5*mm

            # Live image (left)
            live_image = camera.get('live_image')
            if live_image:
                self._draw_small_image(live_image, self.margin, y_img,
                                       image_width, image_height, "Live")

            # Archive image (right)
            archive_image = camera.get('archive_image')
            archive_ts = camera.get('archive_timestamp')
            if archive_image:
                label = f"Archiv {archive_ts.strftime('%d.%m.%Y %H:%M')}" if archive_ts else "Archiv"
                self._draw_small_image(archive_image, self.margin + image_width + gap_x,
                                       y_img, image_width, image_height, label)

        # Page number
        self.c.setFont("Helvetica", 8)
        self.c.setFillColor(colors.grey)
        self.c.drawRightString(self.page_width - self.margin, self.margin/2,
                               f"Seite {self.c.getPageNumber()}")
        self.c.showPage()

    def _draw_small_image(self, image_bytes: bytes, x: float, y: float,
                          max_width: float, max_height: float, label: str):
        """Draw image with label above"""
        try:
            img = Image.open(BytesIO(image_bytes))
            aspect = img.width / img.height

            if aspect > max_width / max_height:
                draw_width = max_width
                draw_height = max_width / aspect
            else:
                draw_height = max_height
                draw_width = max_height * aspect

            # Draw border
            self.c.setStrokeColor(colors.HexColor("#DDDDDD"))
            self.c.setLineWidth(0.5)
            self.c.rect(x, y, draw_width, draw_height)

            # Draw image
            self.c.drawImage(ImageReader(BytesIO(image_bytes)), x, y,
                           width=draw_width, height=draw_height)

            # Label above
            self.c.setFont("Helvetica", 7)
            self.c.setFillColor(colors.grey)
            self.c.drawString(x, y + draw_height + 1*mm, label)

        except Exception as e:
            self.c.setFillColor(colors.red)
            self.c.drawString(x, y, f"Fehler")

    def save(self):
        self.c.save()

    def generate_report(self, cameras_data: List[Dict], project_info: Dict,
                       include_archive: bool = False) -> str:
        """Generate complete PDF report"""
        valid_cameras = [c for c in cameras_data if c.get('live_image')]

        # Title page
        self.add_title_page(
            project_info.get('name', ''),
            project_info.get('location', ''),
            project_info.get('technician', ''),
            project_info.get('company', ''),
            project_info.get('logo_path')
        )

        if include_archive:
            # 3 cameras per page with live + archive
            for i in range(0, len(valid_cameras), 3):
                self.add_cameras_page_with_archive(valid_cameras[i:i+3])
        else:
            # 6 cameras per page (2x3 grid)
            for i in range(0, len(valid_cameras), 6):
                self.add_cameras_page_grid(valid_cameras[i:i+6], cols=2, rows=3)

        self.save()
        return self.output_path
