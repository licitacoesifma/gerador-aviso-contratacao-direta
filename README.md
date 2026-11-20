# Gerador de Aviso de Contratação Direta (Dispensa Eletrônica)

Aplicação web em **Streamlit** para elaboração guiada do **Aviso de Contratação Direta** nos moldes da Lei nº 14.133/2021 e da Instrução Normativa SEGES/ME nº 67/2021.

## Funcionalidades

- Formulário por seções com **notas explicativas oficiais**
- Campos condicionais (Registro de Preços, exclusividade ME/EPP, etc.)
- Validação de campos obrigatórios + pré-visualização
- Geração de arquivo **.docx**
- **Exportar / Importar preenchimento em JSON**
- **Upload de novo modelo oficial** → atualiza automaticamente as notas explicativas

## Como rodar localmente

```bash
git clone https://github.com/SEU_USUARIO/aviso-dispensa-eletronica.git
cd aviso-dispensa-eletronica
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Community Cloud

1. Suba o repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte a conta GitHub → New app
4. Selecione o repositório e o arquivo `app.py`
5. Deploy

## Atualizando quando sair novo modelo da AGU/SEGES

1. Baixe o novo modelo oficial (`.docx`)
2. No app, vá em **9. Atualizar Modelo Oficial**
3. Faça upload → clique em **Aplicar estas notas**
4. Baixe o `notes.py` gerado e substitua no repositório
5. Commit + push → o Streamlit Cloud atualiza

> A estrutura do formulário permanece a mesma. Apenas as notas são atualizadas automaticamente. Mudanças estruturais grandes no modelo ainda exigem ajuste manual.

## Estrutura

```
aviso_dispensa_eletronica/
├── app.py              # Interface Streamlit
├── generator.py        # Gera o .docx
├── notes.py            # Notas explicativas (padrão)
├── model_parser.py     # Extrai notas de novo modelo oficial
├── requirements.txt
└── README.md
```

## Licença

Uso livre para órgãos públicos. Adapte conforme necessidade.
