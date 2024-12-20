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

    def get_unique_sessions(self):
        get_passing_rows = self.get_passing_rows()
        return get_passing_rows['iCDKP_session'].unique()

    def get_scan_rows(self, session):
        matching_rows = self.df[self.df['iCDKP_session'] == session]
        return [self.get_row(index) for index in matching_rows.index]

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
                'iCDKP_subject': row['iCDKP_subject'],
                'iCDKP_session': row['iCDKP_session'],
                'iCDKP_scan': row['iCDKP_scan'],
                'days_shifted': row['days_shifted'],
                'Series Description': row['Series Description'],
                'Image_Session_Id': row['Image Session ID'],
                'source_path': row['source_path'],
                'use_tilt_deface': self._use_tilt(row)
            }
        else:
            raise IndexError("Index out of range")

    def get_all_rows(self):
        return self.df

    def get_all_row_count(self):
        return self.df.shape[0]

    def get_passing_rows(self):
        return self.df[self.df['QC_result'].str.lower() == 'pass']

    def get_matching_row_count(self, column_name, value):
        return len(self.df[self.df[column_name].str.lower() == value.lower()])

    def get_qc_pass_count(self):
        return self.get_matching_row_count('QC_result', 'pass')

    def _use_tilt(self, row):
        return row['use_tilt_deface'] == 'yes'
