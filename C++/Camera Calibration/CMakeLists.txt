# CMake Bulid File
#
# CMake Version
cmake_minimum_required(VERSION 3.12)

# Compiler Settings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(OPENCV_EXTRA_MODULES_PATH ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv_contrib/modules)

add_subdirectory(ThirdParty/opencv)

# Set the project name
project(CameraCalibration)

add_executable(
	CameraCalibration
	${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)

target_include_directories(
	CameraCalibration
	PUBLIC
	${CMAKE_CURRENT_BINARY_DIR}
	${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/include
	${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/calib3d/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/core/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudaarithm/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudabgsegm/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudacodec/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudafeatures2d/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudafilters/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudaimgproc/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudalegacy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudaobjdetect/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudaoptflow/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudastereo/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudawarping/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/cudev/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/dnn/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/features2d/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/flann/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/highgui/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/imgcodecs/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/imgproc/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/ml/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/objdetect/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/photo/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/shape/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/stitching/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/superres/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/ts/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/video/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/videoio/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/videostab/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/viz/include
    ${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv/modules/world/include

	${CMAKE_CURRENT_SOURCE_DIR}/ThirdParty/opencv_contrib/modules/aruco/include

)

target_link_libraries(
	CameraCalibration
	PRIVATE
	opencv_core
	opencv_objdetect
	opencv_calib3d
	opencv_highgui
	opencv_aruco
)