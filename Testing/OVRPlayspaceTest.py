import openvr
# from ctypes import *

# Initialize the OpenVR system
openvr.init(openvr.VRApplication_Utility)

# Create a VRChaperoneSetup object
chaperone_setup = openvr.VRChaperoneSetup()
chaperone = openvr.VRChaperone()


#chaperone_setup.hideWorkingSetPreview()

#chaperone_setup.reloadFromDisk(openvr.EChaperoneConfigFile_Live)

# Get the transformation matrix mapping the standing zero pose to the raw tracking pose
standing_zero_to_raw_tracking_pose = chaperone_setup.getWorkingStandingZeroPoseToRawTrackingPose()

# Get the actual matrix from the tuple
pose = standing_zero_to_raw_tracking_pose[1]

print(pose)
# Print the first row of the transformation matrix

pose[1][0] += 0
pose[1][1] += 0
pose[1][2] += 0
# Bingo
pose[1][3] += -1


print(pose)
#new_matrix = (standing_zero_to_raw_tracking_pose[0], pose)
chaperone_setup.setWorkingStandingZeroPoseToRawTrackingPose(pose)

chaperone_setup.commitWorkingCopy(openvr.EChaperoneConfigFile_Live)
# Clean up and shutdown the OpenVR system
openvr.shutdown()