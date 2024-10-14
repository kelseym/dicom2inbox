import subprocess
import re
import os
import tempfile


class DicomEdit:
    def __init__(self, remap_script_template=None, jar_path='./dicomedit/dicom-edit6-6.6.0-jar-with-dependencies.jar'):
        self.jar_path = jar_path
        self.remap_script_template = remap_script_template

    def remap(self, src_dir, dest_dir, date_inc, patient_id, patient_name, session_label, series_description, use_tilt=False):
        if self.remap_script_template is None:
            raise Exception("No remap script template provided")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_script = self.populate_remap_script(tmp_dir, date_inc, patient_id, patient_name, session_label, series_description)
            self.run_on_dir(tmp_script, src_dir, dest_dir, use_tilt)

    def populate_remap_script(self, tmp_dir, data_inc, patient_id, patient_name, session_label, series_description):
        if self.remap_script_template is None:
            raise Exception("No remap script template provided")
        # create a temporary file to hold the remap script
        tmp_script_path = os.path.join(tmp_dir, 'remap_script.txt')
        replacements = {
            '#DATE_INC#': str(data_inc),
            '#PATIENT_ID#': str(patient_id),
            '#PATIENT_NAME#': str(patient_name),
            '#ACCESSION_NUMBER#': str(session_label),
            '#SERIES_DESCRIPTION#': str(series_description)
        }
        self.replace_patterns_in_file(self.remap_script_template, tmp_script_path, replacements)
        return tmp_script_path

    def replace_patterns_in_file(self, input_path, output_path, replacements):
        with open(input_path, 'r') as file:
            content = file.read()
        for pattern, replacement in replacements.items():
            content = content.replace(pattern, replacement)
        with open(output_path, 'w') as file:
            file.write(content)

    def run_on_dir(self, script_path, src_dir, dest_dir, use_tilt=False):
        processes = []
        for filename in os.listdir(src_dir):
            if (use_tilt and not re.search(r'(Tilt|tilt)', filename)) \
                    or (not use_tilt and re.search(r'(Tilt|tilt)', filename)):
                continue
            src_file = os.path.join(src_dir, filename)
            if not os.path.isfile(src_file):
                raise Exception(f"File not found: {src_file}. Halting directory processing.")
            # start a process for each file in the directory
            processes.append(self.run_async(script_path, src_file, dest_dir))

            # now wait for all the processes to finish
        for process in processes:
            process.wait()
            if process.returncode != 0:
                raise Exception(f"Error running DicomEdit: {process.stdout} \n {process.stderr}")
        return True


    def run_async(self, script_path, input_file, output_dir):
        command = [
            'java', '-jar', self.jar_path,
            '-s', script_path,
            '-i', input_file,
            '-o', output_dir
        ]
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

