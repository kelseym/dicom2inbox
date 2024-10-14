import argparse
import glob
import logging
import sys
import os
import threading
import re

from DicomEdit import DicomEdit
from JobStatus import JobStatus
from RefacePathCSV import RefacePathCSV
from XNAT import XNAT

job_progress = {}
lock = threading.Lock()

def monitor_jobs():
    while True:
        if all(job['status'] == 'Complete' for job in job_progress):
            logging.debug("All jobs complete")
            break
        else:
            print ("Job Progress:")
            for job in job_progress:
                print (job['status'])
            threading.Event().wait(5)

def main():
    parser = argparse.ArgumentParser(description='Trasnfer data to from a file system to XNAT via DICOM Inbox.\nOptionally run data through DicomEdit.')
    parser.add_argument('-u', '--user', required=True, help='Target XNAT username')
    parser.add_argument('-p', '--password', required=True, help='XNAT password')
    parser.add_argument('--url', required=True, help='Target XNAT base URL')
    parser.add_argument('--project', required=True, help='Target XNAT project ID')
    parser.add_argument('-i', '--inbox', required=False, default='/data/xnat/input', help='Path to target DICOM Inbox directory root')
    parser.add_argument('--path_translation', required=False, help='Use to translate local paths to xnat container paths. e.g. /Users/Kelsey/Projects/XNAT/xnat-docker-compose/xnat-data:/data/xnat')
    parser.add_argument('-c', '--reface_csv', required=True, help='Path to Reface CSV file containing paths to refaced DICOM files')
    parser.add_argument('-r', '--remap_script_template', required=True, help='DicomEdit remap script')
    args = parser.parse_args()

    if not args.remap_script_template:
        logging.warning("No remap script template provided. Will not run data through DicomEdit.")

    xnat_inbox_path = args.inbox
    local_inbox_path = xnat_inbox_path
    if args.path_translation:
        local_path, xnat_path = args.path_translation.split(':')
        if not os.path.exists(local_path) or not xnat_path:
            logging.error(f"Invalid path translation: {args.path_translation}\n Exiting.")
            return
        local_inbox_path = xnat_inbox_path.replace(xnat_path, local_path)

    xnat = XNAT(base_url=args.url, username=args.user, password=args.password)

    dicom_edit = DicomEdit(remap_script_template=args.remap_script_template)

    #~ Read reface CSV file
    reface_csv = RefacePathCSV(args.reface_csv)
    #~ Iterate over rows in CSV
    all_row_count = reface_csv.get_all_row_count()
    passing_row_count = reface_csv.get_qc_pass_count()
    logging.debug(f'Found {passing_row_count}/{all_row_count} QC passing rows in CSV')

    #~ Check that all concat_ids are unique, since these are used as job identifiers
    if all_row_count != len(reface_csv.get_all_rows()['concat_id'].unique()):
        logging.error("concat_id values are not unique")
        raise Exception("concat_id values are not unique")


    try:
        while True:
            row = reface_csv.next_passing_row()
            if row is None:
                logging.debug("Finished processing passing rows in CSV")
                break
            logging.debug(f"Processing row: {row}")

            #~ Track progress by concat_id
            job_id = row['concat_id']
            logging.debug(f"Processing session_scan: {job_id}")

            #~ Add job to progress tracker
            with lock:
                job_progress[job_id] =JobStatus(job_id)

            #~ Check that row['Refaced_DICOM_URI'] is a directory
            if not os.path.isdir(row['Refaced_DICOM_URI']):
                logging.error(f"Refaced DICOM URI is not a directory: {row['Refaced_DICOM_URI']}")
                raise Exception("{} is not a directory".format(row['Refaced_DICOM_URI']))



            #~ Set up the DICOM Inbox job directory
            xnat_inbox_target = os.path.join(xnat_inbox_path, args.project, job_id)
            local_inbox_target = os.path.join(local_inbox_path, args.project, job_id)

            try:
                with lock:
                    job_progress[job_id].dicom_edit_status = 'Started'
                    job_progress[job_id].dicom_edit_target = local_inbox_target

                if os.path.exists(local_inbox_target):
                    logging.error(f"Files exist in target inbox directory: {local_inbox_target}")
                    raise Exception(f"Files exist in target inbox directory: {local_inbox_target}")
                else:
                    os.makedirs(local_inbox_target)

                #~ DicomEdit remap into DICOM Inbox job directory
                logging.debug(f"Remapping {row['Refaced_DICOM_URI']} to {local_inbox_target}")
                dicom_edit.remap(
                    src_dir=row['Refaced_DICOM_URI'],
                    dest_dir=local_inbox_target,
                    date_inc=row['days_shifted'],
                    patient_id=row['iCDKP_subject'],
                    patient_name=row['iCDKP_subject'],
                    session_label=row['iCDKP_session'],
                    series_description=row['Series Description'],
                    use_tilt=row['use_tilt']
                )
            except Exception as e:
                with lock:
                    job_progress[job_id].dicom_inbox_status = f"Error: {e}"

            # Check that job directory contains .dcm files
            if not glob.glob(os.path.join(local_inbox_target, '*.dcm')):
                logging.error(f"No .dcm files found in {local_inbox_target}")
                raise Exception(f"No .dcm files found in {local_inbox_target}")
            else:
                with lock:
                    job_progress[job_id].dicom_edit_status = 'Complete'

            #~ Post to XNAT DICOM Inbox
            logging.debug(f"Posting {xnat_inbox_target} to XNAT DICOM Inbox")
            response = xnat.post_to_inbox(
                project_id=args.project,
                subject_id=row['iCDKP_subject'],
                expt_label=row['iCDKP_session'],
                inbox_path=xnat_inbox_target
            )
            if(response.status_code == 200):
                with lock:
                    job_progress[job_id].dicom_inbox_status = 'Posted'
                    job_progress[job_id].dicom_inbox_id = response.text
            else:
                logging.error(f"Failed to post {xnat_inbox_target} to XNAT DICOM Inbox")
                logging.error(f"Response: {response.status_code}\n{parse_error_response(response)}")
                job_progress[job_id].dicom_inbox_status = f"Error: {parse_error_response(response)}"



    except StopIteration:
        logging.error("Exception raised when processing CSV rows")


    xnat.close()

def parse_error_response(response):
    if '<h3>' in response.text:
        match = re.search(r'<h3>(.*?)</h3>', response.text)
        if match:
            return match.group(1)
    return response.text

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=monitor_jobs)
    monitor_thread.daemon = True
    monitor_thread.start()
    main()

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)