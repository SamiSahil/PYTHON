import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_drive_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # Use absolute path to credentials.json
    creds_path = os.path.join(SCRIPT_DIR, 'credentials.json')
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

def upload_and_convert(service, file_path):
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    file_metadata = {
        'name': file_name,
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,webViewLink'
    ).execute()
    
    print(f"Uploaded & converted: {file_name} (ID: {file['id']})")
    return file['id']

if __name__ == "__main__":
    service = get_drive_service()
    docx_folder = r"G:\Takeout\186\New Word File"
    output_file = os.path.join(SCRIPT_DIR, 'doc_ids.txt')
    
    # Clear previous content if file exists
    open(output_file, 'w').close()
    
    for filename in os.listdir(docx_folder):
        if filename.endswith('.docx'):
            file_path = os.path.join(docx_folder, filename)
            google_docs_id = upload_and_convert(service, file_path)
            with open(output_file, 'a') as f:
                f.write(f"{google_docs_id}\n")