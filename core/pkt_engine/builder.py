"""
JARVIS Cisco Packet Tracer Topology Builder
Construye topologías Packet Tracer programáticamente con switches, PCs,
vlan trunking, direccionamiento IP, enlaces de cable y zonas coloreadas.
"""

import os
import copy
import uuid
import random
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple

from .crypto import encrypt_xml, decrypt_pkt


class PktBuilder:
    """Constructor programático de archivos .pkt para Cisco Packet Tracer."""

    def __init__(self, template_dir: Optional[str] = None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.template_dir = template_dir

        self.base_xml_path = os.path.join(template_dir, "base.xml")
        self.switch_xml_path = os.path.join(template_dir, "switch.xml")
        self.pc_xml_path = os.path.join(template_dir, "pc.xml")

        self.tree = ET.parse(self.base_xml_path)
        self.root = self.tree.getroot()
        self.network = self.root.find("NETWORK")
        self.devices_elem = self.network.find("DEVICES")
        self.links_elem = self.network.find("LINKS")

        self.rectangles_elem = self.root.find("RECTANGLES")
        if self.rectangles_elem is None:
            self.rectangles_elem = ET.SubElement(self.root, "RECTANGLES")

        self.notes_elem = self.root.find("NOTES")
        if self.notes_elem is None:
            self.notes_elem = ET.SubElement(self.root, "NOTES")

        self.switch_template = ET.parse(self.switch_xml_path).getroot()
        self.pc_template = ET.parse(self.pc_xml_path).getroot()

        self.devices: Dict[str, ET.Element] = {}
        self.device_ref_ids: Dict[str, str] = {}
        self._counter = 1000

    def _generate_ref_id(self) -> str:
        self._counter += 1
        val = random.randint(10**18, 10**19 - 1)
        return f"save-ref-id:{val}"

    def _generate_mac(self, prefix: str = "0001") -> str:
        r1 = random.randint(0x1000, 0xFFFF)
        r2 = random.randint(0x1000, 0xFFFF)
        return f"{prefix}.{r1:04X}.{r2:04X}"

    def add_switch(
        self,
        name: str,
        x: float,
        y: float,
        vlans: Optional[List[Dict[str, str]]] = None,
        running_config_lines: Optional[List[str]] = None,
        port_count: int = 50,
    ) -> ET.Element:
        """
        Agrega un Switch Cisco C2960 de 48 puertos FastEthernet + 2 GigabitEthernet.
        """
        sw = copy.deepcopy(self.switch_template)
        eng = sw.find("ENGINE")
        ws = sw.find("WORKSPACE")

        ref_id = self._generate_ref_id()
        eng.find("NAME").text = name
        sys_name = eng.find("SYS_NAME")
        if sys_name is not None:
            sys_name.text = name

        save_ref = eng.find("SAVE_REF_ID")
        if save_ref is not None:
            save_ref.text = ref_id

        # Coordenadas
        log = ws.find("LOGICAL")
        if log is not None:
            log.find("X").text = str(x)
            log.find("Y").text = str(y)

        # Ajuste de puertos (48 Fa + 2 Gi)
        slot = eng.find(".//SLOT")
        if slot is not None:
            mod = slot.find("MODULE")
            if mod is not None:
                orig_ports = mod.findall("PORT")
                if orig_ports:
                    fe_tpl = copy.deepcopy(orig_ports[0])
                    gi_tpl = copy.deepcopy(orig_ports[min(24, len(orig_ports) - 1)])

                    for p in orig_ports:
                        mod.remove(p)

                    # 48 FastEthernet ports
                    for i in range(48):
                        p = copy.deepcopy(fe_tpl)
                        mac = self._generate_mac(f"00{i+1:02X}")
                        if p.find("MACADDRESS") is not None:
                            p.find("MACADDRESS").text = mac
                        if p.find("BIA") is not None:
                            p.find("BIA").text = mac
                        mod.append(p)

                    # 2 GigabitEthernet ports
                    for i in range(2):
                        p = copy.deepcopy(gi_tpl)
                        mac = self._generate_mac(f"0A{i+1:02X}")
                        if p.find("MACADDRESS") is not None:
                            p.find("MACADDRESS").text = mac
                        if p.find("BIA") is not None:
                            p.find("BIA").text = mac
                        mod.append(p)

        # Configuración de VLANs en tabla XML
        if vlans:
            vlans_elem = eng.find("VLANS")
            if vlans_elem is not None:
                vlans_elem.clear()
                # Siempre incluir VLAN 1 por defecto
                ET.SubElement(
                    vlans_elem, "VLAN", attrib={"name": "default", "number": "1", "rspan": "0"}
                )
                for v in vlans:
                    if str(v.get("id")) != "1":
                        ET.SubElement(
                            vlans_elem,
                            "VLAN",
                            attrib={
                                "name": v.get("name", f"VLAN_{v.get('id')}"),
                                "number": str(v.get("id")),
                                "rspan": "0",
                            },
                        )
                # VLANs por defecto de Cisco (1002-1005)
                for def_num, def_name in [
                    ("1002", "fddi-default"),
                    ("1003", "token-ring-default"),
                    ("1004", "fddinet-default"),
                    ("1005", "trnet-default"),
                ]:
                    ET.SubElement(
                        vlans_elem,
                        "VLAN",
                        attrib={"name": def_name, "number": def_num, "rspan": "0"},
                    )

        # Configuración IOS en RUNNINGCONFIG
        if running_config_lines:
            rc_elem = eng.find("RUNNINGCONFIG")
            if rc_elem is not None:
                rc_elem.clear()
                for line in running_config_lines:
                    ET.SubElement(rc_elem, "LINE").text = line

        self.devices[name] = sw
        self.device_ref_ids[name] = ref_id
        self.devices_elem.append(sw)
        return sw

    def add_pc(
        self,
        name: str,
        x: float,
        y: float,
        ip: str,
        mask: str = "255.255.255.0",
        gateway: str = "192.168.1.1",
    ) -> ET.Element:
        """
        Agrega una estación de trabajo (PC-PT) con configuración de red completa.
        """
        pc = copy.deepcopy(self.pc_template)
        eng = pc.find("ENGINE")
        ws = pc.find("WORKSPACE")

        ref_id = self._generate_ref_id()
        eng.find("NAME").text = name
        save_ref = eng.find("SAVE_REF_ID")
        if save_ref is not None:
            save_ref.text = ref_id

        gw_elem = eng.find("GATEWAY")
        if gw_elem is not None:
            gw_elem.text = gateway

        # Coordenadas
        log = ws.find("LOGICAL")
        if log is not None:
            log.find("X").text = str(x)
            log.find("Y").text = str(y)

        # Configuración de puerto de red
        for port in eng.findall(".//PORT"):
            ptype = port.find("TYPE")
            if ptype is not None and "FastEthernet" in (ptype.text or ""):
                if port.find("IP") is not None:
                    port.find("IP").text = ip
                if port.find("SUBNET") is not None:
                    port.find("SUBNET").text = mask
                if port.find("PORT_GATEWAY") is not None:
                    port.find("PORT_GATEWAY").text = gateway
                mac = self._generate_mac("0002")
                if port.find("MACADDRESS") is not None:
                    port.find("MACADDRESS").text = mac
                if port.find("BIA") is not None:
                    port.find("BIA").text = mac
                break

        self.devices[name] = pc
        self.device_ref_ids[name] = ref_id
        self.devices_elem.append(pc)
        return pc

    def connect(
        self,
        dev1_name: str,
        port1: str,
        dev2_name: str,
        port2: str,
        cable_type: str = "eStraightThrough",
        color: str = "#6ba72e",
    ) -> ET.Element:
        """
        Crea un enlace físico entre dos dispositivos.
        cable_type: 'eStraightThrough' o 'eCrossOver'
        """
        if dev1_name not in self.device_ref_ids or dev2_name not in self.device_ref_ids:
            raise ValueError(f"Dispositivo no encontrado: {dev1_name} o {dev2_name}")

        from_ref = self.device_ref_ids[dev1_name]
        to_ref = self.device_ref_ids[dev2_name]

        link = ET.SubElement(self.links_elem, "LINK")
        ET.SubElement(link, "TYPE").text = "eCopper"

        cable = ET.SubElement(link, "CABLE")
        ET.SubElement(cable, "LENGTH").text = "1"
        ET.SubElement(cable, "FUNCTIONAL").text = "true"
        ET.SubElement(cable, "FROM").text = from_ref
        ET.SubElement(cable, "PORT").text = port1
        ET.SubElement(cable, "TO").text = to_ref
        ET.SubElement(cable, "PORT").text = port2
        ET.SubElement(cable, "GEO_VIEW_COLOR").text = color
        ET.SubElement(cable, "IS_MANAGED_IN_RACK_VIEW").text = "false"
        ET.SubElement(cable, "TYPE").text = cable_type

        return link

    def add_zone(
        self,
        top_left_x: float,
        top_left_y: float,
        bottom_right_x: float,
        bottom_right_y: float,
        r: int,
        g: int,
        b: int,
        title: Optional[str] = None,
        outline_color: str = "#3A506B",
    ) -> ET.Element:
        """
        Agrega un rectángulo visual coloreado en el fondo para separar pisos o áreas de red.
        """
        zone_uuid = f"{{{uuid.uuid4()}}}"
        rect = ET.SubElement(self.rectangles_elem, "RECTANGLE", attrib={"uuid": zone_uuid})

        ET.SubElement(rect, "TopLeftX").text = str(int(top_left_x))
        ET.SubElement(rect, "TopLeftY").text = str(int(top_left_y))
        ET.SubElement(rect, "BottomRightX").text = str(int(bottom_right_x))
        ET.SubElement(rect, "BottomRightY").text = str(int(bottom_right_y))

        color = ET.SubElement(rect, "Color")
        ET.SubElement(color, "Red").text = str(r)
        ET.SubElement(color, "Green").text = str(g)
        ET.SubElement(color, "Blue").text = str(b)

        filled = ET.SubElement(
            rect, "Filled", attrib={"OUTLINECOLOR": outline_color, "OUTLINED": "true"}
        )
        filled.text = "1"
        ET.SubElement(rect, "RECTCLUSTERID").text = "1-1"

        if title:
            self.add_note(top_left_x + 25, top_left_y + 18, title)

        return rect

    def add_note(self, x: float, y: float, text: str) -> ET.Element:
        """
        Agrega una nota de texto en el lienzo lógico.
        """
        note_uuid = f"{{{uuid.uuid4()}}}"
        note = ET.SubElement(self.notes_elem, "NOTE", attrib={"uuid": note_uuid})
        ET.SubElement(note, "X").text = str(int(x))
        ET.SubElement(note, "Y").text = str(int(y))
        ET.SubElement(note, "Z").text = "40000"
        ET.SubElement(note, "NOTECLUSTERID").text = "1-1"
        ET.SubElement(note, "TEXT").text = text
        return note

    def build_xml(self) -> bytes:
        """Genera el contenido XML formateado en memoria."""
        if hasattr(ET, "indent"):
            ET.indent(self.tree, space="  ")
        return ET.tostring(self.root, encoding="utf-8", xml_declaration=True)

    def export_xml(self, output_xml_path: str) -> None:
        """Exporta la topología a un archivo XML descifrado."""
        xml_bytes = self.build_xml()
        with open(output_xml_path, "wb") as f:
            f.write(xml_bytes)

    def export_pkt(self, output_pkt_path: str) -> None:
        """Exporta la topología compilada y cifrada a formato nativo .pkt de Packet Tracer."""
        xml_bytes = self.build_xml()
        pkt_bytes = encrypt_xml(xml_bytes)
        os.makedirs(os.path.dirname(os.path.abspath(output_pkt_path)), exist_ok=True)
        with open(output_pkt_path, "wb") as f:
            f.write(pkt_bytes)
