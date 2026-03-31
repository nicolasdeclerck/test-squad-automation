from apps.blog.utils import blocknote_json_to_html


class TestBlocknoteJsonToHtml:
    def test_empty_input(self):
        assert blocknote_json_to_html([]) == ""
        assert blocknote_json_to_html(None) == ""
        assert blocknote_json_to_html({}) == ""

    def test_paragraph(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello world"}],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert result == "<p>Hello world</p>"

    def test_heading_levels(self):
        for level in [1, 2, 3]:
            blocks = [
                {
                    "type": "heading",
                    "props": {"level": level},
                    "content": [{"type": "text", "text": "Titre"}],
                }
            ]
            result = blocknote_json_to_html(blocks)
            assert f"<h{level}>Titre</h{level}>" in result

    def test_bold_text(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "gras",
                        "styles": {"bold": True},
                    }
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<strong>gras</strong>" in result

    def test_italic_text(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "italique",
                        "styles": {"italic": True},
                    }
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<em>italique</em>" in result

    def test_combined_styles(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "mix",
                        "styles": {"bold": True, "italic": True},
                    }
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<strong>" in result
        assert "<em>" in result
        assert "mix" in result

    def test_bullet_list(self):
        blocks = [
            {
                "type": "bulletListItem",
                "content": [{"type": "text", "text": "Item 1"}],
            },
            {
                "type": "bulletListItem",
                "content": [{"type": "text", "text": "Item 2"}],
            },
        ]
        result = blocknote_json_to_html(blocks)
        assert "<ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "</ul>" in result

    def test_numbered_list(self):
        blocks = [
            {
                "type": "numberedListItem",
                "content": [{"type": "text", "text": "Premier"}],
            },
            {
                "type": "numberedListItem",
                "content": [{"type": "text", "text": "Deuxième"}],
            },
        ]
        result = blocknote_json_to_html(blocks)
        assert "<ol>" in result
        assert "<li>Premier</li>" in result
        assert "</ol>" in result

    def test_code_block(self):
        blocks = [
            {
                "type": "codeBlock",
                "content": [{"type": "text", "text": "print('hello')"}],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<pre><code>" in result
        assert "print(&#x27;hello&#x27;)" in result

    def test_nested_children(self):
        blocks = [
            {
                "type": "bulletListItem",
                "content": [{"type": "text", "text": "Parent"}],
                "children": [
                    {
                        "type": "bulletListItem",
                        "content": [{"type": "text", "text": "Enfant"}],
                    }
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "Parent" in result
        assert "Enfant" in result

    def test_underline_and_strikethrough(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "souligné",
                        "styles": {"underline": True},
                    },
                    {
                        "type": "text",
                        "text": "barré",
                        "styles": {"strikethrough": True},
                    },
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<u>souligné</u>" in result
        assert "<s>barré</s>" in result

    def test_string_input(self):
        import json

        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "From string"}],
            }
        ]
        result = blocknote_json_to_html(json.dumps(blocks))
        assert "<p>From string</p>" in result

    def test_html_escaping(self):
        blocks = [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "<script>alert('xss')</script>"}
                ],
            }
        ]
        result = blocknote_json_to_html(blocks)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
