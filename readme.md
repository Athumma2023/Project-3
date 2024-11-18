# Audio Analysis Application

## Quick Links
- **Live Application:** https://llmsproject.uc.r.appspot.com/
- **Local Development URL:** http://localhost:8080
- **Python Version Required:** 3.9+
- **Framework:** Flask
- **Cloud Platform:** Google Cloud (App Engine)

## Quick Start Setup
```bash
# Clone and setup environment
git clone <repository-url>
cd LLM_Flask_Final
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Project Structure
```
LLM_Flask_Final/
├── templates/
│   └── index3.html          # Main interface template
├── uploads/                 # Temporary upload directory
├── main.py                 # Application main file
├── requirements.txt        # Project dependencies
├── app.yaml               # App Engine configuration
└── Ajay_application_default_credentials.json  # GCP credentials
```

## Detailed Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher installed
- Google Cloud SDK installed
- Google Cloud Project with the following APIs enabled:
  - Vertex AI API
  - Cloud Text-to-Speech API
  - Cloud Storage API
- Service Account with appropriate permissions

### 2. Google Cloud Setup
1. Create a project in Google Cloud Console
2. Enable required APIs
3. Create a service account with the following roles:
   - Vertex AI User
   - Cloud Text-to-Speech User
   - Storage Object Viewer
4. Download service account key and rename to "Ajay_application_default_credentials.json"

### 3. Local Configuration
1. Place the credentials file in project root directory
2. Create app.yaml with configuration:
```yaml
runtime: python39
instance_class: F1
env_variables:
  GOOGLE_APPLICATION_CREDENTIALS: "Ajay_application_default_credentials.json"
```

### 4. Application Features
- Real-time audio recording in browser
- Audio file upload support
- Automated transcription with timestamps
- Speaker identification
- Sentiment analysis
- Text-to-speech response generation

### 5. API Endpoints
```
GET  /              - Main application interface
POST /upload        - Handle recorded audio
POST /analyze       - Process uploaded audio files
GET  /get_audio    - Retrieve processed audio
GET  /health       - Health check
GET  /_ah/warmup   - App Engine warmup
```

## Usage Guide

### Local Development
1. Start the application:
```bash
python main.py
```
2. Access http://localhost:8080 in your browser
3. Use either recording or file upload feature
4. Review transcription and sentiment analysis
5. Listen to generated audio summary

### Production Application
1. Access https://llmsproject.uc.r.appspot.com/
2. Application provides identical features as local version
3. Supports multiple users and concurrent processing

## Technical Details

### Audio Processing Specifications
- Supported Formats: MP3, WAV
- Maximum File Size: 10MB
- Audio Quality: 44.1kHz, Mono
- Response Format: MP3

### Cloud Services Integration
- Vertex AI with Gemini 1.5 Pro for analysis
- Cloud Text-to-Speech for response generation
- App Engine for application hosting

## Troubleshooting Guide

### Common Issues and Solutions

1. Authentication Errors
```bash
# Verify Google Cloud authentication
gcloud auth application-default login
gcloud config set project llmsproject
```

2. Audio Processing Failures
- Verify file format (MP3/WAV)
- Check file size (<10MB)
- Ensure clear audio quality
- Verify internet connectivity

3. Service Connection Issues
- Check Google Cloud Console for API status
- Verify credential file placement
- Ensure required APIs are enabled

4. Port Conflicts
```bash
# Modify port in main.py if 8080 is in use
app.run(host='0.0.0.0', port=8081)  # Change to available port
```

### Browser Requirements
- Modern browser with MediaRecorder API support
- Enabled microphone permissions for recording
- Active internet connection
- JavaScript enabled

## Deployment

### Local to Production
1. Install Google Cloud SDK
2. Initialize and authenticate:
```bash
gcloud init
gcloud auth application-default login
```

3. Deploy to App Engine:
```bash
gcloud app deploy app.yaml
```

### Monitoring
- Access Google Cloud Console for logs
- Monitor resource usage
- Track API quotas and limits

## Additional Notes
- Application requires active internet connection
- All processing occurs in real-time
- Data is not permanently stored
- Service account credentials are required for both local and production

## Support
For additional support or issues:
1. Check Google Cloud Documentation
2. Verify service status in Google Cloud Console
3. Review application logs for specific errors

## Security Considerations
- Keep credentials file secure
- Don't commit credentials to version control
- Regularly rotate service account keys
- Monitor API usage and access logs

The application is ready for both local development and production use. For any additional questions or support requirements, consult the Google Cloud documentation or contact the development team.