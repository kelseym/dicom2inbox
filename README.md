# dicom2inbox scripts 
These scripts are used to move XNAT session DICOM files from a ingestion project to a processing project

where
*Each XNAT scan resource of interest is specified by a row in a csv file (e.g. SNIPR_reface_paths.csv) with the following columns:
scan: XNAT scan label
Image Session Id: XNAT session ID
Refaced DICOM URI: Full file path to the catalog file under a resource of interest
QC_Result: Pass/Fail
SNIPR_subject: XNAT subject label
SNIPR_session: XNAT session accession number
iCDKP_subject: iCDKP subject label
iCDKP_session: iCDKP session label
days_shifted: Number of days to shift the session date on transfer

A directory of DICOM files, specified in the reface_csv, is copied from a specified path to a dicom inbox target
 If specified, DicomEdit remaps the DICOM files to a new subject and date shift according to the reface_csv before moving them to the dicom inbox target


