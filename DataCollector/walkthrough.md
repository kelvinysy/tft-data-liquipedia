# Verification Walkthrough

I have verified the environment and script readiness for [LiquipediaHttpClient.py](file:///c:/source/TFTDataProcessor/LiquipediaHttpClient.py).

## Steps Taken

1.  **Environment Check**: Verified that the virtual environment `.venv` exists and contains the required `requests` library.
2.  **Script Verification**: Verified that [LiquipediaHttpClient.py](file:///c:/source/TFTDataProcessor/LiquipediaHttpClient.py) is configured with a main block that correctly attempts to connect to the Liquipedia API.
3.  **Dry Run**: Executed the script and confirmed it correctly identifies missing/invalid API credentials (returning a 403 error as expected).

## How to Run the Script

To run the script successfully, follow these steps in your terminal:

### 1. Set your API Key
```powershell
$env:LIQUIPEDIA_API_KEY = "your_actual_api_key_here"
```

### 2. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Run the Script
```powershell
python LiquipediaHttpClient.py
```

> [!NOTE]
> The script is configured to respect rate limits (1 request per minute) and will wait 60 seconds between successful requests.
