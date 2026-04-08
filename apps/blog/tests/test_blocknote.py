import json

from apps.blog.templatetags.blog_extras import blocknote_plaintext

BLOCKNOTE_JSON_CONTENT = json.dumps(
    [
        {
            "id": "1",
            "type": "heading",
            "props": {"level": 2},
            "content": [{"type": "text", "text": "Mon titre"}],
            "children": [],
        },
        {
            "id": "2",
            "type": "paragraph",
            "props": {},
            "content": [
                {"type": "text", "text": "Un paragraphe avec du "},
                {
                    "type": "text",
                    "text": "texte en gras",
                    "styles": {"bold": True},
                },
                {"type": "text", "text": "."},
            ],
            "children": [],
        },
    ]
)

BLOCKNOTE_MERMAID_CONTENT = json.dumps(
    [
        {
            "id": "1",
            "type": "paragraph",
            "props": {},
            "content": [{"type": "text", "text": "Voici un diagramme :"}],
            "children": [],
        },
        {
            "id": "2",
            "type": "mermaid",
            "props": {"data": "graph TD\n    A[Début] --> B[Fin]"},
            "content": [],
            "children": [],
        },
        {
            "id": "3",
            "type": "paragraph",
            "props": {},
            "content": [{"type": "text", "text": "Fin de l'article."}],
            "children": [],
        },
    ]
)


class TestBlockNotePlaintext:
    def test_extracts_text_from_blocknote_json(self):
        result = blocknote_plaintext(BLOCKNOTE_JSON_CONTENT)
        assert "Mon titre" in result
        assert "Un paragraphe avec du" in result
        assert "texte en gras" in result

    def test_returns_plain_text_as_is(self):
        assert blocknote_plaintext("Du texte simple") == "Du texte simple"

    def test_returns_empty_string_for_empty_input(self):
        assert blocknote_plaintext("") == ""
        assert blocknote_plaintext(None) == ""

    def test_returns_value_for_invalid_json(self):
        assert blocknote_plaintext("{invalid") == "{invalid"


class TestBlockNoteMermaidPlaintext:
    def test_mermaid_plaintext_extraction(self):
        result = blocknote_plaintext(BLOCKNOTE_MERMAID_CONTENT)
        assert "Voici un diagramme :" in result
        assert "[Diagramme Mermaid]" in result
        assert "Fin de l'article." in result

    def test_mermaid_empty_data_excluded(self):
        content = json.dumps(
            [
                {
                    "id": "1",
                    "type": "mermaid",
                    "props": {"data": ""},
                    "content": [],
                    "children": [],
                }
            ]
        )
        result = blocknote_plaintext(content)
        assert "[Diagramme Mermaid]" not in result

    def test_mermaid_block_does_not_leak_raw_code(self):
        result = blocknote_plaintext(BLOCKNOTE_MERMAID_CONTENT)
        assert "graph TD" not in result

    def test_mermaid_xss_in_data_not_rendered(self):
        content = json.dumps(
            [
                {
                    "id": "1",
                    "type": "mermaid",
                    "props": {"data": "<script>alert('xss')</script>"},
                    "content": [],
                    "children": [],
                }
            ]
        )
        result = blocknote_plaintext(content)
        assert "<script>" not in result
        assert "alert" not in result
        assert "[Diagramme Mermaid]" in result
