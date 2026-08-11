from radar_ufersa.adapters.html_bs4 import BeautifulSoupAnchorExtractor


def test_extract_resolves_links_filters_schemes_and_deduplicates() -> None:
    html = """
    <html><body><nav><a href='/nav'>Nav</a></nav><main>
      <a href='/edital'> Edital   de servidores </a>
      <a href='/edital'>Edital de servidores</a>
      <a href='#top'>Topo</a>
      <a href='mailto:x@ufersa.edu.br'>E-mail</a>
      <a href='javascript:void(0)'>Script</a>
      <a href='/empty'><span></span></a>
    </main></body></html>
    """
    extractor = BeautifulSoupAnchorExtractor()

    anchors = extractor.extract("https://ufersa.edu.br/base/", html)

    assert len(anchors) == 1
    assert anchors[0].title == "Edital de servidores"
    assert anchors[0].url == "https://ufersa.edu.br/edital"


def test_extract_uses_entry_content_when_main_is_absent() -> None:
    html = """
    <html><body><a href='/outside'>Outside</a>
    <div class='entry-content'><a href='arquivo.pdf'>Arquivo PDF</a></div>
    </body></html>
    """
    extractor = BeautifulSoupAnchorExtractor()

    anchors = extractor.extract("https://ufersa.edu.br/pagina/", html)

    assert anchors == (
        anchors[0],
    )
    assert anchors[0].url == "https://ufersa.edu.br/pagina/arquivo.pdf"
    assert anchors[0].title == "Arquivo PDF"


def test_extract_uses_table_row_context_for_generic_consultar_link() -> None:
    html = """
    <html><body><main><table><tr>
      <td>Processo Seletivo de Remoção de Servidores Técnico-Administrativos</td>
      <td><a href='/processo/42'>Consultar</a></td>
    </tr></table></main></body></html>
    """
    extractor = BeautifulSoupAnchorExtractor()

    anchors = extractor.extract("https://sistemas.ufersa.edu.br/concursos/publico", html)

    assert len(anchors) == 1
    assert "Servidores Técnico-Administrativos" in anchors[0].title
    assert anchors[0].url == "https://sistemas.ufersa.edu.br/processo/42"


def test_extract_uses_paragraph_context_for_portaria_description() -> None:
    html = """
    <html><body><main><p>
      <a href='/portaria.pdf'>PORTARIA Nº 10/2026</a> - Designar Comissão de Trabalho.
    </p></main></body></html>
    """
    extractor = BeautifulSoupAnchorExtractor()

    anchors = extractor.extract("https://documentos.ufersa.edu.br/2026/", html)

    assert len(anchors) == 1
    assert "Designar Comissão de Trabalho" in anchors[0].title
