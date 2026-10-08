"""
JARVIS Packet Tracer Cryptographic Pipeline
Implementa descifrado y cifrado bidireccional para archivos .pkt de Cisco Packet Tracer.
"""
import zlib
import struct
from typing import Union
from .decipher.eax import EAX
from .decipher.twofish import Twofish


def deobf_stage1(data: bytes) -> bytes:
    L = len(data)
    return bytes(data[L - 1 - i] ^ (L - i * L & 0xFF) for i in range(L))


def deobf_stage2(data: bytes) -> bytes:
    L = len(data)
    return bytes(b ^ (L - i & 0xFF) for i, b in enumerate(data))


def uncompress_qt(blob: bytes) -> bytes:
    size = struct.unpack(">I", blob[:4])[0]
    return zlib.decompress(blob[4:])[:size]


def compress_qt(xml_data: bytes) -> bytes:
    size = len(xml_data)
    header = struct.pack(">I", size)
    compressed = zlib.compress(xml_data)
    return header + compressed


def obf_stage2(data: bytes) -> bytes:
    L = len(data)
    return bytes(b ^ (L - i & 0xFF) for i, b in enumerate(data))


def obf_stage1(data: bytes) -> bytes:
    L = len(data)
    output = bytearray(L)
    for i in range(L):
        key_byte = (L - i * L) & 0xFF
        val = data[i] ^ key_byte
        output[L - 1 - i] = val
    return bytes(output)


def decrypt_pkt(pkt_data: bytes) -> bytes:
    """Descifra el binario .pkt y devuelve los bytes XML originales."""
    stage1 = deobf_stage1(pkt_data)
    key = bytes([137]) * 16
    iv = bytes([16]) * 16

    tf = Twofish(key)
    eax = EAX(tf.encrypt)

    ciphertext = stage1[:-16]
    tag = stage1[-16:]

    decrypted = eax.decrypt(nonce=iv, ciphertext=ciphertext, tag=tag)
    stage2 = deobf_stage2(decrypted)
    xml = uncompress_qt(stage2)
    return xml


def encrypt_xml(xml_data: bytes) -> bytes:
    """Cifra los bytes XML y devuelve el binario empaquetado .pkt para Packet Tracer."""
    stage2_input = compress_qt(xml_data)
    decrypted_blob = obf_stage2(stage2_input)

    key = bytes([137]) * 16
    iv = bytes([16]) * 16

    tf = Twofish(key)
    eax = EAX(tf.encrypt)
    ciphertext, tag = eax.encrypt(nonce=iv, plaintext=decrypted_blob)

    stage1_input = ciphertext + tag
    final_pkt_data = obf_stage1(stage1_input)
    return final_pkt_data


def decrypt_file(input_pkt: str, output_xml: str) -> None:
    with open(input_pkt, "rb") as f:
        data = f.read()
    xml_data = decrypt_pkt(data)
    with open(output_xml, "wb") as f:
        f.write(xml_data)


def encrypt_file(input_xml: str, output_pkt: str) -> None:
    with open(input_xml, "rb") as f:
        data = f.read()
    pkt_data = encrypt_xml(data)
    with open(output_pkt, "wb") as f:
        f.write(pkt_data)
