"""
Extrai notas explicativas (comentários) de um modelo oficial de Aviso em .docx.
Usado quando a AGU/SEGES publica nova versão do modelo.
"""

from __future__ import annotations
import zipfile
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Tuple
from lxml import etree
from io import BytesIO


NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def extract_comments_from_docx(file_bytes: bytes) -> Dict[int, str]:
    """
    Recebe o conteúdo binário de um .docx e retorna {id: texto da nota}.
    """
    comments: Dict[int, str] = {}

    with tempfile.TemporaryDirectory() as tmp:
        docx_path = Path(tmp) / "modelo.docx"
        docx_path.write_bytes(file_bytes)

        with zipfile.ZipFile(docx_path, "r") as z:
            # comments.xml pode não existir
            if "word/comments.xml" not in z.namelist():
                return {}

            with z.open("word/comments.xml") as f:
                tree = etree.parse(f)

        for c in tree.findall(".//w:comment", NSMAP):
            cid = c.get(f"{{{NSMAP['w']}}}id")
            if cid is None:
                continue
            texts = [t.text or "" for t in c.findall(".//w:t", NSMAP)]
            full = "".join(texts).strip()
            # limpa espaços múltiplos
            while "  " in full:
                full = full.replace("  ", " ")
            comments[int(cid)] = full

    return comments


def clean_note_text(text: str) -> str:
    """Remove prefixos comuns de 'Nota explicativa:'."""
    prefixes = [
        "Nota explicativa:",
        "Nota  explicativa :",
        "Nota   explicativa :",
        "Nota explicativa :",
        "ORIENTAÇÕES PARA USO DO MODELO – LEITURA OBRIGATÓRIA",
    ]
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].strip()
            break
    return text


def map_comments_to_keys(raw_comments: Dict[int, str]) -> Dict[str, str]:
    """
    Mapeia IDs de comentários para chaves legíveis usadas no app.
    Mantém fallback genérico para IDs desconhecidos (versões futuras).
    """
    # Mapeamento conhecido da versão atual do modelo
    known = {
        0: "orientacoes_gerais",
        1: "horario_fase_lances",
        2: "preambulo_hipotese",
        7: "registro_de_precos",
        10: "exclusividade_me_epp",
        11: "cooperativas_servicos",
        16: "vedacao_consorcio",
        17: "quantitativo_inferior",
        19: "precos_diferentes_local",
        23: "parametrizacao_lance_minimo",
        24: "negociacao_preco",
        25: "planilha_custos",
        26: "consulta_cadastros",
        27: "margem_preferencia",
        28: "desclassificacao_proposta",
        33: "inexequibilidade",
        34: "obras_engenharia_aceitabilidade",
        35: "ajuste_planilha",
        36: "habilitacao_sicaf",
        37: "documentos_complementares",
        38: "consorcio_habilitacao",
        41: "prazo_assinatura_arp",
        42: "habilitacao_cumulativa_itens",
        45: "renovacao_quantitativo_arp",
        52: "verificacao_contrato_assinado",
        53: "termo_contrato_facultativo",
        54: "nota_empenho_substituto",
        55: "manutencao_habilitacao",
        64: "percentual_multa",
    }

    result: Dict[str, str] = {}
    for cid, text in sorted(raw_comments.items()):
        key = known.get(cid, f"nota_{cid}")
        result[key] = clean_note_text(text)

    return result


def extract_and_map(file_bytes: bytes) -> Tuple[Dict[str, str], Dict[int, str]]:
    """
    Retorna (notas_mapeadas, notas_brutas_por_id).
    """
    raw = extract_comments_from_docx(file_bytes)
    mapped = map_comments_to_keys(raw)
    return mapped, raw
