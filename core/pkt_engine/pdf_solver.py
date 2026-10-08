"""
JARVIS Telematics & Cisco Packet Tracer Lab Solver
Resuelve guías de laboratorio de Telemática y genera tanto la topología .pkt
organizada y coloreada como el documento de solución completo con preguntas y matrices.
"""

import os
from typing import Dict, Any, Tuple
from .builder import PktBuilder


class TelematicaLabSolver:
    """
    Solucionador especializado para talleres de Telemática y VLANs en Cisco Packet Tracer.
    """

    def __init__(self):
        self.vlans = [
            {"id": "10", "name": "VENTAS", "subnet": "192.168.10.0/24", "gw": "192.168.10.1"},
            {"id": "20", "name": "CONTRATOS", "subnet": "192.168.20.0/24", "gw": "192.168.20.1"},
            {"id": "30", "name": "JURIDICA", "subnet": "192.168.30.0/24", "gw": "192.168.30.1"},
            {"id": "40", "name": "DIRECTORES", "subnet": "192.168.40.0/24", "gw": "192.168.40.1"},
            {"id": "50", "name": "RRHH", "subnet": "192.168.50.0/24", "gw": "192.168.50.1"},
            {"id": "99", "name": "NATIVA", "subnet": "N/A", "gw": "N/A"},
            {"id": "666", "name": "BLACKHOLE", "subnet": "N/A", "gw": "N/A"},
        ]

        self.port_ranges = [
            {"range": "FastEthernet0/1 - 8", "vlan": 10, "mode": "access", "shutdown": False},
            {"range": "FastEthernet0/9 - 16", "vlan": 20, "mode": "access", "shutdown": False},
            {"range": "FastEthernet0/17 - 24", "vlan": 30, "mode": "access", "shutdown": False},
            {"range": "FastEthernet0/25 - 32", "vlan": 40, "mode": "access", "shutdown": False},
            {"range": "FastEthernet0/33 - 40", "vlan": 50, "mode": "access", "shutdown": False},
            {"range": "FastEthernet0/41 - 48", "vlan": 666, "mode": "access", "shutdown": True},
        ]

        # Definición de Pisos (de arriba hacia abajo: Piso 5 a Piso 1)
        self.floors = [
            {
                "floor_num": 5,
                "sw_name": "SW-PISO-5",
                "title": "PISO 5: ÁREA EJECUTIVA Y GESTIÓN (SW-PISO-5)",
                "color": (225, 238, 252),  # Azul suave
                "y_base": 180,
                "pcs": [
                    {
                        "name": "PC-Directores-P5",
                        "ip": "192.168.40.13",
                        "port": "FastEthernet0/27",
                        "gw": "192.168.40.1",
                        "x": 240,
                        "vlan": 40,
                    },
                    {
                        "name": "PC-Juridica-P5",
                        "ip": "192.168.30.13",
                        "port": "FastEthernet0/19",
                        "gw": "192.168.30.1",
                        "x": 680,
                        "vlan": 30,
                    },
                    {
                        "name": "PC-RRHH-P5",
                        "ip": "192.168.50.13",
                        "port": "FastEthernet0/35",
                        "gw": "192.168.50.1",
                        "x": 860,
                        "vlan": 50,
                    },
                ],
            },
            {
                "floor_num": 4,
                "sw_name": "SW-PISO-4",
                "title": "PISO 4: COMERCIAL Y CONTRATACIÓN (SW-PISO-4)",
                "color": (228, 248, 234),  # Verde suave
                "y_base": 460,
                "pcs": [
                    {
                        "name": "PC-Ventas-P4",
                        "ip": "192.168.10.13",
                        "port": "FastEthernet0/3",
                        "gw": "192.168.10.1",
                        "x": 240,
                        "vlan": 10,
                    },
                    {
                        "name": "PC-Directores-P4",
                        "ip": "192.168.40.12",
                        "port": "FastEthernet0/26",
                        "gw": "192.168.40.1",
                        "x": 680,
                        "vlan": 40,
                    },
                    {
                        "name": "PC-Contratos-P4",
                        "ip": "192.168.20.13",
                        "port": "FastEthernet0/11",
                        "gw": "192.168.20.1",
                        "x": 860,
                        "vlan": 20,
                    },
                ],
            },
            {
                "floor_num": 3,
                "sw_name": "SW-PISO-3",
                "title": "PISO 3: JURÍDICA Y TALENTO HUMANO (SW-PISO-3)",
                "color": (254, 246, 226),  # Ámbar suave
                "y_base": 740,
                "pcs": [
                    {
                        "name": "PC-Contratos-P3",
                        "ip": "192.168.20.12",
                        "port": "FastEthernet0/10",
                        "gw": "192.168.20.1",
                        "x": 240,
                        "vlan": 20,
                    },
                    {
                        "name": "PC-Juridica-P3",
                        "ip": "192.168.30.12",
                        "port": "FastEthernet0/18",
                        "gw": "192.168.30.1",
                        "x": 680,
                        "vlan": 30,
                    },
                    {
                        "name": "PC-RRHH-P3",
                        "ip": "192.168.50.12",
                        "port": "FastEthernet0/34",
                        "gw": "192.168.50.1",
                        "x": 860,
                        "vlan": 50,
                    },
                ],
            },
            {
                "floor_num": 2,
                "sw_name": "SW-PISO-2",
                "title": "PISO 2: CONSULTORÍA Y DIRECCIÓN (SW-PISO-2)",
                "color": (244, 235, 252),  # Violeta suave
                "y_base": 1020,
                "pcs": [
                    {
                        "name": "PC-Ventas-P2",
                        "ip": "192.168.10.12",
                        "port": "FastEthernet0/2",
                        "gw": "192.168.10.1",
                        "x": 240,
                        "vlan": 10,
                    },
                    {
                        "name": "PC-Juridica-P2",
                        "ip": "192.168.30.11",
                        "port": "FastEthernet0/17",
                        "gw": "192.168.30.1",
                        "x": 680,
                        "vlan": 30,
                    },
                    {
                        "name": "PC-Directores-P2",
                        "ip": "192.168.40.11",
                        "port": "FastEthernet0/25",
                        "gw": "192.168.40.1",
                        "x": 860,
                        "vlan": 40,
                    },
                ],
            },
            {
                "floor_num": 1,
                "sw_name": "SW-PISO-1",
                "title": "PISO 1: OPERACIONES Y ATENCIÓN (SW-PISO-1)",
                "color": (254, 234, 238),  # Rosa suave
                "y_base": 1300,
                "pcs": [
                    {
                        "name": "PC-Ventas-P1",
                        "ip": "192.168.10.11",
                        "port": "FastEthernet0/1",
                        "gw": "192.168.10.1",
                        "x": 240,
                        "vlan": 10,
                    },
                    {
                        "name": "PC-Contratos-P1",
                        "ip": "192.168.20.11",
                        "port": "FastEthernet0/9",
                        "gw": "192.168.20.1",
                        "x": 680,
                        "vlan": 20,
                    },
                    {
                        "name": "PC-RRHH-P1",
                        "ip": "192.168.50.11",
                        "port": "FastEthernet0/33",
                        "gw": "192.168.50.1",
                        "x": 860,
                        "vlan": 50,
                    },
                ],
            },
        ]

    def _generate_ios_running_config(self, sw_name: str) -> list[str]:
        """Genera el bloque running-config oficial para cada Switch."""
        lines = [
            "!",
            "version 15.0",
            "no service timestamps log datetime msec",
            "no service timestamps debug datetime msec",
            "no service password-encryption",
            "!",
            f"hostname {sw_name}",
            "!",
            "spanning-tree mode pvst",
            "spanning-tree extend system-id",
            "!",
            "vlan 10",
            " name VENTAS",
            "vlan 20",
            " name CONTRATOS",
            "vlan 30",
            " name JURIDICA",
            "vlan 40",
            " name DIRECTORES",
            "vlan 50",
            " name RRHH",
            "vlan 99",
            " name NATIVA",
            "vlan 666",
            " name BLACKHOLE",
            "!",
        ]

        # Puertos FastEthernet
        for p in range(1, 49):
            lines.append(f"interface FastEthernet0/{p}")
            if 1 <= p <= 8:
                lines.append(" switchport access vlan 10")
                lines.append(" switchport mode access")
            elif 9 <= p <= 16:
                lines.append(" switchport access vlan 20")
                lines.append(" switchport mode access")
            elif 17 <= p <= 24:
                lines.append(" switchport access vlan 30")
                lines.append(" switchport mode access")
            elif 25 <= p <= 32:
                lines.append(" switchport access vlan 40")
                lines.append(" switchport mode access")
            elif 33 <= p <= 40:
                lines.append(" switchport access vlan 50")
                lines.append(" switchport mode access")
            elif 41 <= p <= 48:
                lines.append(" switchport access vlan 666")
                lines.append(" switchport mode access")
                lines.append(" shutdown")
            lines.append("!")

        # Troncales Gigabit
        for g in range(1, 3):
            lines.append(f"interface GigabitEthernet0/{g}")
            lines.append(" switchport trunk native vlan 99")
            lines.append(" switchport mode trunk")
            lines.append("!")

        lines.extend([
            "interface Vlan1",
            " no ip address",
            " shutdown",
            "!",
            "line con 0",
            "line vty 0 4",
            " login",
            "line vty 5 15",
            " login",
            "!",
            "end",
        ])
        return lines

    def generate_pkt_file(self, output_pkt_path: str) -> str:
        """Construye y compila la topología completa en .pkt."""
        builder = PktBuilder()

        # Encabezado General
        builder.add_note(
            120,
            40,
            "🏢 INVERSIONES & CONSULTORÍAS KRONOS S.A.S. — INFRAESTRUCTURA DE RED CORPORATIVA\n"
            "Segmentación de VLANs en Capa 2 (Catalyst 2960-48TT) | Enlaces Troncales Gigabit 802.1Q (Nativa: VLAN 99)\n"
            "Hardening de Seguridad: VLAN 1 Retirada | Puertos no usados Fa0/41-48 en VLAN 666 (Shutdown)",
        )

        # Construir Pisos y Dispositivos
        sw_coords = {}
        for floor in self.floors:
            y_base = floor["y_base"]
            sw_name = floor["sw_name"]
            sw_x = 460
            sw_y = y_base + 60
            sw_coords[sw_name] = (sw_x, sw_y)

            # Zona rectangular coloreada
            r, g, b = floor["color"]
            builder.add_zone(
                top_left_x=100,
                top_left_y=y_base,
                bottom_right_x=1060,
                bottom_right_y=y_base + 240,
                r=r,
                g=g,
                b=b,
                title=f"🏢 {floor['title']}",
            )

            # Agregar Switch de 48 puertos con IOS running-config real
            ios_lines = self._generate_ios_running_config(sw_name)
            builder.add_switch(
                name=sw_name,
                x=sw_x,
                y=sw_y,
                vlans=self.vlans,
                running_config_lines=ios_lines,
                port_count=50,
            )

            # Agregar PCs del piso
            for pc in floor["pcs"]:
                pc_x = pc["x"]
                pc_y = sw_y + 10 if pc_x > sw_x else sw_y - 10
                builder.add_pc(
                    name=pc["name"],
                    x=pc_x,
                    y=pc_y,
                    ip=pc["ip"],
                    mask="255.255.255.0",
                    gateway=pc["gw"],
                )
                # Conectar PC al Switch por el puerto exacto
                builder.connect(
                    dev1_name=sw_name,
                    port1=pc["port"],
                    dev2_name=pc["name"],
                    port2="FastEthernet0/1",
                    cable_type="eStraightThrough",
                )

        # Interconectar Switches en Cascada Vertical (Backbone)
        # Piso 1 Gi0/1 <--> Piso 2 Gi0/1
        # Piso 2 Gi0/2 <--> Piso 3 Gi0/1
        # Piso 3 Gi0/2 <--> Piso 4 Gi0/1
        # Piso 4 Gi0/2 <--> Piso 5 Gi0/1
        builder.connect("SW-PISO-1", "GigabitEthernet0/1", "SW-PISO-2", "GigabitEthernet0/1", "eCrossOver")
        builder.connect("SW-PISO-2", "GigabitEthernet0/2", "SW-PISO-3", "GigabitEthernet0/1", "eCrossOver")
        builder.connect("SW-PISO-3", "GigabitEthernet0/2", "SW-PISO-4", "GigabitEthernet0/1", "eCrossOver")
        builder.connect("SW-PISO-4", "GigabitEthernet0/2", "SW-PISO-5", "GigabitEthernet0/1", "eCrossOver")

        # Leyenda de VLANs en el lateral
        legend_text = (
            "📌 CÓDIGO DE COLORES Y DISTRIBUCIÓN DE VLANS:\n"
            "--------------------------------------------------\n"
            "• VLAN 10 (VENTAS)     : 192.168.10.0/24  -> Puertos Fa0/1 al Fa0/8\n"
            "• VLAN 20 (CONTRATOS)  : 192.168.20.0/24  -> Puertos Fa0/9 al Fa0/16\n"
            "• VLAN 30 (JURIDICA)   : 192.168.30.0/24  -> Puertos Fa0/17 al Fa0/24\n"
            "• VLAN 40 (DIRECTORES) : 192.168.40.0/24  -> Puertos Fa0/25 al Fa0/32\n"
            "• VLAN 50 (RRHH)       : 192.168.50.0/24  -> Puertos Fa0/33 al Fa0/40\n"
            "• VLAN 99 (NATIVA)     : Troncales Gigabit (Gi0/1 y Gi0/2)\n"
            "• VLAN 666 (BLACKHOLE) : Fa0/41 al Fa0/48 (Modo Acceso + Shutdown)"
        )
        builder.add_note(1100, 200, legend_text)

        # Exportar .pkt
        builder.export_pkt(output_pkt_path)
        return output_pkt_path

    def generate_solution_markdown(self, output_md_path: str) -> str:
        """Genera el documento completo en Markdown con todas las respuestas y tablas."""
        content = """# TELEMÁTICA I — SOLUCIÓN OFICIAL DEL TALLER PRÁCTICO
## CONFIGURACIÓN Y SEGMENTACIÓN DE VLANS EN CISCO PACKET TRACER
**Caso de Estudio:** Empresa "Inversiones & Consultorías KRONOS S.A.S."  
**Docente:** Ing. John Jairo Marciales  
**Fecha:** Octubre 2026  

---

## 1. REQUERIMIENTO 1: PLANO FÍSICO ARQUITECTÓNICO (INFRAESTRUCTURA)

Para la entrega a mano en hojas examen/cuadro, el estudiante debe plasmar la siguiente distribución arquitectónica exacta basada en estándares de cableado estructurado **ANSI/TIA-568-C**:

### Guía para la Elaboración del Plano a Mano:
1. **Estructura Vertical del Edificio (5 Pisos):**
   - Dibujar una vista en corte o planta por piso del edificio KRONOS S.A.S.
   - En cada piso se ubica un **Rack de Telecomunicaciones de Piso (IDF)** cerrado con llave, conteniendo el Switch Cisco Catalyst WS-C2960-48TT y un Patch Panel de 48 puertos.
2. **Backbone Vertical (Montante / Riser):**
   - Trazado de ductería vertical rígida que interconecta los Racks de Piso 1 al Piso 5 mediante cable UTP Cat 6A / Fibra Óptica conectado a los puertos GigabitEthernet:
     - Piso 1 (Gi0/1) ➔ Piso 2 (Gi0/1)
     - Piso 2 (Gi0/2) ➔ Piso 3 (Gi0/1)
     - Piso 3 (Gi0/2) ➔ Piso 4 (Gi0/1)
     - Piso 4 (Gi0/2) ➔ Piso 5 (Gi0/1)
3. **Cableado Horizontal y Rosetas RJ-45 por Piso:**
   - Cada puesto de trabajo cuenta con una roseta doble RJ-45 con su respectiva etiqueta de puerto:
     - **Piso 1:** Roseta `R1-01` (Fa0/1 - Ventas), Roseta `R1-09` (Fa0/9 - Contratos), Roseta `R1-33` (Fa0/33 - RRHH).
     - **Piso 2:** Roseta `R2-02` (Fa0/2 - Ventas), Roseta `R2-17` (Fa0/17 - Jurídica), Roseta `R2-25` (Fa0/25 - Directores).
     - **Piso 3:** Roseta `R3-10` (Fa0/10 - Contratos), Roseta `R3-18` (Fa0/18 - Jurídica), Roseta `R3-34` (Fa0/34 - RRHH).
     - **Piso 4:** Roseta `R4-03` (Fa0/3 - Ventas), Roseta `R4-26` (Fa0/26 - Directores), Roseta `R4-11` (Fa0/11 - Contratos).
     - **Piso 5:** Roseta `R5-27` (Fa0/27 - Directores), Roseta `R5-19` (Fa0/19 - Jurídica), Roseta `R5-35` (Fa0/35 - RRHH).

---

## 2. REQUERIMIENTO 2: TOPOLOGÍA LÓGICA EN CISCO PACKET TRACER

La red lógica ha sido compilada en el archivo `KRONOS_TELEMATICA_VLANS.pkt` con:
- **5 Switches Cisco Catalyst WS-C2960-48TT** identificados como `SW-PISO-1` a `SW-PISO-5`.
- **15 Computadores de escritorio (PCs)** conectados estrictamente a los puertos asignados en la guía.
- **División visual por pisos con recuadros coloreados (Liquid Glass style)** y notas técnicas identificando VLANs y subredes.
- **Troncales Gigabit Ethernet 802.1Q** interconectando los switches de piso en cascada vertical.

### Tabla Maestra de Direccionamiento y Puertos:
| Piso | Dispositivo | Nombre PC | Puerto Switch | VLAN ID | Nombre VLAN | Dirección IPv4 | Máscara | Gateway |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Piso 1** | SW-PISO-1 | PC-Ventas-P1 | Fa0/1 | VLAN 10 | VENTAS | 192.168.10.11 | 255.255.255.0 | 192.168.10.1 |
| **Piso 1** | SW-PISO-1 | PC-Contratos-P1 | Fa0/9 | VLAN 20 | CONTRATOS | 192.168.20.11 | 255.255.255.0 | 192.168.20.1 |
| **Piso 1** | SW-PISO-1 | PC-RRHH-P1 | Fa0/33 | VLAN 50 | RRHH | 192.168.50.11 | 255.255.255.0 | 192.168.50.1 |
| **Piso 2** | SW-PISO-2 | PC-Ventas-P2 | Fa0/2 | VLAN 10 | VENTAS | 192.168.10.12 | 255.255.255.0 | 192.168.10.1 |
| **Piso 2** | SW-PISO-2 | PC-Juridica-P2 | Fa0/17 | VLAN 30 | JURIDICA | 192.168.30.11 | 255.255.255.0 | 192.168.30.1 |
| **Piso 2** | SW-PISO-2 | PC-Directores-P2 | Fa0/25 | VLAN 40 | DIRECTORES | 192.168.40.11 | 255.255.255.0 | 192.168.40.1 |
| **Piso 3** | SW-PISO-3 | PC-Contratos-P3 | Fa0/10 | VLAN 20 | CONTRATOS | 192.168.20.12 | 255.255.255.0 | 192.168.20.1 |
| **Piso 3** | SW-PISO-3 | PC-Juridica-P3 | Fa0/18 | VLAN 30 | JURIDICA | 192.168.30.12 | 255.255.255.0 | 192.168.30.1 |
| **Piso 3** | SW-PISO-3 | PC-RRHH-P3 | Fa0/34 | VLAN 50 | RRHH | 192.168.50.12 | 255.255.255.0 | 192.168.50.1 |
| **Piso 4** | SW-PISO-4 | PC-Ventas-P4 | Fa0/3 | VLAN 10 | VENTAS | 192.168.10.13 | 255.255.255.0 | 192.168.10.1 |
| **Piso 4** | SW-PISO-4 | PC-Directores-P4 | Fa0/26 | VLAN 40 | DIRECTORES | 192.168.40.12 | 255.255.255.0 | 192.168.40.1 |
| **Piso 4** | SW-PISO-4 | PC-Contratos-P4 | Fa0/11 | VLAN 20 | CONTRATOS | 192.168.20.13 | 255.255.255.0 | 192.168.20.1 |
| **Piso 5** | SW-PISO-5 | PC-Directores-P5 | Fa0/27 | VLAN 40 | DIRECTORES | 192.168.40.13 | 255.255.255.0 | 192.168.40.1 |
| **Piso 5** | SW-PISO-5 | PC-Juridica-P5 | Fa0/19 | VLAN 30 | JURIDICA | 192.168.30.13 | 255.255.255.0 | 192.168.30.1 |
| **Piso 5** | SW-PISO-5 | PC-RRHH-P5 | Fa0/35 | VLAN 50 | RRHH | 192.168.50.13 | 255.255.255.0 | 192.168.50.1 |

---

## 3. REQUERIMIENTO 3: SCRIPT DE CONFIGURACIÓN CISCO IOS

El siguiente script se ejecuta en modo privilegiado en **TODOS los switches (SW-PISO-1 a SW-PISO-5)**, variando únicamente el comando `hostname`:

```cisco
enable
configure terminal

! 1. Nombre del Switch (SW-PISO-1, SW-PISO-2, SW-PISO-3, SW-PISO-4 o SW-PISO-5)
hostname SW-PISO-1

! 2. Creación e identificación de VLANs
vlan 10
 name VENTAS
vlan 20
 name CONTRATOS
vlan 30
 name JURIDICA
vlan 40
 name DIRECTORES
vlan 50
 name RRHH
vlan 99
 name NATIVA
vlan 666
 name BLACKHOLE
exit

! 3. Asignación masiva por rangos y Hardening de Capa 2
! Puertos Fa0/1 - Fa0/8 -> VLAN 10 (VENTAS)
interface range FastEthernet0/1 - 8
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

! Puertos Fa0/9 - Fa0/16 -> VLAN 20 (CONTRATOS)
interface range FastEthernet0/9 - 16
 switchport mode access
 switchport access vlan 20
 no shutdown
exit

! Puertos Fa0/17 - Fa0/24 -> VLAN 30 (JURIDICA)
interface range FastEthernet0/17 - 24
 switchport mode access
 switchport access vlan 30
 no shutdown
exit

! Puertos Fa0/25 - Fa0/32 -> VLAN 40 (DIRECTORES)
interface range FastEthernet0/25 - 32
 switchport mode access
 switchport access vlan 40
 no shutdown
exit

! Puertos Fa0/33 - Fa0/40 -> VLAN 50 (RRHH)
interface range FastEthernet0/33 - 40
 switchport mode access
 switchport access vlan 50
 no shutdown
exit

! Puertos Fa0/41 - Fa0/48 -> VLAN 666 (BLACKHOLE / Hardening: Apagados)
interface range FastEthernet0/41 - 48
 switchport mode access
 switchport access vlan 666
 shutdown
exit

! 4. Configuración de Enlaces Troncales (GigabitEthernet0/1 y Gi0/2)
interface range GigabitEthernet0/1 - 2
 switchport mode trunk
 switchport trunk native vlan 99
 no shutdown
exit

! 5. Desactivación de la interfaz de administración por defecto VLAN 1
interface Vlan1
 no ip address
 shutdown
exit

end
copy running-config startup-config
```

---

## 4. NUMERAL 6: PREGUNTAS DE CONTEXTO Y ANÁLISIS TEÓRICO

### Pregunta 1: Aislamiento en Capa 2
> **Pregunta:** Si la `PC-Ventas-P1` (192.168.10.11) genera un broadcast ARP, ¿qué dispositivos del edificio recibirán la trama y por qué los usuarios de CONTRATOS en ese mismo piso no la reciben?

**Respuesta Técnica Justificada:**
1. **Dispositivos que la reciben:**  
   La trama broadcast ARP (con dirección MAC de destino `FF:FF:FF:FF:FF:FF`) será recibida **únicamente** por los dispositivos que pertenezcan al mismo dominio de difusión (Broadcast Domain), es decir, a la **VLAN 10**:
   - `PC-Ventas-P2` (Piso 2, 192.168.10.12)
   - `PC-Ventas-P4` (Piso 4, 192.168.10.13)
   - Todos los puertos asignados a la VLAN 10 (Fa0/1 a Fa0/8) en los cinco switches del edificio.
2. **Por qué CONTRATOS no la recibe:**  
   Los switches de Capa 2 operan aislando el tráfico a nivel de tabla de reenvío y etiquetas 802.1Q. Cuando la trama entra por el puerto `Fa0/1`, el switch `SW-PISO-1` la clasifica internamente como perteneciente a la **VLAN 10**. Al propagarse por los enlaces troncales Gigabit, viaja etiquetada con el tag `VLAN 10`. El switch jamás replicará una trama broadcast de la VLAN 10 hacia interfaces asociadas a otras VLANs (como `Fa0/9`, que pertenece a la **VLAN 20 - CONTRATOS**). Esto garantiza la completa segmentación del dominio de colisión y difusión, cumpliendo el principio de mínimo privilegio y confidencialidad en Capa 2.

---

### Pregunta 2: Eliminación de la VLAN 1 y Ataques de VLAN Hopping
> **Pregunta:** ¿Por qué las guías de Hardening de Cisco recomiendan retirar absolutamente todos los puertos de la VLAN 1 y cambiar la VLAN Nativa a un ID diferente (ej. VLAN 99)? Explique qué es un ataque de VLAN Hopping (Salto de VLAN).

**Respuesta Técnica Justificada:**
1. **Razón de Hardening de la VLAN 1:**  
   Por defecto en todos los switches Cisco de fábrica, la VLAN 1 es la VLAN de gestión, la VLAN de acceso predeterminada y la VLAN Nativa en enlaces troncales. Dejar puertos activos en la VLAN 1 expone los protocolos de control del switch (CDP, DTP, PAgP, VTP, STP) y facilita vectores de ataque basados en negociación automática y salto de capa. Cambiar la VLAN nativa a una VLAN sin dispositivos (como la VLAN 99) y enviar los puertos no usados a un pozo ciego (VLAN 666 Blackhole) neutraliza la superficie de ataque.
2. **Explicación del Ataque de VLAN Hopping (Salto de VLAN):**  
   Es una técnica de intrusión en Capa 2 donde un atacante logra enviar paquetes hacia una VLAN a la que normalmente no tiene acceso, evadiendo la segmentación del switch. Existen dos variantes principales:
   - **Switch Spoofing:** El atacante envía tramas falsas de protocolo DTP (*Dynamic Trunking Protocol*) haciéndose pasar por otro switch para negociar un enlace troncal. Si tiene éxito, recibe tráfico de todas las VLANs. (Se mitiga configurando puertos en `switchport mode access` y deshabilitando DTP con `switchport nonegotiate`).
   - **Double Tagging (Doble Etiquetado):** El atacante envía una trama con dos etiquetas 802.1Q. La etiqueta exterior tiene el ID de la **VLAN Nativa** (VLAN 1 por defecto) y la interior el ID de la VLAN víctima (ej. VLAN 40 - Directores). Cuando el primer switch recibe la trama, retira la etiqueta nativa (por diseño estándar de 802.1Q) y la reenvía por el troncal. El switch de destino lee la segunda etiqueta (VLAN 40) y entrega el paquete a la red privada de directores.  
   **Mitigación:** Al cambiar la VLAN Nativa a una VLAN dedicada (VLAN 99) que no coincida con la VLAN de ningún usuario, el doble etiquetado queda completamente inoperante.

---

### Pregunta 3: Mantenimiento y Estándares por "Grupos de Puertos"
> **Pregunta:** ¿Qué ventajas técnicas y administrativas aporta el diseño por "Grupos de Puertos" (ej. puertos 1 al 8 para Ventas) al momento de realizar cableado estructurado y auditorías en el rack del edificio?

**Respuesta Técnica Justificada:**
1. **Estandarización y Determinismo:** Todos los racks de los 5 pisos comparten exactamente la misma plantilla de asignación. Cualquier técnico de soporte o instalador sabe de antemano que la posición física en el Patch Panel (puertos 1-8) corresponde a Ventas, sin necesidad de consultar mapas de red piso por piso.
2. **Eficiencia en Mantenimiento y Reconfiguración:** Permite aplicar configuraciones en bloque utilizando el comando `interface range`, reduciendo el error humano en un 90% comparado con la asignación manual puerto a puerto.
3. **Facilidad de Auditoría y Etiquetado:** Las barras de colores o marquillas en el rack coinciden con el rango de puertos (ej. etiquetas verdes para Fa0/1-8, azules para Fa0/9-16, etc.), permitiendo identificar conexiones anómalas a simple vista durante auditorías de seguridad física.
4. **Seguridad Preventiva:** Al tener los puertos 41 al 48 estrictamente reservados para Blackhole (`shutdown`), cualquier conexión no autorizada en esos puertos queda inmediatamente aislada e inactiva.

---

### Pregunta 4: Ausencia de Enrutamiento Inter-VLAN
> **Pregunta:** En esta topología sin Router, si la `PC-Juridica-P2` intenta comunicarse con `PC-Directores-P2` que están conectadas al mismo switch, ¿por qué falla el envío de datos?

**Respuesta Técnica Justificada:**
1. **Diferente Subred IP (Capa 3):** `PC-Juridica-P2` pertenece a la subred `192.168.30.0/24` y `PC-Directores-P2` a la subred `192.168.40.0/24`. Al comparar la IP de destino con su propia máscara de subred, el stack TCP/IP del emisor determina que el destino está en una **red remota**. Por ende, no envía una trama directa, sino que intenta reenviarla a su **Gateway por Defecto (192.168.30.1)**.
2. **Inexistencia de Gateway / Enrutador:** Dado que la topología está compuesta exclusivamente por switches de Capa 2 (Cisco 2960) y no existe un Router (esquema *Router-on-a-Stick*) ni un Switch de Capa 3 con interfaz SVI enrutada, no hay ninguna entidad que resuelva la solicitud ARP del Gateway ni conmute paquetes entre subredes.
3. **Aislamiento en Capa 2:** Aunque ambos equipos están enchufados al mismo hardware físico (`SW-PISO-2`), pertenecen a etiquetas VLAN distintas (`VLAN 30` vs `VLAN 40`). El switch conmuta tramas basándose únicamente en direcciones MAC dentro del mismo VLAN ID; jamás reenvía una trama entre dos VLANs distintas sin un proceso de enrutamiento. Por tanto, el comando `ping 192.168.40.11` arroja `Destination host unreachable` o `Request timed out`.

---

## 5. NUMERAL 7: MATRIZ DE PRUEBAS DE CONECTIVIDAD Y VALIDACIÓN

| Origen | Destino | Comando de Prueba | Resultado Esperado | Justificación Técnica |
| :--- | :--- | :---: | :---: | :--- |
| **PC-Ventas-P1**<br>(192.168.10.11) | **PC-Ventas-P4**<br>(192.168.10.13) | `ping 192.168.10.13` | **EXITOSO**<br>(Reply from 192.168.10.13, 0% loss) | Ambos equipos pertenecen a la misma subred (`192.168.10.0/24`) y a la misma **VLAN 10**. El tráfico viaja a través de los enlaces troncales Gigabit etiquetado con 802.1Q de forma transparente entre el Piso 1 y el Piso 4. |
| **PC-Juridica-P2**<br>(192.168.30.11) | **PC-Juridica-P5**<br>(192.168.30.13) | `ping 192.168.30.13` | **EXITOSO**<br>(Reply from 192.168.30.13, 0% loss) | Ambos hosts pertenecen a la misma subred (`192.168.30.0/24`) y a la **VLAN 30**. La conmutación de Capa 2 es directa y permitida a través de los troncales Gigabit desde el Piso 2 hasta el Piso 5. |
| **PC-Ventas-P1**<br>(192.168.10.11) | **PC-Contratos-P1**<br>(192.168.20.11) | `ping 192.168.20.11` | **FALLIDO**<br>(Request timed out) | Pertenecen a diferentes VLANs (**VLAN 10 vs VLAN 20**) y diferentes subredes. Al no haber enrutamiento inter-VLAN (Capa 3), el aislamiento de Capa 2 bloquea cualquier comunicación, garantizando la seguridad entre áreas. |
| **PC-RRHH-P3**<br>(192.168.50.12) | **PC-Directores-P4**<br>(192.168.40.12) | `ping 192.168.40.12` | **FALLIDO**<br>(Request timed out) | Pertenecen a diferentes VLANs (**VLAN 50 vs VLAN 40**). La separación de dominios de broadcast impide el intercambio de paquetes entre Recursos Humanos y Directores, preservando la confidencialidad. |

---

*Documento y Topología Packet Tracer generados y certificados por JARVIS AI Assistant v3.1.*
"""
        os.makedirs(os.path.dirname(os.path.abspath(output_md_path)), exist_ok=True)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_md_path

    def generate_solution_pdf(self, output_pdf_path: str) -> str:
        """Genera un PDF profesional utilizando reportlab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

        os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0A2540"),
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0070BA"),
        )
        h1_style = ParagraphStyle(
            "H1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0A2540"),
            spaceBefore=12,
            spaceAfter=6,
        )
        h2_style = ParagraphStyle(
            "H2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#006699"),
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        )
        body_bold = ParagraphStyle(
            "BodyBold",
            parent=body_style,
            fontName="Helvetica-Bold",
        )
        code_style = ParagraphStyle(
            "CodeStyle",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#1A202C"),
            backColor=colors.HexColor("#F7FAFC"),
            spaceBefore=4,
            spaceAfter=6,
        )

        elements = []

        # Encabezado
        elements.append(Paragraph("TELEMÁTICA I — INFORME DE LABORATORIO PRÁCTICO", title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("CONFIGURACIÓN Y SEGMENTACIÓN DE VLANS EN CISCO PACKET TRACER", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("<b>Caso de Estudio:</b> Inversiones & Consultorías KRONOS S.A.S. | <b>Docente:</b> Ing. John Jairo Marciales", ParagraphStyle("Meta", alignment=TA_CENTER, fontSize=8, leading=10)))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0070BA"), spaceAfter=10))

        # Sección 1
        elements.append(Paragraph("1. REQUERIMIENTO 1: PLANO FÍSICO ARQUITECTÓNICO (INFRAESTRUCTURA)", h1_style))
        elements.append(Paragraph(
            "Para la entrega a mano en hojas examen o cuadriculadas según la norma ANSI/TIA-568-C, "
            "se debe graficar la infraestructura vertical y horizontal del edificio corporativo de 5 pisos:", body_style))
        elements.append(Paragraph(
            "• <b>Racks de Telecomunicaciones (IDF):</b> Cada piso alberga un Rack de telecomunicaciones con un Switch "
            "Cisco Catalyst WS-C2960-48TT y un Patch Panel de 48 puertos.<br/>"
            "• <b>Backbone Vertical (Riser):</b> Cableado vertical troncal de alta velocidad por ductos rígidos que "
            "interconecta los racks en cascada mediante los puertos GigabitEthernet (Gi0/1 y Gi0/2).<br/>"
            "• <b>Cableado Horizontal y Rosetas RJ-45:</b> Cada piso contiene rosetas dobles RJ-45 identificadas con la nomenclatura "
            "<i>R[Piso]-[Puerto]</i> (Ej: R1-01 para Fa0/1 en Piso 1, R2-25 para Fa0/25 en Piso 2).", body_style))

        elements.append(Spacer(1, 6))

        # Sección 2
        elements.append(Paragraph("2. REQUERIMIENTO 2: TOPOLOGÍA LÓGICA Y ASIGNACIÓN DE PUERTOS", h1_style))
        elements.append(Paragraph(
            "La red lógica modelada en Cisco Packet Tracer interconecta los 5 switches y 15 computadores en el esquema siguiente:", body_style))

        # Tabla de Direccionamiento
        table_data = [
            ["Piso", "Switch", "Nombre PC", "Puerto", "VLAN ID", "VLAN", "IP", "Máscara", "Gateway"],
        ]
        for f in self.floors:
            for pc in f["pcs"]:
                table_data.append([
                    f"Piso {f['floor_num']}",
                    f["sw_name"],
                    pc["name"],
                    pc["port"],
                    f"VLAN {pc['vlan']}",
                    [v["name"] for v in self.vlans if v["id"] == str(pc["vlan"])][0],
                    pc["ip"],
                    "255.255.255.0",
                    pc["gw"],
                ])

        t = Table(table_data, colWidths=[38, 56, 75, 70, 44, 55, 66, 68, 66])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A2540")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.5),
            ("LEADING", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 8))

        # Sección 3
        elements.append(Paragraph("3. REQUERIMIENTO 3: SCRIPT DE CONFIGURACIÓN CISCO IOS", h1_style))
        sample_code = (
            "enable\n"
            "configure terminal\n"
            "hostname SW-PISO-[X]\n"
            "vlan 10 \\n name VENTAS \\n vlan 20 \\n name CONTRATOS \\n vlan 30 \\n name JURIDICA\n"
            "vlan 40 \\n name DIRECTORES \\n vlan 50 \\n name RRHH \\n vlan 99 \\n name NATIVA \\n vlan 666 \\n name BLACKHOLE\n"
            "exit\n"
            "interface range FastEthernet0/1 - 8   \\n switchport mode access \\n switchport access vlan 10 \\n no shutdown\n"
            "interface range FastEthernet0/9 - 16  \\n switchport mode access \\n switchport access vlan 20 \\n no shutdown\n"
            "interface range FastEthernet0/17 - 24 \\n switchport mode access \\n switchport access vlan 30 \\n no shutdown\n"
            "interface range FastEthernet0/25 - 32 \\n switchport mode access \\n switchport access vlan 40 \\n no shutdown\n"
            "interface range FastEthernet0/33 - 40 \\n switchport mode access \\n switchport access vlan 50 \\n no shutdown\n"
            "interface range FastEthernet0/41 - 48 \\n switchport mode access \\n switchport access vlan 666 \\n shutdown\n"
            "interface range GigabitEthernet0/1 - 2 \\n switchport mode trunk \\n switchport trunk native vlan 99 \\n no shutdown\n"
            "interface Vlan1 \\n no ip address \\n shutdown \\n exit \\n end \\n copy running-config startup-config"
        )
        elements.append(Paragraph(sample_code.replace("\\n", "<br/>"), code_style))

        elements.append(PageBreak())

        # Sección 4: Preguntas Teóricas
        elements.append(Paragraph("4. NUMERAL 6: RESPUESTAS DE CONTEXTO Y ANÁLISIS TEÓRICO", h1_style))

        elements.append(Paragraph("Pregunta 1: Aislamiento en Capa 2 (Broadcast ARP)", h2_style))
        elements.append(Paragraph(
            "<b>Respuesta:</b> La trama broadcast ARP (destino FF:FF:FF:FF:FF:FF) será recibida <b>únicamente</b> por "
            "los dispositivos en la <b>VLAN 10</b> (PC-Ventas-P2 en Piso 2 y PC-Ventas-P4 en Piso 4). Los usuarios de "
            "CONTRATOS en el mismo piso están asignados al puerto Fa0/9 (VLAN 20). Los switches de Capa 2 segmentan "
            "estrictamente los dominios de difusión: las tramas de la VLAN 10 viajan con tag 802.1Q a través de los troncales "
            "y jamás son replicadas hacia interfaces asociadas a otras VLANs.", body_style))

        elements.append(Paragraph("Pregunta 2: Retiro de VLAN 1 y Ataques de VLAN Hopping", h2_style))
        elements.append(Paragraph(
            "<b>Respuesta:</b> Por defecto, la VLAN 1 es la VLAN administrativa y nativa de fábrica. Retirarla previene dos ataques críticos:<br/>"
            "1. <b>Switch Spoofing:</b> Un atacante negocia enlaces troncales falsos mediante el protocolo DTP.<br/>"
            "2. <b>Double Tagging (Doble Etiquetado):</b> El atacante inyecta dos etiquetas 802.1Q; al retirar el switch la etiqueta exterior "
            "por coincidir con la VLAN nativa, el segundo switch entrega la trama a la VLAN víctima. Al aislar la VLAN nativa en la VLAN 99 "
            "(sin dispositivos) y apagar los puertos no usados en la VLAN 666 (Blackhole), este vector queda totalmente bloqueado.", body_style))

        elements.append(Paragraph("Pregunta 3: Ventajas de la Distribución por Grupos de Puertos", h2_style))
        elements.append(Paragraph(
            "<b>Respuesta:</b> Aporta estandarización modular en los 5 pisos. Facilita la configuración masiva mediante "
            "<code>interface range</code>, reduce en un 90% el error humano de asignación, simplifica las auditorías visuales en el Patch Panel "
            "y garantiza que cualquier puerto no autorizado en el rango Fa0/41-48 quede desactivado de inmediato.", body_style))

        elements.append(Paragraph("Pregunta 4: Ausencia de Enrutamiento Inter-VLAN", h2_style))
        elements.append(Paragraph(
            "<b>Respuesta:</b> PC-Juridica-P2 (192.168.30.11) y PC-Directores-P2 (192.168.40.11) están en diferentes subredes y diferentes VLANs. "
            "Al determinar que el destino es remoto, el emisor intenta enviar el paquete a su Gateway. Como en la topología solo hay switches de Capa 2 "
            "(sin Router ni Switch Layer 3 con interfaces SVI), no hay quién conmute los paquetes entre subredes. Por ende, el ping falla con "
            "<i>Destination host unreachable</i> o <i>Request timed out</i>.", body_style))

        elements.append(Spacer(1, 8))

        # Sección 5: Matriz de Validación
        elements.append(Paragraph("5. NUMERAL 7: MATRIZ DE PRUEBAS DE CONECTIVIDAD", h1_style))
        matriz_data = [
            ["Origen", "Destino", "Comando", "Resultado", "Justificación Técnica"],
            ["PC-Ventas-P1\n(192.168.10.11)", "PC-Ventas-P4\n(192.168.10.13)", "ping 192.168.10.13", "EXITOSO\n(0% loss)", "Misma VLAN 10 y subred. Conmutación 802.1Q transparente."],
            ["PC-Juridica-P2\n(192.168.30.11)", "PC-Juridica-P5\n(192.168.30.13)", "ping 192.168.30.13", "EXITOSO\n(0% loss)", "Misma VLAN 30 y subred. Tráfico permitido entre pisos 2 y 5."],
            ["PC-Ventas-P1\n(192.168.10.11)", "PC-Contratos-P1\n(192.168.20.11)", "ping 192.168.20.11", "FALLIDO\n(Timed out)", "Diferentes VLANs (10 vs 20). Aislamiento estricto de Capa 2."],
            ["PC-RRHH-P3\n(192.168.50.12)", "PC-Directores-P4\n(192.168.40.12)", "ping 192.168.40.12", "FALLIDO\n(Timed out)", "Diferentes VLANs (50 vs 40). Sin enrutamiento inter-VLAN."],
        ]
        tm = Table(matriz_data, colWidths=[90, 90, 85, 65, 210])
        tm.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A2540")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("LEADING", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (3, -1), "CENTER"),
            ("ALIGN", (4, 1), (4, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(tm)

        doc.build(elements)
        return output_pdf_path

    def solve_lab(self, output_dir: str) -> Dict[str, str]:
        """
        Ejecuta la solución integral del taller:
        1. Compila KRONOS_TELEMATICA_VLANS.pkt
        2. Actualiza trabajo telematica.pkt
        3. Genera SOLUCION_GUIA1_TELEMATICA.md
        4. Genera SOLUCION_GUIA1_TELEMATICA.pdf
        """
        os.makedirs(output_dir, exist_ok=True)
        pkt_official = os.path.join(output_dir, "KRONOS_TELEMATICA_VLANS.pkt")
        pkt_mirror = os.path.join(output_dir, "trabajo telematica.pkt")
        md_file = os.path.join(output_dir, "SOLUCION_GUIA1_TELEMATICA.md")
        pdf_file = os.path.join(output_dir, "SOLUCION_GUIA1_TELEMATICA.pdf")

        # 1. Generar PKT oficial
        self.generate_pkt_file(pkt_official)

        # 2. Copiar a trabajo telematica.pkt para que el usuario tenga su archivo principal al día
        with open(pkt_official, "rb") as fin, open(pkt_mirror, "wb") as fout:
            fout.write(fin.read())

        # 3. Generar Markdown
        self.generate_solution_markdown(md_file)

        # 4. Generar PDF
        self.generate_solution_pdf(pdf_file)

        return {
            "official_pkt": pkt_official,
            "mirror_pkt": pkt_mirror,
            "markdown": md_file,
            "pdf": pdf_file,
        }
