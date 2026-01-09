
1. Waveshare installation (Manually)
https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(B)_Manual_Configuration
display_rotate=2
Do touch calibration
2. Installation of apache2 and php
sudo apt install apache2 -y
sudo apt install php -y
###I stucked with Apache execution. SHC2.py was working fine from the local directories but atlast found the solution that works perfectly fine from Apache. 
Copying a virtual environment is generally not recommended. 😬
While it might seem like a quick fix, it often leads to problems because virtual environments contain hard-coded, absolute paths to their original location. When you copy the shc_env directory to a new location (like within Apache's web root), the internal scripts and binaries inside the virtual environment will still point back to the old path, causing the interpreter to fail.
The Problem with Copying

A virtual environment is more than just a folder of libraries. It's a structured directory that includes:
A copy or symlink of the Python interpreter.
The bin directory, which contains executable scripts (python, pip, etc.).
The lib or Lib directory, where installed packages live.
Crucially, these files often contain lines that refer to the environment's specific location, such as #! /home/pi/shc_env/bin/python. If you move the environment, these paths become invalid.###

The Recommended Solution

Instead of copying, the standard practice is to recreate the virtual environment in the new location. This ensures all paths are set correctly for the new environment. Here's a safe and reliable way to do it:
Generate a requirements.txt file from your existing environment. From your terminal, with shc_env activated, run this command to list all installed packages and their versions:
/home/pi/shc_env/bin/pip freeze > requirements.txt
Copying a virtual environment is generally not recommended. 😬
While it might seem like a quick fix, it often leads to problems because virtual environments contain hard-coded, absolute paths to their original location. When you copy the shc_env directory to a new location (like within Apache's web root), the internal scripts and binaries inside the virtual environment will still point back to the old path, causing the interpreter to fail.

Now i already have requirements.txt file on /var/www/html
2. Create a new virtual environment for Apache. As we discussed, it's best to create this in a location accessible by the www-data user, like /var/www/html/.
sudo -u www-data python3 -m venv /var/www/html/shc_env_apache
3. Install the packages from your requirements.txt file into the new environment. Copy the requirements.txt file to a location the www-data user can access (e.g., /var/www/html/). Then, run the installation command using the new environment's pip:
sudo -u www-data /var/www/html/shc_env_apache/bin/pip install -r /var/www/html/requirements.txt
4. Update your PHP script. Finally, change the $command variable in your PHP file to point to the new virtual environment's Python interpreter:
$command = "/var/www/html/shc_env_apache/bin/python /home/pi/Documents/Debjani/SHC/SHC2.py ...";
pi@raspberrypi:~/Documents/Debjani $ mkdir Soil
pi@raspberrypi:~/Documents/Debjani $ mkdir Farmer
pi@raspberrypi:~/Documents/Debjani $ cd Farmer
pi@raspberrypi:~/Documents/Debjani/Farmer $ sudo touch farmer_details.csv
pi@raspberrypi:~/Documents/Debjani/Farmer $ cd ..
pi@raspberrypi:~/Documents/Debjani $ mkdir SHC
pi@raspberrypi:~/Documents/Debjani $ cd SHC
pi@raspberrypi:~/Documents/Debjani/SHC $ sudo mkdir Archive_SHC
pi@raspberrypi:~/Documents/Debjani/SHC $ cd ..
pi@raspberrypi:~/Documents/Debjani $ touch testing.csv
pi@raspberrypi:~/Documents/Debjani $ cd SHC
pi@raspberrypi:~/Documents/Debjani/SHC $ touch error_log.txt
 
here’s the one-liner that sets everything up so both you (pi) and Apache (www-data) can access the files, and new files will keep the same group automatically:
sudo usermod -a -G www-data pi && sudo chown -R pi:www-data /home/pi && sudo chmod -R 775 /home/pi && sudo chmod g+s /home/pi
What it does in sequence:
usermod -a -G www-data pi → adds you to Apache’s group.


chown -R pi:www-data → makes you the owner, group is www-data.


chmod -R 775 → lets owner & group read/write/execute.


chmod g+s → ensures future files inherit the same group.


⚠ Important: After running it, you must log out and back in (or restart the shell) for the group change to apply.



//Code (submitImproved1.php)
//submitImproved1.php
$photo_path = '/home/pi/Documents/Debjani/Soil/';
$csv_aggregate_path = '/home/pi/Documents/Debjani/Farmer/farmer_details.csv';
$csv_individual_dir = '/home/pi/Documents/Debjani/Farmer/';
$python_script = '/home/pi/Documents/Debjani/SHC/SHC2.py';
$pdf_output_dir = '/var/www/html/';
$pdf_archive_dir = '/home/pi/Documents/Debjani/SHC/Archive_SHC/';
$testing_csv = '/home/pi/Documents/Debjani/testing.csv';

//Soil health card name 
$pdf_filename = "SoilHealthCard_" . $sanitized_name . "_" . $survey_no . "_" . $timestamp . ".pdf";
//photo upload
$destination = $photo_path . $unique_photo_name;
$unique_photo_name = $survey_no . "_" . $timestamp . "." . $photo_ext;
$photo_path = '/home/pi/Documents/Debjani/Soil/';
// Log the error for debugging
/home/pi/Documents/Debjani/SHC/error_log.txt
 // Define the source and archive PDF paths
    $source_pdf = $pdf_output_dir . $pdf_filename;
    $archive_pdf = $pdf_archive_dir . $sanitized_name . "_" . $survey_no . "_SoilHealthCard_" . $timestamp . ".pdf";
    
//cron job
@reboot export DISPLAY=:0 && /home/pi/Documents/Debjani/start.sh >> /home/pi/logfile.log 2>&1
*/30 * * * * rclone copy /home/pi/Documents/Debjani/ mdrive:/SoilEye_Jan2025/
*/35 * * * * rclone copy /var/www/ mdrive:/SoilEye_Jan2025/

//I2C Interface enabled for raspi to get battery updation
sudo raspi-config 
then enable I2C
//Install smbus
sudo apt-get update
sudo apt-get install -y python3-smbus i2c-tools

//VNC server to enable via 
sudo raspi-config


​
