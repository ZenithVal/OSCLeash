import openvr
import time
# from ctypes import *

# Initialize the OpenVR system
openvr.init(openvr.VRApplication_Utility)

# Create a VRChaperoneSetup object
chaperone_setup = openvr.VRChaperoneSetup()
chaperone = openvr.VRChaperone()



#chaperone_setup.reloadFromDisk(openvr.EChaperoneConfigFile_Live)
while True:
    #chaperone_setup.hideWorkingSetPreview()
    # Get the transformation matrix mapping the standing zero pose to the raw tracking pose
    chaperone_setup.revertWorkingCopy()
    standing_zero_to_raw_tracking_pose = chaperone_setup.getWorkingStandingZeroPoseToRawTrackingPose()
    #standing_zero_to_raw_tracking_pose = chaperone_setup.get

    # Get the actual matrix from the tuple
    pose = standing_zero_to_raw_tracking_pose[1]

    print(f"Old Pose: {pose}")
    # Print the first row of the transformation matrix

    pose[1][0] += 0
    pose[1][1] += 0
    pose[1][2] += 0
    # Bingo
    pose[1][3] += -0.1


    #print(pose)
    #new_matrix = (standing_zero_to_raw_tracking_pose[0], pose)
    chaperone_setup.setWorkingStandingZeroPoseToRawTrackingPose(pose)
    chaperone_setup.commitWorkingCopy(openvr.EChaperoneConfigFile_Live)
    print(f"New Pose: {pose}")
    time.sleep(5)
# Clean up and shutdown the OpenVR system
openvr.shutdown()