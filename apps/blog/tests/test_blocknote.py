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
