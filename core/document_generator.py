import os
import re
import time
import base64
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from core.security import SecurityPolicy
from core.logger import logger

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de doble pasada para calcular el total de páginas y agregar
    encabezado formal y pie de página 'Página X de Y' estilo APA.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        doc_title = getattr(self, "_doc_title", "JARVIS — Documento Formal")
        if len(doc_title) > 55:
            doc_title = doc_title[:52] + "..."

        # Encabezado (solo páginas > 1)
        if self._pageNumber > 1:
            self.drawString(72, 750, doc_title.upper())
            self.drawRightString(612 - 72, 750, "ESTÁNDAR APA / PDF")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(72, 744, 612 - 72, 744)

        # Pie de página en todas las páginas
        text_page = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 72, 40, text_page)
        self.drawString(72, 40, "Generado por JARVIS Assistant — Formato Formal")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(72, 52, 612 - 72, 52)
        self.restoreState()


class DocumentGenerator:
    """
    Generador unificado de documentos estéticos y editables (PDF y DOCX)
    bajo estándares formales de maquetación (APA, tipografía limpia, márgenes de 1 pulgada).
    """

    @classmethod
    def _parse_markdown_formatting(cls, text: str) -> str:
        """Convierte marcas básicas de markdown a etiquetas XML soportadas por ReportLab."""
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#2C5282">\1</font>', text)
        return text

    _last_session_image: Optional[Path] = None

    @classmethod
    def set_last_session_image(cls, img_path: Path):
        """Registra la ruta de la última imagen adjunta, subida o pegada en la sesión."""
        cls._last_session_image = img_path

    @classmethod
    def _find_image_file(cls, path_str: str) -> Optional[Path]:
        """Localiza un archivo de imagen en el disco o en carpetas de usuario autorizadas."""
        return cls._resolve_image_file(path_str)

    @classmethod
    def _resolve_image_file(cls, path_str: str, alt_text: str = "") -> Optional[Path]:
        """
        Localiza, descarga o sintetiza un archivo de imagen válido para incrustar en el documento.
        Soporta:
        1. Rutas locales directas o en Pictures, Desktop, Documents, Downloads.
        2. URLs web completas (http://, https://) con descarga y caché local.
        3. URIs codificadas en Base64 (data:image/...).
        4. Referencias a imágenes adjuntas o pegadas ('adjunto', 'clipboard', 'imagen_adjunta').
        5. Auto-generación de imágenes inexistentes usando el prompt o alt descriptivo.
        """
        if not path_str or not path_str.strip():
            if alt_text:
                return cls._synthesize_image(alt_text)
            return None

        clean_path = path_str.strip().strip('"\'<>').strip()

        # 1. Base64 data URI
        if clean_path.startswith("data:image/"):
            try:
                header, b64_data = clean_path.split(",", 1)
                img_bytes = base64.b64decode(b64_data)
                cache_dir = SecurityPolicy.get_actual_user_dir("Pictures") / ".jarvis_cache"
                cache_dir.mkdir(parents=True, exist_ok=True)
                out_path = cache_dir / f"b64_img_{int(time.time() * 1000)}.png"
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                return out_path
            except Exception as e:
                logger.warning(f"[DocumentGenerator] Error decodificando imagen base64: {e}")

        # 2. Descarga de imagen remota por HTTP / HTTPS
        if clean_path.startswith(("http://", "https://")):
            try:
                cache_dir = SecurityPolicy.get_actual_user_dir("Pictures") / ".jarvis_cache"
                cache_dir.mkdir(parents=True, exist_ok=True)
                url_slug = re.sub(r'[^a-zA-Z0-9]', '_', clean_path[-25:]).strip('_') or "web"
                out_path = cache_dir / f"web_{url_slug}_{int(time.time())}.png"
                with httpx.Client(timeout=20.0, follow_redirects=True) as client:
                    resp = client.get(clean_path)
                    if resp.status_code == 200 and len(resp.content) > 1024:
                        with open(out_path, "wb") as f:
                            f.write(resp.content)
                        return out_path
            except Exception as e:
                logger.warning(f"[DocumentGenerator] Error descargando imagen web {clean_path}: {e}")

        # 3. Referencia a la última imagen adjunta o pegada en la sesión
        lowered = clean_path.lower()
        if any(k in lowered for k in ["adjunt", "clipboard", "foto", "portapapeles", "imagen_adjunta"]) or lowered == "imagen":
            if cls._last_session_image and cls._last_session_image.exists():
                return cls._last_session_image

        # 4. Archivo local existente
        if clean_path.startswith("file:///"):
            clean_path = clean_path[8:]

        p = Path(clean_path)
        if p.exists() and p.is_file():
            return p

        for folder in ["Pictures", "Desktop", "Documents", "Downloads"]:
            d = SecurityPolicy.get_actual_user_dir(folder)
            cand = d / clean_path
            if cand.exists() and cand.is_file():
                return cand
            cand_name = d / p.name
            if cand_name.exists() and cand_name.is_file():
                return cand_name

        # 5. Si el archivo no existe físicamente en disco, sintetizar la imagen bajo demanda
        prompt = alt_text.strip() if alt_text and len(alt_text.strip()) > 3 else p.stem.replace('_', ' ').replace('-', ' ').strip()
        if prompt and not any(k in prompt.lower() for k in ["unknown", "none", "null", "undefined"]):
            return cls._synthesize_image(prompt, clean_path)

        return None

    @classmethod
    def _synthesize_image(cls, prompt: str, target_filename: Optional[str] = None) -> Optional[Path]:
        """Auto-genera una ilustración relevante mediante IA y la guarda en la carpeta de Imágenes."""
        try:
            enhanced_prompt = f"{prompt}, clear details, high quality, professional illustration, realistic"
            enc_prompt = urllib.parse.quote(enhanced_prompt)
            seed = int(time.time() * 1000) % 1000000
            gen_url = f"https://image.pollinations.ai/prompt/{enc_prompt}?width=768&height=512&nologo=true&seed={seed}"

            pics_dir = SecurityPolicy.get_actual_user_dir("Pictures")
            pics_dir.mkdir(parents=True, exist_ok=True)

            if target_filename and target_filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                out_path = pics_dir / Path(target_filename).name
            else:
                slug = re.sub(r'[^a-zA-Z0-9]', '_', prompt[:20]).strip('_').lower() or "figura"
                out_path = pics_dir / f"jarvis_{slug}_{int(time.time())}.png"

            with httpx.Client(timeout=25.0, follow_redirects=True) as client:
                resp = client.get(gen_url)
                if resp.status_code == 200 and len(resp.content) > 2048:
                    with open(out_path, "wb") as f:
                        f.write(resp.content)
                    logger.info(f"[DocumentGenerator] Imagen auto-sintetizada con éxito: {out_path}")
                    return out_path
        except Exception as ge:
            logger.warning(f"[DocumentGenerator] Error en auto-síntesis de imagen ({prompt}): {ge}")
        return None

    @classmethod
    def _parse_blocks(cls, content: str):
        """Parsea el contenido markdown en bloques estructurados (encabezados, tablas, imágenes, viñetas, párrafos)."""
        blocks = []
        lines = content.split("\n")
        i = 0
        n = len(lines)
        img_md_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        img_html_pattern = re.compile(r'<img\s+[^>]*?src=[\"\'](.*?)[\"\'][^>]*?>', re.IGNORECASE)
        html_alt_pattern = re.compile(r'alt=[\"\'](.*?)[\"\']', re.IGNORECASE)

        while i < n:
            raw_line = lines[i]
            line = raw_line.strip()
            if not line:
                i += 1
                continue

            # 1. Tabla Markdown: líneas consecutivas con delimitadores |
            if line.startswith("|") and line.endswith("|"):
                table_lines = []
                while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1

                rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.strip("|").split("|")]
                    # Omitir fila separadora tipo |---|---|
                    if all(re.match(r'^:?-+:?$', c) for c in cells if c):
                        continue
                    rows.append(cells)

                if rows:
                    blocks.append({"type": "table", "rows": rows})
                continue

            # 2. Imagen Markdown o HTML
            img_md_match = img_md_pattern.search(line)
            img_html_match = img_html_pattern.search(line)
            if img_md_match:
                prefix = line[:img_md_match.start()].strip()
                suffix = line[img_md_match.end():].strip()
                if prefix:
                    blocks.append({"type": "paragraph", "text": prefix})
                alt = img_md_match.group(1).strip()
                src = img_md_match.group(2).strip().strip('"\'<>')
                blocks.append({"type": "image", "alt": alt, "src": src})
                if suffix:
                    blocks.append({"type": "paragraph", "text": suffix})
                i += 1
                continue
            elif img_html_match:
                prefix = line[:img_html_match.start()].strip()
                suffix = line[img_html_match.end():].strip()
                if prefix:
                    blocks.append({"type": "paragraph", "text": prefix})
                src = img_html_match.group(1).strip().strip('"\'<>')
                alt_m = html_alt_pattern.search(img_html_match.group(0))
                alt = alt_m.group(1).strip() if alt_m else ""
                blocks.append({"type": "image", "alt": alt, "src": src})
                if suffix:
                    blocks.append({"type": "paragraph", "text": suffix})
                i += 1
                continue

            # 3. Encabezados
            if line.startswith("### "):
                blocks.append({"type": "h2", "text": line[4:].strip()})
            elif line.startswith("## "):
                blocks.append({"type": "h1", "text": line[3:].strip()})
            elif line.startswith("# "):
                blocks.append({"type": "h1", "text": line[2:].strip()})
            elif line.startswith(("-", "*", "•")):
                blocks.append({"type": "bullet", "text": line.lstrip("-*• ").strip()})
            else:
                blocks.append({"type": "paragraph", "text": line})

            i += 1

        return blocks

    @classmethod
    def create_pdf(
        cls,
        filename: str,
        title: str,
        content: str,
        standard: str = "pdf/a",
        author: str = "Dante",
        location: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Genera un documento PDF profesional con márgenes APA de 1 pulgada,
        encabezados jerárquicos, paleta cromática sobria y paginación automática.
        """
        loc_str = location.lower().strip()
        target_dir = SecurityPolicy.get_actual_user_dir("Desktop")
        if loc_str in ["documents", "documentos"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Documents")
        elif loc_str in ["downloads", "descargas"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Downloads")

        clean_name = filename.strip()
        if not clean_name.lower().endswith(".pdf"):
            clean_name += ".pdf"

        target_file_path = target_dir / clean_name
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(str(target_file_path), must_exist=False)
        if not is_safe or not safe_path:
            return {
                "success": False,
                "error": err or "BLOCKED_ACTION",
                "message": "Acceso denegado: la ubicación de guardado no está autorizada."
            }

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            doc = SimpleDocTemplate(
                str(safe_path),
                pagesize=letter,
                leftMargin=inch,
                rightMargin=inch,
                topMargin=inch,
                bottomMargin=inch,
                title=title,
                author=author
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#1A365D'),
                spaceAfter=6
            )
            meta_style = ParagraphStyle(
                'DocMeta',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor('#4A5568'),
                spaceAfter=14
            )
            h1_style = ParagraphStyle(
                'DocH1',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=13.5,
                leading=17,
                textColor=colors.HexColor('#1A365D'),
                spaceBefore=14,
                spaceAfter=6,
                keepWithNext=True
            )
            h2_style = ParagraphStyle(
                'DocH2',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=11.5,
                leading=15,
                textColor=colors.HexColor('#2B6CB0'),
                spaceBefore=10,
                spaceAfter=4,
                keepWithNext=True
            )
            body_style = ParagraphStyle(
                'DocBody',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                leading=14.5,
                textColor=colors.HexColor('#2D3748'),
                alignment=4, # Justificado
                spaceAfter=8
            )
            bullet_style = ParagraphStyle(
                'DocBullet',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#2D3748'),
                leftIndent=16,
                spaceAfter=4
            )

            table_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=9.5,
                leading=12,
                textColor=colors.whitesmoke,
                alignment=0
            )
            table_cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#2D3748'),
                alignment=0
            )
            caption_style = ParagraphStyle(
                'DocCaption',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#718096'),
                alignment=1, # Centrado
                spaceAfter=8
            )

            story = []

            # Encabezado del documento
            story.append(Paragraph(cls._parse_markdown_formatting(title), title_style))
            today_str = datetime.now().strftime("%d de %B de %Y")
            meta_text = f"<b>Autor:</b> {author} &nbsp;|&nbsp; <b>Fecha:</b> {today_str} &nbsp;|&nbsp; <b>Estándar:</b> {standard.upper()}"
            story.append(Paragraph(meta_text, meta_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=14))

            # Procesar el cuerpo del contenido estructurado
            blocks = cls._parse_blocks(content)
            figure_counter = 0
            for b in blocks:
                b_type = b["type"]
                if b_type == "h2":
                    clean_h = cls._parse_markdown_formatting(b["text"])
                    story.append(Paragraph(clean_h, h2_style))
                elif b_type == "h1":
                    clean_h = cls._parse_markdown_formatting(b["text"])
                    story.append(Paragraph(clean_h, h1_style))
                elif b_type == "bullet":
                    clean_b = cls._parse_markdown_formatting(b["text"])
                    story.append(Paragraph(f"&bull; {clean_b}", bullet_style))
                elif b_type == "paragraph":
                    clean_p = cls._parse_markdown_formatting(b["text"])
                    story.append(Paragraph(clean_p, body_style))
                elif b_type == "table":
                    table_rows = b.get("rows", [])
                    if table_rows:
                        max_cols = max(len(r) for r in table_rows)
                        norm_rows = []
                        for r_idx, r in enumerate(table_rows):
                            r_pad = r + [""] * (max_cols - len(r))
                            cells = []
                            for c in r_pad:
                                style = table_header_style if r_idx == 0 else table_cell_style
                                cells.append(Paragraph(cls._parse_markdown_formatting(c), style))
                            norm_rows.append(cells)
                        col_w = 468.0 / max_cols if max_cols > 0 else 468.0
                        t = Table(norm_rows, colWidths=[col_w] * max_cols)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                            ('TOPPADDING', (0, 0), (-1, -1), 5),
                            ('LEFTPADDING', (0, 0), (-1, -1), 6),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        story.append(Spacer(1, 4))
                        story.append(t)
                        story.append(Spacer(1, 8))
                elif b_type == "image":
                    figure_counter += 1
                    alt_desc = b.get("alt", "").strip()
                    img_file = cls._resolve_image_file(b["src"], alt_text=alt_desc)
                    caption_text = f"<b>Figura {figure_counter}.</b> <i>{alt_desc}</i>" if alt_desc else f"<b>Figura {figure_counter}.</b>"
                    caption_p = Paragraph(caption_text, caption_style)

                    if img_file and img_file.exists():
                        try:
                            with PILImage.open(img_file) as im:
                                orig_w, orig_h = im.size
                                if im.mode not in ("RGB", "L", "RGBA"):
                                    im = im.convert("RGB")
                            aspect = orig_h / orig_w if orig_w > 0 else 1.0
                            target_w = min(468.0, float(orig_w))
                            target_h = target_w * aspect
                            if target_h > 320.0:
                                target_h = 320.0
                                target_w = target_h / aspect

                            rl_img = RLImage(str(img_file), width=target_w, height=target_h, hAlign='CENTER')
                            # KeepTogether previene que la figura y su rótulo queden huérfanos entre saltos de página
                            story.append(KeepTogether([
                                Spacer(1, 6),
                                rl_img,
                                Spacer(1, 4),
                                caption_p,
                                Spacer(1, 10)
                            ]))
                        except Exception as ie:
                            logger.warning(f"[DocumentGenerator] Error incrustando imagen {img_file}: {ie}")
                            box_t = Table([[Paragraph(f"[ 📷 Figura {figure_counter}: {alt_desc or 'Ilustración'} ]", caption_style)]], colWidths=[468.0])
                            box_t.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7FAFC')),
                                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('TOPPADDING', (0, 0), (-1, -1), 14),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                            ]))
                            story.append(KeepTogether([
                                Spacer(1, 6),
                                box_t,
                                Spacer(1, 4),
                                caption_p,
                                Spacer(1, 10)
                            ]))
                    else:
                        box_t = Table([[Paragraph(f"[ 📷 Figura {figure_counter}: {alt_desc or 'Ilustración'} ]", caption_style)]], colWidths=[468.0])
                        box_t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7FAFC')),
                            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E0')),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('TOPPADDING', (0, 0), (-1, -1), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                        ]))
                        story.append(KeepTogether([
                            Spacer(1, 6),
                            box_t,
                            Spacer(1, 4),
                            caption_p,
                            Spacer(1, 10)
                        ]))

            def _canvas_factory(*args, **kwargs):
                canv = NumberedCanvas(*args, **kwargs)
                canv._doc_title = title
                return canv

            doc.build(story, canvasmaker=_canvas_factory)
            file_size = safe_path.stat().st_size if safe_path.exists() else 0

            logger.info(f"[DocumentGenerator] PDF creado: {safe_path} ({file_size} bytes)")
            return {
                "success": True,
                "file_name": safe_path.name,
                "path": str(safe_path),
                "bytes_written": file_size,
                "format": "PDF",
                "standard": standard.upper(),
                "message": f"Documento PDF '{safe_path.name}' generado con éxito en formato APA en tu {location.capitalize()}."
            }

        except Exception as e:
            logger.error(f"[DocumentGenerator] Error creando PDF: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al generar el documento PDF: {e}"
            }

    @classmethod
    def create_docx(
        cls,
        filename: str,
        title: str,
        content: str,
        author: str = "Dante",
        location: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Genera un documento editable DOCX (Microsoft Word) con estilo limpio,
        márgenes estándar de 1 pulgada y tipografía Calibri.
        """
        loc_str = location.lower().strip()
        target_dir = SecurityPolicy.get_actual_user_dir("Desktop")
        if loc_str in ["documents", "documentos"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Documents")
        elif loc_str in ["downloads", "descargas"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Downloads")

        clean_name = filename.strip()
        if not clean_name.lower().endswith(".docx"):
            clean_name += ".docx"

        target_file_path = target_dir / clean_name
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(str(target_file_path), must_exist=False)
        if not is_safe or not safe_path:
            return {
                "success": False,
                "error": err or "BLOCKED_ACTION",
                "message": "Acceso denegado: la ubicación de guardado no está autorizada."
            }

        try:
            import docx
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            doc = docx.Document()

            # Márgenes de 1 pulgada (APA)
            for sec in doc.sections:
                sec.top_margin = Inches(1)
                sec.bottom_margin = Inches(1)
                sec.left_margin = Inches(1)
                sec.right_margin = Inches(1)

            # Título principal
            p_title = doc.add_paragraph()
            r_title = p_title.add_run(title)
            r_title.font.name = "Calibri"
            r_title.font.size = Pt(20)
            r_title.font.bold = True
            r_title.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
            p_title.paragraph_format.space_after = Pt(4)

            # Metadatos
            today_str = datetime.now().strftime("%d de %B de %Y")
            p_meta = doc.add_paragraph()
            r_meta = p_meta.add_run(f"Autor: {author}  |  Fecha: {today_str}  |  JARVIS Assistant")
            r_meta.font.name = "Calibri"
            r_meta.font.size = Pt(9.5)
            r_meta.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
            p_meta.paragraph_format.space_after = Pt(14)

            # Contenido estructurado
            blocks = cls._parse_blocks(content)
            figure_counter = 0
            for b in blocks:
                b_type = b["type"]
                if b_type == "h2":
                    h = doc.add_heading(level=2)
                    r = h.add_run(b["text"])
                    r.font.name = "Calibri"
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
                    h.paragraph_format.space_before = Pt(10)
                    h.paragraph_format.space_after = Pt(3)
                elif b_type == "h1":
                    h = doc.add_heading(level=1)
                    r = h.add_run(b["text"])
                    r.font.name = "Calibri"
                    r.font.size = Pt(14)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
                    h.paragraph_format.space_before = Pt(14)
                    h.paragraph_format.space_after = Pt(4)
                elif b_type == "bullet":
                    bp = doc.add_paragraph(style="List Bullet")
                    r = bp.add_run(b["text"])
                    r.font.name = "Calibri"
                    r.font.size = Pt(11)
                    bp.paragraph_format.space_after = Pt(3)
                elif b_type == "paragraph":
                    p = doc.add_paragraph()
                    r = p.add_run(b["text"])
                    r.font.name = "Calibri"
                    r.font.size = Pt(11)
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(6)
                elif b_type == "table":
                    table_rows = b.get("rows", [])
                    if table_rows:
                        max_cols = max(len(r) for r in table_rows)
                        t = doc.add_table(rows=len(table_rows), cols=max_cols)
                        try:
                            t.style = 'Light Shading Accent 1'
                        except Exception:
                            t.style = 'Table Grid'
                        for r_idx, row in enumerate(table_rows):
                            r_pad = row + [""] * (max_cols - len(row))
                            for c_idx, cell in enumerate(r_pad):
                                p = t.cell(r_idx, c_idx).paragraphs[0]
                                p.text = cell
                                for r in p.runs:
                                    r.font.name = "Calibri"
                                    r.font.size = Pt(10)
                                    if r_idx == 0:
                                        r.font.bold = True
                                        r.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
                        p_sp = doc.add_paragraph()
                        p_sp.paragraph_format.space_after = Pt(6)
                elif b_type == "image":
                    figure_counter += 1
                    alt_desc = b.get("alt", "").strip()
                    img_file = cls._resolve_image_file(b["src"], alt_text=alt_desc)
                    if img_file and img_file.exists():
                        try:
                            p_img = doc.add_paragraph()
                            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            p_img.paragraph_format.space_before = Pt(8)
                            p_img.paragraph_format.space_after = Pt(2)
                            r_img = p_img.add_run()
                            r_img.add_picture(str(img_file), width=Inches(5.0))

                            p_cap = doc.add_paragraph()
                            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            r_fig = p_cap.add_run(f"Figura {figure_counter}. ")
                            r_fig.font.name = "Calibri"
                            r_fig.font.size = Pt(9)
                            r_fig.font.bold = True
                            r_fig.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

                            if alt_desc:
                                r_desc = p_cap.add_run(alt_desc)
                                r_desc.font.name = "Calibri"
                                r_desc.font.size = Pt(9)
                                r_desc.font.italic = True
                                r_desc.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
                            p_cap.paragraph_format.space_after = Pt(10)
                        except Exception as ie:
                            logger.warning(f"[DocumentGenerator] Error incrustando imagen DOCX {img_file}: {ie}")

            doc.save(str(safe_path))
            file_size = safe_path.stat().st_size if safe_path.exists() else 0
            logger.info(f"[DocumentGenerator] DOCX creado: {safe_path} ({file_size} bytes)")
            return {
                "success": True,
                "file_name": safe_path.name,
                "path": str(safe_path),
                "bytes_written": file_size,
                "format": "DOCX",
                "message": f"Documento Word '{safe_path.name}' generado con éxito en tu {location.capitalize()}."
            }

        except Exception as e:
            logger.error(f"[DocumentGenerator] Error creando DOCX: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al generar el documento Word: {e}"
            }
