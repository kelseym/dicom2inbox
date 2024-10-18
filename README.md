# dicom2inbox scripts 
These scripts are used to move XNAT session DICOM files from a ingestion project to a processing project. Each DICOM file is remapped and renamed according to a csv file and remap template.

## Usage:
```bash
python src/dicom2inbox.py  [-h] -u USER [-p PASSWORD] --url URL --project PROJECT [-i INBOX] [--path_translation PATH_TRANSLATION] -c REFACE_CSV -r REMAP_SCRIPT_TEMPLATE [-o OUTPUT] [-v]

```
The following arguments are required: -u/--user, --url, --project, -r/--remap_script_template

## Options:
* -h, --help            show this help message and exit
*  -u or --user USER  Target : XNAT username
*  -p or --password PASSWORD : XNAT password. Use XNAT token or repond to password prompt in interactive mode
*  --url URL                 : Target XNAT base URL. e.g. https://snipr.xnat.org
*  --project PROJECT         : Target XNAT project ID
*  -i or --inbox INBOX       : Path to target DICOM Inbox directory root. e.g. /data/xnat/inbox
*  --path_translation PATH_TRANSLATION : Use to translate local paths to xnat container paths. e.g. /Users/Kelsey/Projects/XNAT/xnat-docker-compose/xnat-data:/data/xnat
*  -c or --reface_csv REFACE_CSV : Path to Reface CSV file containing paths to refaced DICOM files
*  -r or --remap_script_template REMAP_SCRIPT_TEMPLATE : DicomEdit remap script. Defaults to ./dicomedit/snipr_remap_template.txt
*  -o OUTPUT, --output OUTPUT : Path to output report csv file.
*  -v, --verbose              : Enable verbose logging


## Reface CSV:
** Each XNAT scan resource of interest is specified by a row in a csv file (e.g. SNIPR_reface_paths.csv) with the following required columns:
* 'QC_result' : Pass|Fail. Only 'Pass' rows will be processed
* 'concat_id' : Unique identifier for each source scan row in the CSV
* 'Refaced_DICOM_URI' : Full file path to the catalog file under a resource of interest
* 'days_shifted' : Number of days to shift the session date on transfer
* 'iCDKP_subject' : iCDKP subject label. Used for patient name and patient ID in anonymization
* 'iCDKP_session' : iCDKP session label. Used for accession number in anonymization
* 'iCDKP_scan' : iCDKP scan label. Used for series number in anonymization
* 'Series Description' : Series description. Used for series description in anonymization
* 'use_tilt' : If 'yes', use only DICOM files containing 'tilt' or 'Tilt' in the file name. Otherwise, use DICOM files without 'tilt|Tilt' in the file name.



