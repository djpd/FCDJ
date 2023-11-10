FCDJ - File Cloner DJPools Detector
Description
FCDJ (File Cloner DJPools Detector) is a Python script designed to search for pairs of music files in a given directory based on specified conditions. It can identify clean and dirty versions of music files and perform various operations, including logging, removing, and autoremoving files.

Usage
Prerequisites
Python 3.x
Required Python packages (install using pip install -r requirements.txt):
tqdm
Configuration
Create a configuration file (e.g., config.cfg) to customize the script's behavior.
Modify the configuration parameters as needed. See the provided config.cfg file for an example.
Command Line Options
-base BASE: Specify the base folder for searching.
-output OUTPUT: Specify the output file to store valid pairs.
-config CONFIG: Specify the path to the config file.
-help: Show help message.
Example Usage
bash
Copy code
python fcdj.py -config config.cfg
Configuration File (config.cfg)
The configuration file allows you to customize various aspects of the script. Below are the key sections:

[GENERAL]
use_threadorpoolexecutor: Enable/disable the use of thread or pool executor.
buffer_size: Set the buffer size for processing files.
remove: Enable/disable file removal.
autoremove: Enable/disable autoremoval.
log: Enable/disable logging.
[BASE]
path: Specify the base folder with the music library.
[OUTPUT]
output_file: Specify the output file path to store valid pairs.
[PAIRx] (Replace x with a number)
clean_condition: Specify the clean condition for file matching.
dirty_condition: Specify the dirty condition for file matching.
[WHATAUTOREMOVE]
Specify conditions for autoremoval.
[LOG]
log_file: Specify the path for the log file.
Script Details
Script File (fcdj.py)
The script uses Python and various libraries for parallel processing and file manipulation.
The main functionality includes searching for pairs of music files, logging, and removing files based on specified conditions.
License
This script is licensed under the MIT License.

Make sure to replace the placeholders like LICENSE with the appropriate information. You may also want to include a license file if you haven't already.
