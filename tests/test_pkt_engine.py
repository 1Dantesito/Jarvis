"""
Tests unitarios para el motor de Cisco Packet Tracer (core.pkt_engine) y sus herramientas asociadas.
"""

import os
import pytest
import xml.etree.ElementTree as ET
from core.pkt_engine.crypto import encrypt_xml, decrypt_pkt
from core.pkt_engine.builder import PktBuilder
from core.pkt_engine.pdf_solver import TelematicaLabSolver
from tools.implementations.packet_tracer_tools import SolveTelematicaLabTool, GeneratePktTool
from tools.router import ToolRouter


def test_crypto_roundtrip():
    original_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<PACKETTRACER5>
  <NETWORK>
    <DEVICES />
    <LINKS />
  </NETWORK>
</PACKETTRACER5>"""
    # Cifrar
    pkt_bytes = encrypt_xml(original_xml)
    assert isinstance(pkt_bytes, bytes)
    assert len(pkt_bytes) > 0

    # Descifrar
    decrypted_xml = decrypt_pkt(pkt_bytes)
    assert b"<PACKETTRACER5>" in decrypted_xml
    assert b"<NETWORK>" in decrypted_xml


def test_pkt_builder(tmp_path):
    builder = PktBuilder()

    # Agregar Switch
    sw = builder.add_switch(
        name="SW-TEST",
        x=400,
        y=300,
        vlans=[{"id": "10", "name": "VENTAS"}],
        running_config_lines=["hostname SW-TEST", "vlan 10"],
    )
    assert sw is not None

    # Agregar PC
    pc = builder.add_pc(
        name="PC-TEST",
        x=200,
        y=300,
        ip="192.168.10.10",
        mask="255.255.255.0",
        gateway="192.168.10.1",
    )
    assert pc is not None

    # Conectar
    link = builder.connect("SW-TEST", "FastEthernet0/1", "PC-TEST", "FastEthernet0/1")
    assert link is not None

    # Zona coloreada y nota
    zone = builder.add_zone(100, 100, 600, 400, 230, 240, 255, title="Zona Pruebas")
    assert zone is not None

    # Exportar XML y PKT
    xml_path = str(tmp_path / "test.xml")
    pkt_path = str(tmp_path / "test.pkt")

    builder.export_xml(xml_path)
    builder.export_pkt(pkt_path)

    assert os.path.exists(xml_path)
    assert os.path.exists(pkt_path)
    assert os.path.getsize(pkt_path) > 1000

    # Verificar que el PKT generado es descifrable
    with open(pkt_path, "rb") as f:
        data = f.read()
    decrypted = decrypt_pkt(data)
    assert b"SW-TEST" in decrypted
    assert b"PC-TEST" in decrypted
    assert b"192.168.10.10" in decrypted


def test_telematica_solver(tmp_path):
    solver = TelematicaLabSolver()
    out_dir = str(tmp_path / "telematica_out")
    res = solver.solve_lab(out_dir)

    assert os.path.exists(res["official_pkt"])
    assert os.path.exists(res["mirror_pkt"])
    assert os.path.exists(res["markdown"])
    assert os.path.exists(res["pdf"])

    # Validar contenidos del markdown
    with open(res["markdown"], "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "KRONOS S.A.S." in md_text
    assert "VLAN 10" in md_text
    assert "SW-PISO-1" in md_text
    assert "VLAN Hopping" in md_text


@pytest.mark.asyncio
async def test_packet_tracer_tools(tmp_path):
    router = ToolRouter()
    solve_tool = SolveTelematicaLabTool()
    gen_tool = GeneratePktTool()

    router.register_tool(solve_tool)
    router.register_tool(gen_tool)

    # Probar ejecución de SolveTelematicaLabTool
    out_dir = str(tmp_path / "tool_out")
    res = await solve_tool.execute(output_dir=out_dir)
    assert res["success"] is True
    assert os.path.exists(res["data"]["official_pkt"])
    assert os.path.exists(res["data"]["pdf"])

    # Probar ejecución de GeneratePktTool
    custom_pkt = str(tmp_path / "custom.pkt")
    res_gen = await gen_tool.execute(
        output_pkt_path=custom_pkt,
        title="Red Demo",
        switches=[{"name": "SW1", "x": 300, "y": 200}],
        pcs=[{"name": "PC1", "x": 100, "y": 200, "ip": "10.0.0.1"}],
        links=[{"dev1": "SW1", "port1": "FastEthernet0/1", "dev2": "PC1", "port2": "FastEthernet0/1"}],
    )
    assert res_gen["success"] is True
    assert os.path.exists(custom_pkt)
