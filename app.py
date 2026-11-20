"""
Aviso de Contratação Direta (Dispensa Eletrônica) - Gerador Guiado
Modelo baseado na Lei 14.133/2021 + IN SEGES/ME 67/2021

Recursos:
- Formulário guiado com notas explicativas
- Exportar / Importar preenchimento em JSON
- Upload de novo modelo oficial → atualiza notas automaticamente
"""

import streamlit as st
import json
from datetime import datetime, date
from io import BytesIO
from generator import generate_aviso
from notes import NOTES as DEFAULT_NOTES
from model_parser import extract_and_map

st.set_page_config(
    page_title="Gerador de Aviso de Contratação Direta",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== CSS ==========
st.markdown("""
<style>
    .stExpander { border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; }
    .note-box {
        background-color: #f0f7ff; border-left: 4px solid #1e88e5;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 6px 6px 0; font-size: 0.9rem;
    }
    .warning-box {
        background-color: #fff8e1; border-left: 4px solid #ffb300;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 6px 6px 0;
    }
    h1, h2, h3 { color: #1a237e; }
</style>
""", unsafe_allow_html=True)


# ========== Notas (permite override via upload) ==========
def get_notes() -> dict:
    if "custom_notes" in st.session_state and st.session_state.custom_notes:
        return st.session_state.custom_notes
    return DEFAULT_NOTES


def show_note(key: str, title: str = "Nota explicativa"):
    notes = get_notes()
    if key in notes:
        with st.expander(f"ℹ️ {title}", expanded=False):
            st.markdown(f'<div class="note-box">{notes[key]}</div>', unsafe_allow_html=True)


# ========== Session defaults ==========
def init_session():
    defaults = {
        "numero_aviso": "",
        "numero_processo": "",
        "orgao": "Instituto Federal de Educação, Ciência e Tecnologia do Maranhão - IFMA",
        "setor": "Coordenação de Licitações e Contratos",
        "endereco": "Av. Colares Moreira, 77 – Renascença, São Luís – MA",
        "uasg": "",
        "objeto_resumo": "",
        "objeto_completo": "",
        "valor_total": "",
        "data_sessao": date.today(),
        "horario_lances": "Das 08h às 14h",
        "criterio_julgamento": "menor preço",
        "forma_julgamento": "por item",
        "inciso_art75": "II",
        "registro_precos": False,
        "tratamento_me_epp": True,
        "exclusividade_me_epp": False,
        "itens_exclusivos_me": "",
        "margem_preferencia": False,
        "multiplos_itens": True,
        "vedar_consorcio": True,
        "vedar_oscip": True,
        "vedar_cooperativas": False,
        "vedar_pessoas_fisicas": True,
        "permitir_quantitativo_inferior": False,
        "precos_diferentes_local": False,
        "prazo_validade_proposta": 60,
        "prazo_docs_habilitacao": 2,
        "prazo_assinatura_arp": 5,
        "prazo_assinatura_contrato": 5,
        "prazo_recolhimento_multa": 15,
        "intervalo_minimo_lances": "R$ 0,01 (um centavo)",
        "percentual_multa": "10",
        "exigir_planilha_custos": False,
        "renovar_quantitativo_arp": False,
        "local": "São Luís - MA",
        "autoridade": "",
        "cargo_autoridade": "Ordenador de Despesas",
        "custom_notes": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ========== Helpers JSON ==========
FORM_KEYS = [
    "numero_aviso", "numero_processo", "orgao", "setor", "endereco", "uasg",
    "objeto_resumo", "objeto_completo", "valor_total", "data_sessao", "horario_lances",
    "criterio_julgamento", "forma_julgamento", "inciso_art75", "registro_precos",
    "tratamento_me_epp", "exclusividade_me_epp", "itens_exclusivos_me", "margem_preferencia",
    "multiplos_itens", "vedar_consorcio", "vedar_oscip", "vedar_cooperativas",
    "vedar_pessoas_fisicas", "permitir_quantitativo_inferior", "precos_diferentes_local",
    "prazo_validade_proposta", "prazo_docs_habilitacao", "prazo_assinatura_arp",
    "prazo_assinatura_contrato", "prazo_recolhimento_multa", "intervalo_minimo_lances",
    "percentual_multa", "exigir_planilha_custos", "renovar_quantitativo_arp",
    "local", "autoridade", "cargo_autoridade",
]


def export_to_json() -> str:
    data = {}
    for k in FORM_KEYS:
        val = st.session_state.get(k)
        if isinstance(val, date):
            val = val.isoformat()
        data[k] = val
    data["_exported_at"] = datetime.now().isoformat()
    data["_version"] = "1.0"
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_from_json(content: str) -> list:
    """Retorna lista de avisos/erros."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return [f"JSON inválido: {e}"]

    applied = []
    for k in FORM_KEYS:
        if k not in data:
            continue
        val = data[k]
        if k == "data_sessao" and isinstance(val, str):
            try:
                val = date.fromisoformat(val)
            except ValueError:
                continue
        st.session_state[k] = val
        applied.append(k)
    return applied


def numero_por_extenso(n: int) -> str:
    mapa = {
        1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco",
        6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez",
        15: "quinze", 30: "trinta", 60: "sessenta", 90: "noventa",
        120: "cento e vinte", 180: "cento e oitenta",
    }
    return mapa.get(n, str(n))


# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📋 Aviso de Dispensa")
    st.caption("Lei 14.133/2021 • IN 67/2021")
    st.markdown("---")

    page = st.radio(
        "Navegação",
        [
            "1. Orientações",
            "2. Dados Gerais",
            "3. Objeto e Critérios",
            "4. Participação",
            "5. Prazos e Lances",
            "6. Habilitação e Sanções",
            "7. Gerar Documento",
            "8. Importar / Exportar JSON",
            "9. Atualizar Modelo Oficial",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.session_state.get("custom_notes"):
        st.success("Notas personalizadas ativas (modelo atualizado)")
    else:
        st.caption("Usando notas do modelo padrão")


# ========== PÁGINAS ==========

if page == "1. Orientações":
    st.header("Orientações para uso do modelo")
    notes = get_notes()
    if "orientacoes_gerais" in notes:
        st.markdown(f'<div class="note-box">{notes["orientacoes_gerais"]}</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Como usar este gerador

    1. Navegue pelas seções no menu lateral.
    2. Preencha os campos. Campos com ℹ️ possuem **nota explicativa**.
    3. Campos condicionais aparecem conforme suas escolhas.
    4. Use a seção **Importar / Exportar JSON** para salvar o preenchimento.
    5. Quando a AGU/SEGES publicar novo modelo, use a seção **Atualizar Modelo Oficial**.
    """)

elif page == "2. Dados Gerais":
    st.header("2. Dados Gerais do Aviso")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.numero_aviso = st.text_input("Número do Aviso *", value=st.session_state.numero_aviso, placeholder="Ex: 001/2026")
        st.session_state.numero_processo = st.text_input("Número do Processo Administrativo *", value=st.session_state.numero_processo, placeholder="Ex: 23249.001234/2026-00")
        st.session_state.uasg = st.text_input("UASG (Código) *", value=st.session_state.uasg, placeholder="Ex: 158123")
    with col2:
        st.session_state.orgao = st.text_input("Órgão / Entidade *", value=st.session_state.orgao)
        st.session_state.setor = st.text_input("Setor responsável *", value=st.session_state.setor)
        st.session_state.endereco = st.text_input("Endereço *", value=st.session_state.endereco)

    st.subheader("Hipótese de Dispensa")
    show_note("preambulo_hipotese", "Ajuste do preâmbulo")
    st.session_state.inciso_art75 = st.selectbox(
        "Inciso do art. 75 da Lei 14.133/2021 *",
        options=["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"],
        index=["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"].index(st.session_state.inciso_art75) if st.session_state.inciso_art75 in ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI"] else 1,
    )

    st.subheader("Local e Autoridade")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.local = st.text_input("Local de emissão", value=st.session_state.local)
        st.session_state.autoridade = st.text_input("Nome da autoridade competente *", value=st.session_state.autoridade)
    with col2:
        st.session_state.cargo_autoridade = st.text_input("Cargo da autoridade", value=st.session_state.cargo_autoridade)

elif page == "3. Objeto e Critérios":
    st.header("3. Objeto e Critérios de Julgamento")

    st.session_state.objeto_resumo = st.text_input("Objeto (resumo para capa) *", value=st.session_state.objeto_resumo, placeholder="Ex: Aquisição de material de expediente")
    st.session_state.objeto_completo = st.text_area("Objeto completo (cláusula 1.1) *", value=st.session_state.objeto_completo, height=100)
    st.session_state.valor_total = st.text_input("Valor total estimado da contratação *", value=st.session_state.valor_total, placeholder="Ex: 45.000,00")

    st.subheader("Registro de Preços")
    show_note("registro_de_precos")
    st.session_state.registro_precos = st.checkbox("Esta dispensa é para Registro de Preços (SRP)", value=st.session_state.registro_precos)
    if st.session_state.registro_precos:
        show_note("renovacao_quantitativo_arp", "Renovação de quantitativo na prorrogação da ARP")
        st.session_state.renovar_quantitativo_arp = st.checkbox("Permitir renovação do quantitativo original na prorrogação da ARP", value=st.session_state.renovar_quantitativo_arp)

    st.subheader("Critério de Julgamento")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.criterio_julgamento = st.selectbox("Critério *", ["menor preço", "maior desconto"], index=0 if st.session_state.criterio_julgamento == "menor preço" else 1)
    with col2:
        st.session_state.forma_julgamento = st.selectbox("Forma *", ["por item", "por grupo", "global"], index=["por item", "por grupo", "global"].index(st.session_state.forma_julgamento))

    st.session_state.multiplos_itens = st.checkbox("Há mais de um item (permite participação parcial)", value=st.session_state.multiplos_itens)

    st.subheader("Margem de Preferência")
    show_note("margem_preferencia")
    st.session_state.margem_preferencia = st.checkbox("Há margem de preferência para algum item", value=st.session_state.margem_preferencia)

    st.session_state.exigir_planilha_custos = st.checkbox("Exigir planilha de custos e formação de preços do vencedor", value=st.session_state.exigir_planilha_custos)
    show_note("planilha_custos")

elif page == "4. Participação":
    st.header("4. Regras de Participação")

    st.subheader("Tratamento ME/EPP")
    show_note("exclusividade_me_epp")
    st.session_state.tratamento_me_epp = st.checkbox("Aplicar tratamento favorecido a ME/EPP/Equiparadas", value=st.session_state.tratamento_me_epp)
    st.session_state.exclusividade_me_epp = st.checkbox("Há itens com participação exclusiva de ME/EPP", value=st.session_state.exclusividade_me_epp)
    if st.session_state.exclusividade_me_epp:
        st.session_state.itens_exclusivos_me = st.text_input("Itens exclusivos ME/EPP (ex: 01, 03 e 05)", value=st.session_state.itens_exclusivos_me)

    st.subheader("Vedações de participação")
    show_note("vedacao_consorcio")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.vedar_consorcio = st.checkbox("Vedar consórcio", value=st.session_state.vedar_consorcio)
        st.session_state.vedar_oscip = st.checkbox("Vedar OSCIP", value=st.session_state.vedar_oscip)
    with col2:
        st.session_state.vedar_cooperativas = st.checkbox("Vedar sociedades cooperativas", value=st.session_state.vedar_cooperativas)
        show_note("cooperativas_servicos", "Cooperativas em serviços com dedicação exclusiva")
        st.session_state.vedar_pessoas_fisicas = st.checkbox("Vedar pessoas físicas", value=st.session_state.vedar_pessoas_fisicas)

    st.subheader("Proposta")
    show_note("quantitativo_inferior")
    st.session_state.permitir_quantitativo_inferior = st.checkbox("Permitir proposta em quantitativo inferior ao máximo previsto", value=st.session_state.permitir_quantitativo_inferior)
    show_note("precos_diferentes_local")
    st.session_state.precos_diferentes_local = st.checkbox("Admitir preços diferentes por local de entrega / lote", value=st.session_state.precos_diferentes_local)

elif page == "5. Prazos e Lances":
    st.header("5. Datas, Horários e Prazos")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.data_sessao = st.date_input("Data da sessão pública *", value=st.session_state.data_sessao if isinstance(st.session_state.data_sessao, date) else date.today())
        show_note("horario_fase_lances")
        st.session_state.horario_lances = st.text_input("Horário da fase de lances *", value=st.session_state.horario_lances)
    with col2:
        st.session_state.intervalo_minimo_lances = st.text_input("Intervalo mínimo entre lances *", value=st.session_state.intervalo_minimo_lances)

    st.subheader("Prazos importantes")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.prazo_validade_proposta = st.number_input("Validade da proposta (dias)", min_value=30, max_value=180, value=int(st.session_state.prazo_validade_proposta))
    with col2:
        st.session_state.prazo_docs_habilitacao = st.number_input("Prazo docs complementares de habilitação (horas)", min_value=1, max_value=48, value=int(st.session_state.prazo_docs_habilitacao))
        show_note("documentos_complementares")
    with col3:
        st.session_state.prazo_assinatura_contrato = st.number_input("Prazo assinatura do contrato (dias úteis)", min_value=1, max_value=30, value=int(st.session_state.prazo_assinatura_contrato))

    if st.session_state.registro_precos:
        show_note("prazo_assinatura_arp")
        st.session_state.prazo_assinatura_arp = st.number_input("Prazo assinatura da Ata de Registro de Preços (dias)", min_value=1, max_value=15, value=int(st.session_state.prazo_assinatura_arp))

elif page == "6. Habilitação e Sanções":
    st.header("6. Habilitação e Sanções Administrativas")

    show_note("habilitacao_sicaf")
    show_note("manutencao_habilitacao", "Manutenção das condições de habilitação")
    show_note("habilitacao_cumulativa_itens", "Habilitação cumulativa em múltiplos itens")

    st.subheader("Multa")
    show_note("percentual_multa")
    st.session_state.percentual_multa = st.text_input("Percentual de multa (%) *", value=st.session_state.percentual_multa, help="Deve estar entre 0,5% e 30% (art. 156, § 3º).")
    st.session_state.prazo_recolhimento_multa = st.number_input("Prazo para recolhimento administrativo da multa (dias)", min_value=5, max_value=30, value=int(st.session_state.prazo_recolhimento_multa))

    st.subheader("Instrumento contratual")
    show_note("termo_contrato_facultativo")
    show_note("nota_empenho_substituto")
    show_note("verificacao_contrato_assinado")

elif page == "7. Gerar Documento":
    st.header("7. Revisar e Gerar o Aviso")

    erros = []
    if not st.session_state.numero_aviso: erros.append("Número do Aviso")
    if not st.session_state.numero_processo: erros.append("Número do Processo")
    if not st.session_state.objeto_resumo: erros.append("Objeto (resumo)")
    if not st.session_state.objeto_completo: erros.append("Objeto completo")
    if not st.session_state.valor_total: erros.append("Valor total estimado")
    if not st.session_state.uasg: erros.append("UASG")
    if not st.session_state.autoridade: erros.append("Nome da autoridade competente")

    if erros:
        st.error("Preencha os campos obrigatórios: " + ", ".join(erros))
    else:
        st.success("Campos obrigatórios preenchidos. Você pode gerar o documento.")

    with st.expander("Pré-visualização dos dados principais", expanded=True):
        st.markdown(f"""
        | Campo | Valor |
        |-------|-------|
        | **Aviso** | {st.session_state.numero_aviso} |
        | **Processo** | {st.session_state.numero_processo} |
        | **UASG** | {st.session_state.uasg} |
        | **Órgão** | {st.session_state.orgao} |
        | **Objeto** | {st.session_state.objeto_resumo} |
        | **Valor** | R$ {st.session_state.valor_total} |
        | **Data sessão** | {st.session_state.data_sessao} |
        | **Horário lances** | {st.session_state.horario_lances} |
        | **Critério** | {st.session_state.criterio_julgamento} {st.session_state.forma_julgamento} |
        | **Registro de Preços** | {"Sim" if st.session_state.registro_precos else "Não"} |
        | **Exclusividade ME/EPP** | {"Sim" if st.session_state.exclusividade_me_epp else "Não"} |
        | **Inciso art. 75** | {st.session_state.inciso_art75} |
        """)

    data = {
        "numero_aviso": st.session_state.numero_aviso,
        "numero_processo": st.session_state.numero_processo,
        "orgao": st.session_state.orgao,
        "setor": st.session_state.setor,
        "endereco": st.session_state.endereco,
        "uasg": st.session_state.uasg,
        "objeto_resumo": st.session_state.objeto_resumo,
        "objeto_completo": st.session_state.objeto_completo,
        "valor_total": st.session_state.valor_total,
        "data_sessao": st.session_state.data_sessao.strftime("%d/%m/%Y") if isinstance(st.session_state.data_sessao, date) else str(st.session_state.data_sessao),
        "horario_lances": st.session_state.horario_lances,
        "criterio_julgamento": st.session_state.criterio_julgamento,
        "forma_julgamento": st.session_state.forma_julgamento,
        "inciso_art75": st.session_state.inciso_art75,
        "registro_precos": st.session_state.registro_precos,
        "tratamento_me_epp": st.session_state.tratamento_me_epp,
        "exclusividade_me_epp": st.session_state.exclusividade_me_epp,
        "itens_exclusivos_me": st.session_state.itens_exclusivos_me,
        "margem_preferencia": st.session_state.margem_preferencia,
        "multiplos_itens": st.session_state.multiplos_itens,
        "vedar_consorcio": st.session_state.vedar_consorcio,
        "vedar_oscip": st.session_state.vedar_oscip,
        "vedar_cooperativas": st.session_state.vedar_cooperativas,
        "vedar_pessoas_fisicas": st.session_state.vedar_pessoas_fisicas,
        "permitir_quantitativo_inferior": st.session_state.permitir_quantitativo_inferior,
        "precos_diferentes_local": st.session_state.precos_diferentes_local,
        "prazo_validade_proposta": st.session_state.prazo_validade_proposta,
        "prazo_validade_proposta_extenso": numero_por_extenso(st.session_state.prazo_validade_proposta),
        "prazo_docs_habilitacao": st.session_state.prazo_docs_habilitacao,
        "prazo_docs_habilitacao_extenso": numero_por_extenso(st.session_state.prazo_docs_habilitacao),
        "prazo_assinatura_arp": st.session_state.prazo_assinatura_arp,
        "prazo_assinatura_arp_extenso": numero_por_extenso(st.session_state.prazo_assinatura_arp),
        "prazo_assinatura_contrato": st.session_state.prazo_assinatura_contrato,
        "prazo_assinatura_contrato_extenso": numero_por_extenso(st.session_state.prazo_assinatura_contrato),
        "prazo_recolhimento_multa": st.session_state.prazo_recolhimento_multa,
        "prazo_recolhimento_multa_extenso": numero_por_extenso(st.session_state.prazo_recolhimento_multa),
        "intervalo_minimo_lances": st.session_state.intervalo_minimo_lances,
        "percentual_multa": st.session_state.percentual_multa,
        "exigir_planilha_custos": st.session_state.exigir_planilha_custos,
        "renovar_quantitativo_arp": st.session_state.renovar_quantitativo_arp,
        "local": st.session_state.local,
        "data_documento": datetime.now().strftime("%d de %B de %Y")
            .replace("January", "janeiro").replace("February", "fevereiro").replace("March", "março")
            .replace("April", "abril").replace("May", "maio").replace("June", "junho")
            .replace("July", "julho").replace("August", "agosto").replace("September", "setembro")
            .replace("October", "outubro").replace("November", "novembro").replace("December", "dezembro"),
        "autoridade": st.session_state.autoridade,
        "cargo_autoridade": st.session_state.cargo_autoridade,
    }

    if st.button("📄 Gerar e baixar Aviso (.docx)", type="primary", disabled=bool(erros)):
        with st.spinner("Gerando documento..."):
            buffer = generate_aviso(data)
            nome_arquivo = f"Aviso_Dispensa_{st.session_state.numero_aviso.replace('/', '-')}.docx"
            st.download_button(
                label="⬇️ Clique para baixar o arquivo",
                data=buffer,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            st.success("Documento gerado com sucesso!")

    st.markdown("---")
    st.caption("Revise sempre o resultado final. Este gerador produz uma base alinhada ao modelo oficial.")

elif page == "8. Importar / Exportar JSON":
    st.header("8. Importar / Exportar preenchimento (JSON)")

    st.markdown("""
    Use esta seção para **salvar o preenchimento atual** ou **carregar um preenchimento anterior**.
    Útil para continuar de onde parou, compartilhar com colegas ou manter templates de processos recorrentes.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Exportar")
        json_str = export_to_json()
        st.download_button(
            label="⬇️ Baixar preenchimento (.json)",
            data=json_str.encode("utf-8"),
            file_name=f"aviso_preenchimento_{st.session_state.numero_aviso.replace('/', '-') or 'rascunho'}.json",
            mime="application/json",
            type="primary",
        )
        with st.expander("Ver JSON atual"):
            st.code(json_str, language="json")

    with col2:
        st.subheader("Importar")
        uploaded = st.file_uploader("Selecione um arquivo .json", type=["json"])
        if uploaded is not None:
            content = uploaded.read().decode("utf-8")
            if st.button("Carregar dados do JSON", type="primary"):
                applied = import_from_json(content)
                if applied and not any("inválido" in str(a).lower() for a in applied):
                    st.success(f"Dados carregados com sucesso ({len(applied)} campos).")
                    st.rerun()
                else:
                    st.error("Falha ao importar: " + str(applied))

elif page == "9. Atualizar Modelo Oficial":
    st.header("9. Atualizar notas a partir de novo modelo oficial")

    st.markdown("""
    Quando a **AGU/SEGES** publicar uma nova versão do modelo de Aviso de Contratação Direta, 
    faça o upload do arquivo `.docx` oficial aqui.

    O sistema irá:
    1. Extrair automaticamente todos os **comentários / notas explicativas**
    2. Atualizar as notas usadas neste formulário (nesta sessão)
    3. Permitir que você baixe o novo `notes.py` para versionar no GitHub

    > **Limitação atual**: a estrutura do formulário (campos) permanece a mesma. 
    > Apenas as notas explicativas são atualizadas. Mudanças estruturais grandes 
    > no modelo ainda exigem ajuste manual do código.
    """)

    uploaded_model = st.file_uploader(
        "Faça upload do novo modelo oficial (.docx)",
        type=["docx"],
        help="Arquivo baixado do site da SEGES/Compras.gov.br ou AGU",
    )

    if uploaded_model is not None:
        with st.spinner("Extraindo notas do modelo..."):
            try:
                file_bytes = uploaded_model.read()
                mapped, raw = extract_and_map(file_bytes)

                if not mapped:
                    st.warning("Nenhum comentário/nota encontrado neste arquivo. Verifique se é o modelo oficial com as notas embutidas.")
                else:
                    st.success(f"Extraídas **{len(mapped)}** notas explicativas.")

                    # Mostra preview
                    with st.expander("Pré-visualização das notas extraídas", expanded=True):
                        for key, text in sorted(mapped.items()):
                            st.markdown(f"**`{key}`**")
                            st.caption(text[:300] + ("..." if len(text) > 300 else ""))
                            st.markdown("---")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Aplicar estas notas nesta sessão", type="primary"):
                            st.session_state.custom_notes = mapped
                            st.success("Notas atualizadas para esta sessão!")
                            st.rerun()

                    with col_b:
                        # Gera um notes.py atualizado para download
                        lines = [
                            "# Notas explicativas atualizadas a partir de novo modelo oficial",
                            f"# Extraído em {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            "",
                            "NOTES = {",
                        ]
                        for k, v in mapped.items():
                            v_esc = v.replace("\\", "\\\\").replace('"""', r"\"\"\"")
                            lines.append(f'    "{k}": """{v_esc}""",')
                            lines.append("")
                        lines.append("}")
                        notes_py_content = "\n".join(lines)

                        st.download_button(
                            label="⬇️ Baixar notes.py atualizado",
                            data=notes_py_content.encode("utf-8"),
                            file_name="notes.py",
                            mime="text/x-python",
                        )

                    if st.button("↺ Voltar às notas padrão do sistema"):
                        st.session_state.custom_notes = None
                        st.rerun()

            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    st.markdown("---")
    st.info("""
    **Dica de fluxo recomendado quando sair nova versão do modelo:**
    1. Baixe o modelo oficial novo no site da SEGES/Compras.gov.br
    2. Faça upload aqui e clique em “Aplicar estas notas”
    3. Baixe o `notes.py` gerado e substitua no repositório GitHub
    4. Faça commit + push → o Streamlit Cloud atualiza automaticamente
    """)
