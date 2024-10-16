import requests


class XNAT:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth_url = f"{base_url}/data/JSESSION"
        self.inbox_url = f"{base_url}/data/services/import"
        self.username = username
        self.password = password
        self._create_session()
        self.inbox_sessions = []

    def _create_session(self):
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({'Content-Type': 'application/json'})
        response = self.session.post(self.auth_url)
        if response.status_code != 200:
            raise Exception("Failed to authenticate with XNAT")

    def get_session(self):
        return self.session

    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.session.close()

    # ~ DICOM Inbox methods
    def post_to_inbox(self, project_id, subject_id, expt_label, inbox_path):
        params = {
            'import-handler': 'inbox',
            'cleanupAfterImport': 'true',
            'PROJECT_ID': project_id,
            'SUBJECT_ID': subject_id,
            'EXPT_LABEL': expt_label,
            'path': inbox_path
        }
        return self.session.post(self.inbox_url, params=params)
