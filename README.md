
<b>FCDJ - File Cloner DJPools Detector 0.1 by DJ PD</b>
<br>
Overview
<br>
<br>
<b>
FCDJ is a script designed to detect pairs of files within a specified music library. It identifies clean and dirty versions of the same track based on user-defined conditions and can optionally remove the identified files.</b>
<br>
<br>

<b>Features</b><br>
<br>Parallel Processing: Utilizes multi-threading or multi-processing for efficient file processing.
<br>Configurable: Easily configurable through a dedicated configuration file (config.cfg).
<br>Logging: Provides logging functionality to record operations and results.
<br>
<br>
<br><b>Prerequisites</b>
<br>
Python 3.7 or higher
<br>
<br>
<b>Installation</b>
Clone the repository:<br>
<br>
Copy code
<br>
git clone https://github.com/yourusername/fcdj.git
<br>
cd fcdj
<br>
Install the required packages:
<br>
pip install -r requirements.txt
<br>
<br>
<b>Usage</b>
<br>python fcdj.py -config config.cfg<br>
<br>
<b>Command-line Arguments</b>
<br>
-base: Specify the base folder for searching (optional).<br>
-output: Specify the output file to store valid pairs (optional).<br>
-config: Specify the path to the config file (required).<br>
-help: Show the help message.<br><br>
<b>Configuration (config.cfg)</b>
<br>
<br>
The configuration file allows you to customize the behavior of the script.<br><br><br>

[GENERAL]
<br>
use_threadorpoolexecutor: Use multi-threading or multi-processing. Set to true for multi-threading, false for multi-processing.
<br>
buffer_size: Number of file pairs to buffer during processing.
<br>
remove: Enable/disable file removal based on conditions.
<br>
autoremove: Automatically remove files without user confirmation.
<br>
log: Enable/disable logging.
<br>
<br>
[BASE]<br>
path: Path to the base folder containing the music library.<br>
[OUTPUT]<br>
output_file: Path to the output file to store valid pairs.<br>
[PAIR1], [PAIR2], ...<br>
clean_condition: Clean file identifier condition.<br>
dirty_condition: Dirty file identifier condition.<br><br>
[WHATAUTOREMOVE]<br>
Specify conditions for files to be automatically removed.<br><br>

[LOG]<br>
log_file: Path to the log file.<br>
Examples<br>
For detailed examples, refer to the provided config.cfg file.<br>
<br>
License<br>
This project is licensed under the MIT License.<br>

Author<br>
DJPD<br>
<br>
requirements.txt
tqdm==4.62.3
