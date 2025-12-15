import pytest
from unittest.mock import patch, MagicMock, mock_open
from engine.utils import process_website_data, load_config

def test_process_website_data_success():
    """Test that valid HTML is correctly processed and returned."""
    mock_html = "<html><body><h1>Welcome</h1><p>Text</p></body></html>"
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        with patch('engine.utils.MarkItDown') as mock_md:
            mock_md_instance = mock_md.return_value
            mock_md_instance.convert_stream.return_value.text_content = "Welcome Text"

            url, cleaned_html, visible_text = process_website_data("http://example.com")

            assert url == "http://example.com"
            assert "Welcome" in cleaned_html
            assert visible_text == "Welcome Text"

def test_process_website_data_failure():
    """Test that the function returns Nones when the website is down (404)."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = Exception("404 Error")

        url, cleaned_html, visible_text = process_website_data("http://bad-url.com")

        assert url is None
        assert cleaned_html is None
        assert visible_text is None

def test_process_website_data_html_truncation():
    """Test the HTML truncation logic."""
    huge_html = "a" * 19990 + "<div></div>" + "b" * 100
    
    with patch('requests.get') as mock_get, \
         patch('engine.utils.MarkItDown') as mock_md:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = huge_html
        mock_get.return_value = mock_response
        
        mock_md.return_value.convert_stream.return_value.text_content = "Short text"

        url, cleaned_html, visible_text = process_website_data("http://trunc-html.com")

        assert len(cleaned_html) <= 20005 # 20000 + len('\n') approx
        assert cleaned_html.endswith(">\n") # Should end with a closing tag + newline
        assert len(cleaned_html) < len(huge_html) # Verify it actually truncated

def test_process_website_data_text_truncation():
    """Test the Visible Text truncation logic."""
    short_html = "<html><body>Content</body></html>"
    
    with patch('requests.get') as mock_get, \
         patch('engine.utils.MarkItDown') as mock_md:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = short_html
        mock_get.return_value = mock_response
        
        huge_text = "x" * 25000
        mock_md.return_value.convert_stream.return_value.text_content = huge_text

        url, cleaned_html, visible_text = process_website_data("http://trunc-text.com")

        assert "\n[Content truncated...]" in visible_text
        expected_len = 20000 + len("\n[Content truncated...]")
        assert len(visible_text) == expected_len

def test_process_website_data_empty_returns_none():
    """Test the empty content check."""
    only_style_html = "<style>body { color: red; }</style>"
    
    with patch('requests.get') as mock_get, \
         patch('engine.utils.MarkItDown') as mock_md:
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = only_style_html
        mock_get.return_value = mock_response
        mock_md.return_value.convert_stream.return_value.text_content = ""
        url, cleaned_html, visible_text = process_website_data("http://empty.com")

        assert url is None
        assert cleaned_html is None
        assert visible_text is None

def test_load_config():
    """Test that the configuration loads correctly from a mocked YAML file."""
    mock_yaml_content = """
    judgement_agent:
      model: "gemini-pro"
      name: "judge"
    """
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)) as mock_file:
        with patch("yaml.safe_load") as mock_yaml_load:
            mock_yaml_load.return_value = {
                "judgement_agent": {"model": "gemini-pro", "name": "judge"}
            }
            config = load_config()
            assert config["judgement_agent"]["name"] == "judge"