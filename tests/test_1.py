import pytest
import json
import urllib
from unittest.mock import patch, MagicMock
from io import BytesIO
from api import fetch_hiking_data

url = "https://voibos.rechenraum.com/voibos/voibos"

def test_fetch_hiking_data_success():
    """Test successful API call with valid WKT data in Vorarlberg."""
    # WKT linestring in EPSG:31254 (MGI / Austria GK West) 
    # Coordinates approximately in Bregenz, Vorarlberg
    # Starting point near Bregenz and extending ~1km eastward
    wkt_text = "LINESTRING(85000 260000, 86000 260000)"
    crs = "31254"
    method = "standard"
    
    # Mock response data
    mock_response_data = {
        "status": "success",
        "hiking_time": 12.5,  # minutes
        "distance": 1000,  # meters
        "elevation_gain": 50,  # meters
        "elevation_loss": 20,  # meters
    }
    
    # Convert the mock response to bytes as that's what urlopen returns
    mock_response_bytes = json.dumps(mock_response_data).encode('utf-8')
    
    # Create a mock response object
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = mock_response_bytes
    mock_response.__enter__.return_value = mock_response
    
    # Patch urlopen to return our mock response
    with patch('urllib.request.urlopen', return_value=mock_response):
        result = fetch_hiking_data(wkt_text, crs, method, url)
        
        # Check if the result matches our mock data
        assert result == mock_response_data
        
        # Verify the mocked response was called with expected parameters
        # This would require additional setup with patch.object and is optional

def test_fetch_hiking_data_http_error():
    """Test handling of HTTP errors."""
    wkt_text = "LINESTRING(85000 260000, 86000 260000)"
    crs = "31254"
    method = "standard"
    
    # Mock a HTTP error
    with patch('urllib.request.urlopen', side_effect=urllib.error.HTTPError(
            url, 404, 'Not Found', {}, None)):
        result = fetch_hiking_data(wkt_text, crs, method, url)
        assert result is None

def test_fetch_hiking_data_invalid_json():
    """Test handling of invalid JSON response."""
    wkt_text = "LINESTRING(85000 260000, 86000 260000)"
    crs = "31254"
    method = "standard"
    
    # Create a mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = b"Invalid JSON data"
    mock_response.__enter__.return_value = mock_response
    
    # Patch urlopen to return our mock response
    with patch('urllib.request.urlopen', return_value=mock_response):
        result = fetch_hiking_data(wkt_text, crs, method, url)
        assert result is None

#@pytest.mark.integration
def test_real_api_call():
    """
    Test with a real API call to the service.
    This test makes an actual network request and should be used sparingly.
    """
    # WKT linestring in EPSG:31254 (MGI / Austria GK West) 
    # Coordinates approximately in Bregenz, Vorarlberg
    # Starting point near Bregenz and extending ~1km eastward
    wkt_text = "LINESTRING(85000 260000, 86000 260000)"
    crs = "31254"
    method = "viia"
    
    # Try to make the actual API call
    try:
        result = fetch_hiking_data(wkt_text, crs, method, url, timeout=60)
        
        # Verify we got a valid response
        assert result is not None, "API returned None"
        
        # Check the structure of the result - adjust based on actual API response
        # These are just examples of what you might want to check
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Print the result for inspection
        print(f"API Response: {json.dumps(result, indent=2)}")
        
        # Optional: You can add more specific assertions based on the actual API response
        # For example:
        # assert "hiking_time" in result, "Response should contain hiking_time"
        # assert "distance" in result, "Response should contain distance"
        
    except urllib.error.URLError as e:
        pytest.skip(f"API endpoint not available: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error during API call: {str(e)}")