import json
import time
import logging
from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import QUrl, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

def fetch_hiking_data(wkt_text, crs, method, url, timeout=30):
    """
    Fetch hiking data from a web service using QGIS network manager.
    
    Args:
        wkt_text (str): WKT geometry
        crs (str): CRS identifier
        method (str): Calculation method
        url (str): API endpoint
        timeout (int): Request timeout in seconds

    Returns:
        dict or None: JSON response or None if failed
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

    # Start timing
    start_time = time.time()
    print(f"Starting request at {time.ctime()}")

    # Send POST request
    reply = nam.post(request, payload)

    # Wait for reply synchronously 
    # use async instead?
    loop = QEventLoop()
    reply.finished.connect(loop.quit)
    loop.exec_()

    elapsed = time.time() - start_time
    print(f"Response received in {elapsed:.2f} seconds")

    # Check for errors
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
