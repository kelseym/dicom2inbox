


class JobStatus:
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = 'Started'
        self.dicom_edit_target = ''
        self.dicom_edit_status = ''
        self.dicom_inbox_id = ''
        self.dicom_inbox_status = ''

    @staticmethod
    def header():
        return "Job ID,Status,DicomEditTarget,DicomEditStatus,DicomInboxID,DicomInboxStatus"

    def csv(self):
        return f"{self.job_id},{self.status},{self.dicom_edit_target},{self.dicom_edit_status},{self.dicom_inbox_id},{self.dicom_inbox_status}"