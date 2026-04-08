import json
import time
import logging
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

def fetch_hiking_data(wkt_text, crs, method, url, timeout=30):
    """
    Function to fetch hiking data from the given web service.
    
    Args:
        wkt_text (str): The WKT (Well-Known Text) representation of geometry
        crs (str): Coordinate Reference System identifier
        method (str): The calculation method to use
        url (str): The API endpoint URL
        timeout (int, optional): Timeout in seconds for the request. Defaults to 30.
        use_requests (bool, optional): Use requests library instead of urllib. Defaults to True.
        
    Returns:
        dict or None: The JSON response data if successful, None otherwise
    """
    post_data = {
        "name": "wegzeit",
        "polygonzug": wkt_text,
        "crs": crs,
        "methode": method,
        "output": "jsondownload"
    }

    # Format data as JSON
    payload = json.dumps(post_data).encode("utf-8")

    # Get the QGIS network manager instance
    nam = QgsNetworkAccessManager.instance()
    request = QNetworkRequest(QUrl(url))
    request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
    #TODO QGIS4: request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

    # Start timing
    start_time = time.time()
    print(f"Starting request at {time.ctime()}")

    # Send POST request
    reply = nam.post(request, payload)

    # Wait for reply synchronously 
    loop = QEventLoop()
    reply.finished.connect(loop.quit)
    loop.exec_()
    #TODO QGIS4: loop.exec()

    elapsed = time.time() - start_time
    print(f"Response received in {elapsed:.2f} seconds")

    # Check for errors
    #TODO QGIS4: if reply.error() != QNetworkReply.NetworkError.NoError:
    if reply.error() != QNetworkReply.NoError:
        logging.error(f"Network error after {elapsed:.2f}s: {reply.errorString()}")
        reply.deleteLater()
        return None

    # Read and parse JSON
    try:
        data = reply.readAll().data()
        result = json.loads(data)
        reply.deleteLater()
        return result
    except ValueError as e:
        logging.warning(f"Error decoding JSON: {str(e)}")
        reply.deleteLater()
        return None
