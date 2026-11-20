"""
Gera o Aviso de Contratação Direta (Dispensa Eletrônica) em .docx
a partir dos dados coletados no formulário Streamlit.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime
from io import BytesIO
from typing import Dict, Any


def set_run_font(run, font_name="Arial", size=12, bold=False, italic=False, color=None):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_heading_custom(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    if level == 0:
        set_run_font(run, size=16, bold=True)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif level == 1:
        set_run_font(run, size=14, bold=True)
    else:
        set_run_font(run, size=12, bold=True)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_para(doc, text, bold=False, italic=False, space_after=6, first_line_indent=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size=11, bold=bold, italic=italic)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if first_line_indent:
        p.paragraph_format.first_line_indent = Cm(first_line_indent)
    return p


def add_item(doc, number, text, bold_number=True):
    p = doc.add_paragraph()
    run_num = p.add_run(f"{number} ")
    set_run_font(run_num, size=11, bold=bold_number)
    run_txt = p.add_run(text)
    set_run_font(run_txt, size=11)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    return p


def generate_aviso(data: Dict[str, Any]) -> BytesIO:
    """
    Gera o documento completo a partir do dicionário de dados do formulário.
    Retorna um BytesIO pronto para download.
    """
    doc = Document()

    # Margens
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # ========== CABEÇALHO / CAPA ==========
    add_heading_custom(doc, "AVISO DE CONTRATAÇÃO DIRETA", level=0)
    add_heading_custom(doc, f"Nº {data.get('numero_aviso', 'XXX/AAAA')}", level=0)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Processo Administrativo nº {data.get('numero_processo', 'xxxxx.xxxxxx/xxxx-xx')}")
    set_run_font(run, size=11)

    doc.add_paragraph()

    # Dados principais em formato de ficha
    add_para(doc, f"CONTRATANTE/GERENCIADOR (UASG): {data.get('uasg', 'XXXX')}", bold=True)
    add_para(doc, f"OBJETO: {data.get('objeto_resumo', '[objeto]')}", bold=True)
    if data.get("registro_precos"):
        add_para(doc, "MODALIDADE: Dispensa Eletrônica para Registro de Preços", bold=True)
    else:
        add_para(doc, "MODALIDADE: Dispensa Eletrônica", bold=True)

    add_para(doc, f"VALOR TOTAL ESTIMADO DA CONTRATAÇÃO: R$ {data.get('valor_total', '00.000,00')}", bold=True)
    add_para(doc, f"DATA DA SESSÃO PÚBLICA: {data.get('data_sessao', 'XX/XX/202X')}", bold=True)
    add_para(doc, f"HORÁRIO DA FASE DE LANCES: {data.get('horario_lances', 'Das xxh até xxh')}", bold=True)

    criterio = data.get("criterio_julgamento", "menor preço")
    forma = data.get("forma_julgamento", "por item")
    add_para(doc, f"CRITÉRIO DE JULGAMENTO: {criterio} {forma}", bold=True)

    tratamento_me = "SIM" if data.get("tratamento_me_epp") else "NÃO"
    add_para(doc, f"TRATAMENTO FAVORECIDO ME/EPP/EQUIPARADAS: {tratamento_me}", bold=True)

    margem = "SIM" if data.get("margem_preferencia") else "NÃO"
    add_para(doc, f"MARGEM DE PREFERÊNCIA PARA ALGUM ITEM: {margem}", bold=True)

    doc.add_paragraph()

    # ========== PREÂMBULO ==========
    orgao = data.get("orgao", "[órgão ou entidade pública]")
    setor = data.get("setor", "[setor responsável pelas contratações]")
    endereco = data.get("endereco", "[endereço]")
    inciso = data.get("inciso_art75", "II")
    criterio_txt = data.get("criterio_julgamento", "menor preço")

    preambulo = (
        f"Torna-se público que o(a) {orgao}, por meio do(a) {setor}, "
        f"sediado(a) {endereco}, realizará Dispensa Eletrônica"
    )
    if data.get("registro_precos"):
        preambulo += ", para registro de preços,"
    preambulo += (
        f" com critério de julgamento {criterio_txt}, na hipótese do art. 75, "
        f"inciso {inciso}, nos termos da Lei nº 14.133, de 1º de abril de 2021, "
        f"da Instrução Normativa SEGES/ME nº 67, de 8 de julho de 2021, "
        f"do Decreto nº 11.462, de 31 de março de 2023, e demais normas aplicáveis."
    )
    add_para(doc, preambulo, space_after=12)

    # ========== 1. DO OBJETO ==========
    add_heading_custom(doc, "1. DO OBJETO", level=1)
    add_item(doc, "1.1.", f"O objeto do presente procedimento é a escolha da proposta mais vantajosa para a contratação, por dispensa de licitação, de {data.get('objeto_completo', '[objeto]')}, conforme condições, quantidades e exigências estabelecidas neste Aviso de Contratação Direta e seus anexos.")
    if data.get("multiplos_itens"):
        add_item(doc, "1.1.1.", "Havendo mais de um item, faculta-se ao fornecedor a participação em quantos forem de seu interesse.")
    add_item(doc, "1.2.", f"O critério de julgamento adotado será o {criterio_txt}, observadas as exigências contidas neste Aviso de Contratação Direta e seus Anexos quanto às especificações do objeto.")

    # ========== 2. DO REGISTRO DE PREÇOS ==========
    if data.get("registro_precos"):
        add_heading_custom(doc, "2. DO REGISTRO DE PREÇOS", level=1)
        add_item(doc, "2.1.", "As regras referentes aos órgãos gerenciador e participantes, bem como a eventuais adesões são as que constam da minuta de Ata de Registro de Preços.")

    # ========== 3. DA PARTICIPAÇÃO ==========
    add_heading_custom(doc, "3. DA PARTICIPAÇÃO NA DISPENSA ELETRÔNICA", level=1)
    add_item(doc, "3.1.", "A participação na presente dispensa eletrônica ocorrerá por meio do Sistema de Dispensa Eletrônica, ferramenta informatizada integrante do Sistema de Compras do Governo Federal – Compras.gov.br, disponível no Portal de Compras do Governo Federal, no endereço eletrônico www.gov.br/compras.")
    add_item(doc, "3.1.1.", "O procedimento será divulgado no Compras.gov.br e no Portal Nacional de Contratações Públicas - PNCP, e encaminhado automaticamente aos fornecedores registrados no Sistema de Cadastramento Unificado de Fornecedores - Sicaf, por mensagem eletrônica, na correspondente linha de fornecimento que pretende atender.")
    add_item(doc, "3.1.2.", "O Compras.gov.br poderá ser acessado pela web ou pelo aplicativo Compras.gov.br.")
    add_item(doc, "3.1.3.", "O fornecedor é o responsável por qualquer transação efetuada diretamente ou por seu representante no Sistema de Dispensa Eletrônica, não cabendo ao provedor do Sistema ou ao órgão entidade promotor do procedimento a responsabilidade por eventuais danos decorrentes de uso indevido da senha, ainda que por terceiros não autorizados.")

    if data.get("exclusividade_me_epp") and data.get("itens_exclusivos_me"):
        itens = data.get("itens_exclusivos_me", "XX, XX e XX")
        add_item(doc, "3.2.", f"Para os itens {itens}, a participação é exclusiva a microempresas e empresas de pequeno porte, nos termos do art. 49, inciso IV, c/c o art. 48, inciso I, da Lei Complementar nº 123, de 14 de dezembro de 2006.")
        add_item(doc, "3.2.1.", "A obtenção do benefício a que se refere o item anterior fica limitada às microempresas e às empresas de pequeno porte que, no ano-calendário de realização do procedimento, ainda não tenham celebrado contratos com a Administração Pública cujos valores somados extrapolem a receita bruta máxima admitida para fins de enquadramento como empresa de pequeno porte.")
        add_item(doc, "3.2.2.", "Será concedido tratamento favorecido para as microempresas e empresas de pequeno porte, para as sociedades cooperativas mencionadas no art. 16 da Lei nº 14.133, de 2021, para o agricultor familiar, o produtor rural pessoa física e para o microempreendedor individual - MEI, nos limites previstos da Lei Complementar nº 123, de 2006, e do Decreto n.º 8.538, de 6 de outubro de 2015.")

    add_item(doc, "3.3.", "Não poderão participar desta dispensa de licitação:")
    vedacoes = [
        ("3.3.1.", "aquele que não atenda às condições deste Aviso de Contratação Direta e seu(s) anexo(s);"),
        ("3.3.2.", "sociedade que desempenhe atividade incompatível com o objeto da dispensa;"),
        ("3.3.3.", "empresas estrangeiras que não tenham representação legal no Brasil com poderes expressos para receber citação e responder administrativa ou judicialmente;"),
        ("3.3.4.", "autor do anteprojeto, do projeto básico ou do projeto executivo, pessoa física ou jurídica, quando a contratação versar sobre obra, serviços ou fornecimento de bens a ele relacionados;"),
        ("3.3.5.", "empresa, isoladamente ou em consórcio, responsável pela elaboração do projeto básico ou do projeto executivo, ou empresa da qual o autor do projeto seja dirigente, gerente, controlador, acionista ou detentor de mais de 5% (cinco por cento) do capital com direito a voto, responsável técnico ou subcontratado, quando a contratação versar sobre obra, serviços ou fornecimento de bens a ela necessários;"),
        ("3.3.6.", "pessoa física ou jurídica que se encontre, ao tempo da contratação, impossibilitada de contratar em decorrência de sanção que lhe foi imposta;"),
        ("3.3.7.", "aquele que mantenha vínculo de natureza técnica, comercial, econômica, financeira, trabalhista ou civil com dirigente do órgão ou entidade contratante ou com agente público que desempenhe função na dispensa de licitação ou atue na fiscalização ou na gestão do contrato, ou que deles seja cônjuge, companheiro ou parente em linha reta, colateral ou por afinidade, até o terceiro grau;"),
        ("3.3.8.", "empresas controladoras, controladas ou coligadas, nos termos da Lei nº 6.404, de 15 de dezembro de 1976, concorrendo entre si;"),
        ("3.3.9.", "pessoa física ou jurídica que, nos 5 (cinco) anos anteriores à divulgação do aviso, tenha sido condenada judicialmente, com trânsito em julgado, por exploração de trabalho infantil, por submissão de trabalhadores a condições análogas às de escravo ou por contratação de adolescentes nos casos vedados pela legislação trabalhista;"),
    ]
    for num, txt in vedacoes:
        add_item(doc, num, txt)

    if data.get("vedar_consorcio"):
        add_item(doc, "3.3.10.", "pessoas jurídicas reunidas em consórcio;")
    if data.get("vedar_oscip"):
        add_item(doc, "3.3.11.", "Organização da Sociedade Civil de Interesse Público - OSCIP, atuando nessa condição;")
    if data.get("vedar_cooperativas"):
        add_item(doc, "3.3.12.", "sociedades cooperativas;")
    if data.get("vedar_pessoas_fisicas"):
        add_item(doc, "3.3.13.", "pessoas físicas.")

    add_item(doc, "3.4.", "Não poderá participar, direta ou indiretamente, da dispensa eletrônica ou da execução do contrato agente público do órgão ou entidade contratante, devendo ser observadas as situações que possam configurar conflito de interesses no exercício ou após o exercício do cargo ou emprego, nos termos da legislação que disciplina a matéria, conforme § 1º do art. 9º da Lei n.º 14.133, de 2021.")
    add_item(doc, "3.5.", "O impedimento de que trata o item 3.3.6 aplica-se também ao fornecedor que atue em substituição a outra pessoa, física ou jurídica, com o intuito de burlar a efetividade da sanção a ela aplicada, inclusive a sua controladora, controlada ou coligada, desde que devidamente comprovado o ilícito ou a utilização fraudulenta da personalidade jurídica do fornecedor.")

    # ========== 4. INGRESSO E PROPOSTA ==========
    add_heading_custom(doc, "4. DO INGRESSO NA DISPENSA ELETRÔNICA E DO CADASTRAMENTO DA PROPOSTA INICIAL", level=1)
    add_item(doc, "4.1.", "O ingresso do fornecedor na disputa da dispensa eletrônica ocorrerá com o cadastramento de sua proposta inicial, na forma deste item.")
    add_item(doc, "4.2.", "O fornecedor interessado, após a divulgação do Aviso de Contratação Direta, encaminhará, exclusivamente por meio do Sistema de Dispensa Eletrônica, a proposta com a descrição do objeto ofertado, a marca do produto, quando for o caso, e o preço ou o desconto, até a data e o horário estabelecidos para abertura do procedimento.")

    if data.get("permitir_quantitativo_inferior"):
        add_item(doc, "4.2.1.", "O fornecedor poderá oferecer proposta em quantitativo inferior ao máximo previsto para contratação.")
    else:
        add_item(doc, "4.2.1.", "O fornecedor NÃO poderá oferecer proposta em quantitativo inferior ao máximo previsto para contratação.")

    if data.get("precos_diferentes_local"):
        add_item(doc, "4.2.2.", "Será admitida a previsão de preços diferentes, conforme os critérios abaixo:")
        for i, criterio_local in enumerate(data.get("criterios_preco_local", ["[...]"]), 1):
            add_item(doc, f"4.2.2.{i}.", criterio_local)
    else:
        add_item(doc, "4.2.2.", "Não será admitida a previsão de preços diferentes em razão de local de entrega ou de acondicionamento, tamanho de lote ou qualquer outro motivo.")

    add_item(doc, "4.3.", "Todas as especificações do objeto contidas na proposta, em especial o preço ou o desconto ofertado, vinculam a Contratada.")
    add_item(doc, "4.4.", "Nos valores propostos estarão inclusos todos os custos operacionais, encargos previdenciários, trabalhistas, tributários, comerciais e quaisquer outros que incidam direta ou indiretamente na execução do objeto.")
    add_item(doc, "4.4.1.", "A proposta deverá conter declaração de que compreende a integralidade dos custos para atendimento dos direitos trabalhistas assegurados na Constituição Federal, nas leis trabalhistas, nas normas infralegais, nas convenções coletivas de trabalho e nos termos de ajustamento de conduta vigentes na data de entrega das propostas.")
    add_item(doc, "4.4.2.", "Os preços ofertados, tanto na proposta inicial, quanto na etapa de lances, serão de exclusiva responsabilidade do fornecedor, não lhe assistindo o direito de pleitear qualquer alteração, sob alegação de erro, omissão ou qualquer outro pretexto.")
    add_item(doc, "4.5.", "Se o regime tributário da empresa implicar o recolhimento de tributos em percentuais variáveis, a cotação adequada será aquela correspondente à média dos efetivos recolhimentos da empresa nos últimos doze meses.")
    add_item(doc, "4.6.", "Independentemente do percentual do tributo que constar da planilha, no pagamento serão retidos na fonte os percentuais estabelecidos pela legislação vigente.")
    add_item(doc, "4.7.", "A apresentação das propostas implica obrigatoriedade do cumprimento das disposições nelas contidas, em conformidade com o que dispõe o Termo de Referência, assumindo o proponente o compromisso de executar os serviços nos seus termos, bem como de fornecer os materiais, equipamentos, ferramentas e utensílios necessários, em quantidades e qualidades adequadas à perfeita execução contratual, promovendo, quando requerido, sua substituição.")
    add_item(doc, "4.8.", f"O prazo de validade da proposta não será inferior a {data.get('prazo_validade_proposta', '60')} ({data.get('prazo_validade_proposta_extenso', 'sessenta')}) dias, a contar da data de sua apresentação.")

    # Declarações
    add_item(doc, "4.9.", "No cadastramento da proposta inicial, o fornecedor deverá, também, assinalar Termo de Aceitação, em campo próprio do sistema eletrônico, relativo às seguintes declarações:")
    declaracoes = [
        "que inexistem fatos impeditivos para sua habilitação no certame, ciente da obrigatoriedade de declarar ocorrências posteriores;",
        "que está ciente e concorda com as condições contidas no Aviso de Contratação Direta e seus anexos;",
        "que se responsabiliza pelas transações que forem efetuadas no sistema, assumindo-as como firmes e verdadeiras;",
        "que cumpre as exigências de reserva de cargos para pessoa com deficiência e para reabilitado da Previdência Social, previstas em lei e em outras normas específicas;",
        "que não emprega menor de 18 anos em trabalho noturno, perigoso ou insalubre e não emprega menor de 16 anos, salvo menor, a partir de 14 anos, na condição de aprendiz, nos termos do art. 7°, inciso XXXIII, da Constituição; e",
        "não possui empregados executando trabalho degradante ou forçado, observando o disposto nos incisos III e IV do art. 1º e no inciso III do art. 5º da Constituição Federal.",
    ]
    for i, d in enumerate(declaracoes, 1):
        add_item(doc, f"4.9.{i}.", d)

    add_item(doc, "4.10.", "O fornecedor organizado em cooperativa deverá declarar, ainda, em campo próprio do sistema eletrônico, que cumpre os requisitos estabelecidos no art. 16 da Lei nº 14.133, de 2021.")
    if data.get("margem_preferencia"):
        add_item(doc, "4.11.", "O fornecedor deverá declarar em campo próprio do sistema se o produto ou serviço ofertado é manufaturado nacional beneficiado por um dos critérios de margem de preferência indicados no Termo de Referência, quando for o caso, para usufruir do benefício.")
    add_item(doc, "4.12.", "O fornecedor enquadrado como microempresa, empresa de pequeno porte ou sociedade cooperativa deverá declarar, ainda, em campo próprio do sistema eletrônico, que cumpre os requisitos estabelecidos no art. 3° da Lei Complementar nº 123, de 2006, estando apto a usufruir do tratamento favorecido estabelecido em seus arts. 42 a 49, observado o disposto nos §§ 1º ao 3º do art. 4º, da Lei n.º 14.133, de 2021.")

    # ========== 5. FASE DE LANCES ==========
    add_heading_custom(doc, "5. DA FASE DE LANCES", level=1)
    add_item(doc, "5.1.", "A partir da data e horário estabelecidos neste Aviso de Contratação Direta, a sessão pública será automaticamente aberta pelo sistema para o envio de lances públicos e sucessivos, exclusivamente por meio do sistema eletrônico, sendo encerrado no horário de finalização de lances também já previsto neste Aviso.")
    add_item(doc, "5.2.", "Iniciada a etapa competitiva, os fornecedores deverão encaminhar lances exclusivamente por meio de sistema eletrônico, sendo imediatamente informados do seu recebimento e do valor consignado no registro.")

    tipo_lance = "valor unitário" if data.get("criterio_julgamento") == "menor preço" else "percentual de desconto"
    add_item(doc, "5.2.1.", f"O lance deverá ser ofertado pelo {tipo_lance} do item.")

    add_item(doc, "5.3.", "O fornecedor somente poderá oferecer valor inferior ou percentual de desconto superior ao último lance por ele ofertado e registrado pelo sistema.")
    add_item(doc, "5.3.1.", "O fornecedor poderá oferecer lances sucessivos iguais ou superiores ao lance que esteja vencendo o certame, desde que inferiores ao menor por ele ofertado e registrado pelo sistema, sendo tais lances definidos como “lances intermediários” para os fins deste Aviso de Contratação Direta.")
    intervalo = data.get("intervalo_minimo_lances", "R$ 0,01")
    add_item(doc, "5.3.2.", f"O intervalo mínimo de diferença de valores ou percentuais entre os lances, que incidirá tanto em relação aos lances intermediários quanto em relação ao que cobrir a melhor oferta é de {intervalo}.")
    add_item(doc, "5.4.", "Havendo lances iguais ao menor já ofertado, prevalecerá aquele que for recebido e registrado primeiro no sistema.")
    add_item(doc, "5.5.", "Caso o fornecedor não apresente lances, concorrerá com o valor de sua proposta.")
    add_item(doc, "5.6.", "Durante o procedimento, os fornecedores serão informados, em tempo real, do valor do menor lance ou do maior desconto registrado, vedada a identificação do fornecedor.")
    add_item(doc, "5.7.", "Imediatamente após o término do prazo estabelecido para a fase de lances, haverá o seu encerramento, com o ordenamento e divulgação dos lances, pelo sistema, em ordem crescente de classificação.")
    add_item(doc, "5.7.1.", "O encerramento da fase de lances ocorrerá de forma automática pontualmente no horário indicado, sem qualquer possibilidade de prorrogação e não havendo tempo aleatório ou mecanismo similar.")

    # ========== 6. JULGAMENTO ==========
    add_heading_custom(doc, "6. DA FASE DE JULGAMENTO E ACEITAÇÃO DAS PROPOSTAS", level=1)
    add_item(doc, "6.1.", "Encerrada a fase de lances, quando a proposta do primeiro colocado permanecer acima do preço máximo ou abaixo do desconto definido para a contratação, o gestor poderá negociar condições mais vantajosas.")
    add_item(doc, "6.1.1.", "Neste caso, será encaminhada contraproposta ao fornecedor que tenha apresentado o menor preço ou o maior desconto, para que seja obtida a melhor proposta compatível em relação ao estipulado pela Administração.")
    add_item(doc, "6.1.2.", "A negociação poderá ser feita com os demais fornecedores classificados, exclusivamente por meio do sistema, respeitada a ordem de classificação, quando o primeiro colocado, mesmo após a negociação, for desclassificado em razão de sua proposta permanecer acima do preço máximo ou abaixo do desconto definido para a contratação.")
    add_item(doc, "6.2.", "Em qualquer caso, concluída a negociação, se houver, o resultado será divulgado a todos e registrado na ata do procedimento da dispensa eletrônica, devendo esta ser anexada aos autos do processo de contratação.")
    add_item(doc, "6.3.", "Constatada a compatibilidade entre o valor da proposta e o estipulado para a contratação, será solicitado ao fornecedor o envio da proposta adequada ao último lance ofertado ou ao valor negociado, se for o caso, acompanhada dos documentos complementares, quando necessários.")
    if data.get("exigir_planilha_custos"):
        add_item(doc, "6.3.1.", "Além da documentação supracitada, o fornecedor com a melhor proposta deverá encaminhar planilha com indicação de custos unitários e formação de preços, conforme modelo anexo, com os valores adequados à proposta vencedora.")

    add_item(doc, "6.4.", "Encerrada a etapa de negociação, se houver, o gestor verificará se o fornecedor provisoriamente classificado em primeiro lugar atende às condições de participação no certame, conforme previsto no art. 14 da Lei nº 14.133, de 2021, legislação correlata e nos itens 3.3 e seguintes deste Aviso, especialmente quanto à existência de sanção que impeça a participação no processo de contratação direta ou a futura contratação, mediante a consulta aos seguintes cadastros:")
    for cad in ["Sicaf", "Cadastro Nacional de Empresas Inidôneas e Suspensas – CEIS", "Cadastro Nacional de Empresas Punidas – CNEP", "Lista de licitantes inidôneos, mantida pelo Tribunal de Contas da União"]:
        add_item(doc, "", f"• {cad}")

    add_item(doc, "6.9.", "Verificadas as condições de participação e de utilização do tratamento favorecido, o gestor examinará a proposta classificada em primeiro lugar quanto à adequação ao objeto e à compatibilidade do preço em relação ao máximo estipulado para contratação neste Aviso de Contratação Direta e em seus anexos.")
    add_item(doc, "6.10.", "Será desclassificada a proposta vencedora que:")
    motivos = [
        "contiver vícios insanáveis;",
        "não obedecer às especificações técnicas pormenorizadas neste Aviso ou em seus anexos;",
        "apresentar preços inexequíveis ou que permanecerem acima do preço máximo definido para a contratação;",
        "não tiver sua exequibilidade demonstrada, quando exigido pela Administração;",
        "não cumpra os critérios de aceitabilidade de preços definidos no Termo de Referência;",
        "apresentar desconformidade com quaisquer outras exigências deste Aviso ou seus anexos, desde que insanável.",
    ]
    for i, m in enumerate(motivos, 1):
        add_item(doc, f"6.10.{i}.", m)

    # ========== 7. HABILITAÇÃO ==========
    add_heading_custom(doc, "7. DA FASE DE HABILITAÇÃO", level=1)
    add_item(doc, "7.1.", "Os documentos a serem exigidos para fins de habilitação, nos termos dos arts. 62 a 70 da Lei nº 14.133, de 2021, constam do Termo de Referência e serão solicitados do fornecedor mais bem classificado na fase de lances.")
    add_item(doc, "7.2.", "A habilitação dos fornecedores será verificada por meio do Sicaf, nos documentos por ele abrangidos.")
    add_item(doc, "7.2.1.", "É dever do fornecedor atualizar previamente as comprovações constantes do Sicaf para que estejam vigentes na data da abertura da sessão pública, ou encaminhar, quando solicitado, a respectiva documentação atualizada.")
    add_item(doc, "7.6.", f"Na hipótese de necessidade de envio de documentos complementares, indispensáveis à confirmação dos já apresentados para a habilitação, ou de documentos não constantes do Sicaf, o fornecedor será convocado a encaminhá-los, em formato digital, por meio do sistema, no prazo de {data.get('prazo_docs_habilitacao', '2')} ({data.get('prazo_docs_habilitacao_extenso', 'duas')}) horas, sob pena de inabilitação.")
    add_item(doc, "7.13.", "Será inabilitado o fornecedor que não comprovar sua habilitação, seja por não apresentar quaisquer dos documentos exigidos, ou apresentá-los em desacordo com o estabelecido neste Aviso de Contratação Direta.")
    add_item(doc, "7.14.", "Constatado o atendimento às exigências de habilitação, o fornecedor será habilitado.")

    # ========== 8. ATA DE REGISTRO DE PREÇOS ==========
    if data.get("registro_precos"):
        add_heading_custom(doc, "8. DA ATA DE REGISTRO DE PREÇOS", level=1)
        add_item(doc, "8.1.", f"Homologado o resultado do procedimento, o fornecedor mais bem classificado terá o prazo de {data.get('prazo_assinatura_arp', '5')} ({data.get('prazo_assinatura_arp_extenso', 'cinco')}) dias, contados a partir da data de sua convocação, para assinar a Ata de Registro de Preços, cujo prazo de validade encontra-se nela fixado, sob pena de decadência do direito à contratação, sem prejuízo das sanções previstas na Lei nº 14.133, de 2021.")
        add_item(doc, "8.8.", "O prazo de vigência da ata de registro de preços será de 1 (um) ano e poderá ser prorrogado, por igual período, desde que comprovado o preço vantajoso.")
        if data.get("renovar_quantitativo_arp"):
            add_item(doc, "8.8.1.", "Em caso de prorrogação da ata, poderá ser renovado o quantitativo originalmente registrado.")
        else:
            add_item(doc, "8.8.1.", "Em caso de prorrogação da ata, não poderá ser renovado o quantitativo originalmente registrado.")

    # ========== 9. CADASTRO DE RESERVA ==========
    if data.get("registro_precos"):
        add_heading_custom(doc, "9. DA FORMAÇÃO DO CADASTRO DE RESERVA", level=1)
        add_item(doc, "9.1.", "Após a homologação do procedimento, será incluído na ata, na forma de anexo, o registro:")
        add_item(doc, "9.1.1.", "dos fornecedores que aceitarem cotar o objeto com preço igual ao do adjudicatário, observada a classificação no procedimento e excluído o percentual referente à margem de preferência, quando o objeto não atender aos requisitos previstos no art. 26 da Lei nº 14.133, de 2021; e")
        add_item(doc, "9.1.2.", "dos fornecedores que mantiverem sua proposta original.")
        add_item(doc, "9.2.", "Será respeitada, nas contratações, a ordem de classificação dos fornecedores registrados na ata.")

    # ========== 10. CONTRATAÇÃO ==========
    add_heading_custom(doc, "10. DA CONTRATAÇÃO", level=1)
    add_item(doc, "10.1.", "Após a homologação e adjudicação, caso se conclua pela contratação, será firmado Termo de Contrato ou emitido instrumento equivalente.")
    add_item(doc, "10.2.", f"O adjudicatário terá o prazo de {data.get('prazo_assinatura_contrato', '10')} ({data.get('prazo_assinatura_contrato_extenso', 'dez')}) dias úteis, contados a partir da data de sua convocação, para assinar o Termo de Contrato ou aceitar instrumento equivalente, conforme o caso (Nota de Empenho/Carta Contrato/Autorização), sob pena de decair o direito à contratação, sem prejuízo das sanções previstas neste Aviso de Contratação Direta.")
    add_item(doc, "10.4.", "O prazo de vigência da contratação é o estabelecido no Termo de Referência.")
    add_item(doc, "10.5.", "Na assinatura do contrato ou do instrumento equivalente será exigida a comprovação das condições de habilitação e contratação consignadas neste aviso, que deverão ser mantidas pelo fornecedor durante a vigência do contrato.")

    # ========== 11. SANÇÕES ==========
    add_heading_custom(doc, "11. DAS INFRAÇÕES E SANÇÕES ADMINISTRATIVAS", level=1)
    add_item(doc, "11.1.", "Comete infração administrativa o fornecedor que praticar quaisquer das hipóteses previstas no art. 155 da Lei nº 14.133, de 2021.")
    multa_pct = data.get("percentual_multa", ".......")
    add_item(doc, "11.1.15.", f"Multa de {multa_pct}% sobre o valor estimado do(s) item(s) prejudicado(s) pela conduta do fornecedor, por qualquer das infrações dos subitens 11.1.1 a 11.1.12;")
    add_item(doc, "11.2.", "A aplicação das sanções previstas neste Aviso de Contratação Direta não exclui, em hipótese alguma, a obrigação de reparação integral do dano causado à Contratante.")
    add_item(doc, "11.3.", "Todas as sanções previstas neste Aviso poderão ser aplicadas cumulativamente com a multa.")
    add_item(doc, "11.4.", "Antes da aplicação da multa, será facultada a defesa do interessado no prazo de 15 (quinze) dias úteis, contado da data de sua intimação.")
    add_item(doc, "11.6.", f"Previamente ao encaminhamento à cobrança judicial, a multa poderá ser recolhida administrativamente no prazo máximo de {data.get('prazo_recolhimento_multa', '15')} ({data.get('prazo_recolhimento_multa_extenso', 'quinze')}) dias, a contar da data do recebimento da comunicação enviada pela autoridade competente.")

    # ========== 12. DISPOSIÇÕES GERAIS ==========
    add_heading_custom(doc, "12. DAS DISPOSIÇÕES GERAIS", level=1)
    add_item(doc, "12.1.", "No caso de todos os fornecedores restarem desclassificados ou inabilitados (procedimento fracassado), a Administração poderá:")
    add_item(doc, "12.1.1.", "republicar o presente Aviso com uma nova data;")
    add_item(doc, "12.1.2.", "valer-se, para a contratação, de proposta obtida na pesquisa de preços que serviu de base ao procedimento, se houver, privilegiando-se os menores preços, sempre que possível, e desde que atendidas às condições de habilitação exigidas;")
    add_item(doc, "12.5.", "Não havendo expediente ou ocorrendo qualquer fato superveniente que impeça a realização do certame na data marcada, a sessão será automaticamente transferida para o primeiro dia útil subsequente, no mesmo horário anteriormente estabelecido, desde que não haja comunicação em contrário.")
    add_item(doc, "12.6.", "Os horários estabelecidos na divulgação deste procedimento e durante o envio de lances observarão o horário de Brasília-DF, inclusive para contagem de tempo e registro no Sistema e na documentação relativa ao procedimento.")
    add_item(doc, "12.8.", "As normas disciplinadoras deste Aviso de Contratação Direta serão sempre interpretadas em favor da ampliação da disputa entre os interessados, desde que não comprometam o interesse da Administração, o princípio da isonomia, a finalidade e a segurança da contratação.")
    add_item(doc, "12.11.", "Da sessão pública será divulgada Ata no sistema eletrônico.")

    add_item(doc, "12.12.", "Integram este Aviso de Contratação Direta, para todos os fins e efeitos, os seguintes anexos:")
    anexos = ["ANEXO I – Termo de Referência"]
    if data.get("registro_precos"):
        anexos.append("ANEXO II – Minuta de Ata de Registro de Preços")
    anexos.append("ANEXO III – Minuta de Termo de Contrato")
    if data.get("exigir_planilha_custos"):
        anexos.append("ANEXO IV – Planilha de Custos e Formação de Preços")
    for a in anexos:
        add_item(doc, "", f"• {a}")

    # Assinatura
    doc.add_paragraph()
    local = data.get("local", "[Local]")
    data_doc = data.get("data_documento", datetime.now().strftime("%d de %B de %Y"))
    add_para(doc, f"{local}, {data_doc}.")
    doc.add_paragraph()
    add_para(doc, data.get("autoridade", "[ASSINATURA DA AUTORIDADE COMPETENTE]"), bold=True)
    add_para(doc, data.get("cargo_autoridade", "[Cargo]"))

    # Salvar em memória
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
