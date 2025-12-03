import os
import uuid
from jobs.application_job import ApplicationJob
from services.openlp_service import extract_openlp_items, extract_service_items


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)
TMP_DIR = os.path.join(BASE_DIR, "tmp")

class UploaderJob(ApplicationJob):
    def run(self, job_id, data):
        job_dir = os.path.join(TMP_DIR, job_id)
        service_file_path = data['service_file_path']
        theme_file_path = data['theme_file_path']

        service_extract_dir, theme_extract_dir = extract_openlp_items(job_dir, service_file_path, theme_file_path)

        slides = extract_service_items(service_extract_dir)


