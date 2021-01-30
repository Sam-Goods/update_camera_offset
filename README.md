Run the update_camera_offset.py script in the root directory to snap the alignment.
When running the script ensure that the correct subject name is entered using the argument 
"--propname <Subject>" 

This script will:

1. Export XCP from Shogun Live to the current capture directory
2. Export VSK for the input subject name
3. Get a pose from the Datastream for the input subject
4. Align the markers in the VSK to the calibrated SDI camera
5. Re-import the aligned VSK