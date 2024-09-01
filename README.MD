# Remove cabeçalho e rodapé de PDFs
Uma ferramenta para remover cabeçalhos e rodapés de arquivos PDF e otimizar o tamanho dos arquivos resultantes. Utiliza a biblioteca PyMuPDF (fitz) para manipulação de PDFs e o algoritmo HDBSCAN para identificar clusters de coordenadas de blocos de texto que são usados para estimar as áreas dos cabeçalhos e rodapés.
## Passos para execução
Primeiramente clone o repositório para o seu computador, depois siga os passos.
## Windows
- Criar ambiente virtual
- `python -m venv .\venv`
- Ativar
-  `.\venv\Scripts\activate`
- Instalar requisitos
- `pip install -r .\requirements.txt`
- Colocar os PDFs na pasta PDF_IN
- Ou alterar as variáveis `path_in` e `path_out` em `main.py`
- executar o programa `python -m main`
## Linux
- Criar ambiente virtual
-  `python3 -m venv ./venv`
- Ativar:
-  `./venv/bin/activate`
- Instalar requisitos
-  `pip install -r ./requirements.txt`
- Colocar os PDFs na pasta PDF_IN
- Ou alterar as variáveis `path_in` e `path_out` em `main.py`
- executar o programa `python3 -m main`
## Detalhes de Implementação
- Caso tenha problemas com a precisão ajustar a variável `hff` linha 33 no arquivo `pdf_remove_header_footer.py`
- Voçê pode instalar as biblioteca manualmente `pip install pymupdf numpy pandas scikit-learn`
- Qualidade das Imagens: As imagens re-inseridas são compactadas com uma qualidade definida de 75 `page.insert_image(rect, stream=img['image'], keep_proportion=True, quality=75)`. Isso pode ser ajustado linha 73.
