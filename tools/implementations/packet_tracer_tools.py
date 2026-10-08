"""
JARVIS Cisco Packet Tracer Tools
Herramientas integradas para resolver talleres de telemática y generar archivos .pkt
programáticos con topologías completas, configuraciones IOS y zonas coloreadas.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from tools.router import BaseTool, ToolType
from core.pkt_engine.pdf_solver import TelematicaLabSolver
from core.pkt_engine.builder import PktBuilder
from core.logger import logger


class SolveTelematicaLabTool(BaseTool):
    name = "solve_telematica_lab"
    description = (
        "Resuelve un taller o guía de Telemática y redes de Cisco Packet Tracer. "
        "Construye la topología .pkt con switches C2960 de 48 puertos, PCs, direccionamiento IP, "
        "VLANs (10-50, 99, 666), enlaces troncales y zonas coloreadas por piso, además del informe "
        "académico completo en PDF y Markdown con respuestas a preguntas teóricas y matrices de pruebas."
    )
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "pdf_path": {
                "type": "string",
                "description": "Ruta opcional al archivo PDF del taller (ej. 'C:/Users/6dant/OneDrive/Desktop/Asignatura_TELEMATICA I_GUIA1 (1).pdf')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directorio destino para guardar el .pkt y los informes de solución."
            }
        }
    }

    async def execute(self, pdf_path: Optional[str] = None, output_dir: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if not output_dir:
            output_dir = r"C:\Users\6dant\OneDrive\Desktop\trabajo telematica"
        
        try:
            solver = TelematicaLabSolver()
            results = await asyncio.to_thread(solver.solve_lab, output_dir)
            logger.info(f"[SolveTelematicaLabTool] Taller resuelto con éxito en {output_dir}")
            return {
                "success": True,
                "data": results,
                "error": None
            }
        except Exception as e:
            logger.error(f"[SolveTelematicaLabTool] Error resolviendo taller: {e}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }


class GeneratePktTool(BaseTool):
    name = "generate_packet_tracer_pkt"
    description = (
        "Genera un archivo nativo .pkt para Cisco Packet Tracer con dispositivos (Switches, PCs), "
        "enlaces de cable, asignación de VLANs y zonas rectangulares coloreadas."
    )
    tool_type = ToolType.ACTION
    parameters_schema = {
        "type": "object",
        "properties": {
            "output_pkt_path": {
                "type": "string",
                "description": "Ruta destino del archivo .pkt a generar."
            },
            "title": {
                "type": "string",
                "description": "Título o descripción de la red para la nota en el lienzo."
            },
            "switches": {
                "type": "array",
                "description": "Lista de switches a agregar [{'name': 'SW1', 'x': 400, 'y': 300, 'vlans': [{'id': '10', 'name': 'V10'}]}]",
                "items": {"type": "object"}
            },
            "pcs": {
                "type": "array",
                "description": "Lista de computadores [{'name': 'PC1', 'x': 200, 'y': 300, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'}]",
                "items": {"type": "object"}
            },
            "links": {
                "type": "array",
                "description": "Lista de conexiones [{'dev1': 'SW1', 'port1': 'FastEthernet0/1', 'dev2': 'PC1', 'port2': 'FastEthernet0/1'}]",
                "items": {"type": "object"}
            },
            "zones": {
                "type": "array",
                "description": "Zonas coloreadas [{'x1': 100, 'y1': 100, 'x2': 800, 'y2': 400, 'r': 230, 'g': 240, 'b': 255, 'title': 'Zona 1'}]",
                "items": {"type": "object"}
            }
        },
        "required": ["output_pkt_path"]
    }

    async def execute(
        self,
        output_pkt_path: str,
        title: Optional[str] = None,
        switches: Optional[List[Dict[str, Any]]] = None,
        pcs: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, Any]]] = None,
        zones: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            def _build():
                builder = PktBuilder()
                if title:
                    builder.add_note(100, 30, title)

                if zones:
                    for z in zones:
                        builder.add_zone(
                            z.get("x1", 100),
                            z.get("y1", 100),
                            z.get("x2", 800),
                            z.get("y2", 400),
                            z.get("r", 230),
                            z.get("g", 240),
                            z.get("b", 250),
                            title=z.get("title")
                        )

                if switches:
                    for sw in switches:
                        builder.add_switch(
                            name=sw["name"],
                            x=sw.get("x", 400),
                            y=sw.get("y", 300),
                            vlans=sw.get("vlans"),
                            running_config_lines=sw.get("running_config")
                        )

                if pcs:
                    for pc in pcs:
                        builder.add_pc(
                            name=pc["name"],
                            x=pc.get("x", 200),
                            y=pc.get("y", 300),
                            ip=pc.get("ip", "192.168.1.10"),
                            mask=pc.get("mask", "255.255.255.0"),
                            gateway=pc.get("gateway", "192.168.1.1")
                        )

                if links:
                    for lk in links:
                        builder.connect(
                            dev1_name=lk["dev1"],
                            port1=lk["port1"],
                            dev2_name=lk["dev2"],
                            port2=lk["port2"],
                            cable_type=lk.get("cable_type", "eStraightThrough")
                        )

                builder.export_pkt(output_pkt_path)
                return output_pkt_path

            saved_path = await asyncio.to_thread(_build)
            return {
                "success": True,
                "data": {"output_pkt_path": saved_path},
                "error": None
            }
        except Exception as e:
            logger.error(f"[GeneratePktTool] Error creando .pkt: {e}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
