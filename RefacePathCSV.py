import pandas as pd
import os


class RefacePathCSV:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.index = 0

    def next_row(self):
        if self.index < len(self.df):
            current_row_index = self.index
            self.index += 1
            return self.get_row(current_row_index)
        else:
            raise StopIteration("End of CSV file reached")

    def next_passing_row(self):
        while self.index < len(self.df):
            qc_result = self.df.iloc[self.index]['QC_result']
            self.index += 1
            if qc_result.lower() == 'pass':
                return self.get_row(self.index - 1)
        return None

    def reset(self):
        self.index = 0

    def get_row(self, index):
        if 0 <= index < len(self.df):
            row = self.df.iloc[index]
            return {
                'concat_id': row['concat_id'],
                'SNIPR_subject': row['SNIPR_subject'],
                'SNIPR_session': row['SNIPR_session'],
                'iCDKP_subject': row['iCDKP_subject'],
                'iCDKP_session': row['iCDKP_session'],
                'days_shifted': row['days_shifted'],
                'scan': row['scan'],
                'Series Description': row['Series Description'],
                'Image_Session_Id': row['Image Session ID'],
                'Refaced_DICOM_URI': os.path.dirname(row['Refaced DICOM URI']),
                'use_tilt': self._use_tilt(row)
            }
        else:
            raise IndexError("Index out of range")

    def get_all_rows(self):
        return self.df

    def get_all_row_count(self):
        return self.df.shape[0]

    def get_matching_row_count(self, column_name, value):
        return len(self.df[self.df[column_name].str.lower() == value.lower()])

    def get_qc_pass_count(self):
        return self.get_matching_row_count('QC_result', 'pass')

    def _use_tilt(self, row):
        return row['use_tilt_deface'] == 'yes'
