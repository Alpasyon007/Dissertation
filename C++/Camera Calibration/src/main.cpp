// std
#include <iostream>
#include <vector>

// Windows
#include <Windows.h>
#include <commdlg.h>
#include <shlobj.h> // Include this header for BROWSEINFO

// OpenCV
#include <opencv2/aruco/charuco.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

namespace {
	const char* about = "Calibration using a ChArUco board\n"
						"  To capture a frame for calibration, press 'c',\n"
						"  If input comes from video, press any key for next frame\n"
						"  To finish capturing, press 'ESC' key and calibration starts.\n";
	const char* keys  = "{w        |       | Number of squares in X direction }"
						"{h        |       | Number of squares in Y direction }"
						"{sl       |       | Square side length (in meters) }"
						"{ml       |       | Marker side length (in meters) }"
						"{d        |       | dictionary: DICT_4X4_50=0, DICT_4X4_100=1, DICT_4X4_250=2,"
						"DICT_4X4_1000=3, DICT_5X5_50=4, DICT_5X5_100=5, DICT_5X5_250=6, DICT_5X5_1000=7, "
						"DICT_6X6_50=8, DICT_6X6_100=9, DICT_6X6_250=10, DICT_6X6_1000=11, DICT_7X7_50=12,"
						"DICT_7X7_100=13, DICT_7X7_250=14, DICT_7X7_1000=15, DICT_ARUCO_ORIGINAL = 16}"
						"{cd       |       | Input file with custom dictionary }"
						"{@outfile |<none> | Output file with calibrated camera parameters }"
						"{v        |       | Input from video file, if ommited, input comes from camera }"
						"{ci       | 0     | Camera id if input doesnt come from video (-v) }"
						"{dp       |       | File of marker detector parameters }"
						"{rs       | false | Apply refind strategy }"
						"{zt       | false | Assume zero tangential distortion }"
						"{a        |       | Fix aspect ratio (fx/fy) to this value }"
						"{pc       | false | Fix the principal point at the center }"
						"{sc       | false | Show detected chessboard corners after calibration }";
} // namespace

inline static bool saveCameraParams(const std::string& filename, cv::Size imageSize, float aspectRatio, int flags, const cv::Mat& cameraMatrix,
									const cv::Mat& distCoeffs, double totalAvgErr) {
	cv::FileStorage fs(filename, cv::FileStorage::WRITE);
	if(!fs.isOpened()) return false;

	time_t tt;
	time(&tt);
	struct tm* t2 = localtime(&tt);
	char	   buf[1024];
	strftime(buf, sizeof(buf) - 1, "%c", t2);

	fs << "calibration_time" << buf;
	fs << "image_width" << imageSize.width;
	fs << "image_height" << imageSize.height;

	if(flags & cv::CALIB_FIX_ASPECT_RATIO) fs << "aspectRatio" << aspectRatio;

	if(flags != 0) {
		sprintf(buf, "flags: %s%s%s%s", flags & cv::CALIB_USE_INTRINSIC_GUESS ? "+use_intrinsic_guess" : "",
				flags & cv::CALIB_FIX_ASPECT_RATIO ? "+fix_aspectRatio" : "", flags & cv::CALIB_FIX_PRINCIPAL_POINT ? "+fix_principal_point" : "",
				flags & cv::CALIB_ZERO_TANGENT_DIST ? "+zero_tangent_dist" : "");
	}
	fs << "flags" << flags;
	fs << "camera_matrix" << cameraMatrix;
	fs << "distortion_coefficients" << distCoeffs;
	fs << "avg_reprojection_error" << totalAvgErr;
	return true;
}

#include <fstream>
#include <sstream>

#include <fstream>
#include <sstream>

std::vector<cv::Vec3f> readLightDirectionsFromFile(const std::string& filename) {
	std::vector<cv::Vec3f> lightDirs;

	std::ifstream		   inputFile(filename);
	if(!inputFile.is_open()) { throw std::runtime_error("Unable to open file " + filename); }

	std::string line;
	while(std::getline(inputFile, line)) {
		std::istringstream iss(line);
		float			   x, y, z;
		if(!(iss >> x >> y >> z)) { throw std::runtime_error("Invalid line in file " + filename + ": " + line); }
		lightDirs.push_back(cv::Vec3f(x, y, z));
	}

	return lightDirs;
}

void writeLightDirectionsToFile(const std::string& filename, const std::vector<cv::Vec3f>& lightDirs) {
	std::ofstream outputFile(filename);
	if(!outputFile.is_open()) { throw std::runtime_error("Unable to open file " + filename); }

	std::ostream_iterator<std::string> outputIterator(outputFile, "\n");
	std::transform(lightDirs.begin(), lightDirs.end(), outputIterator, [](const cv::Vec3f& v) -> std::string {
		std::ostringstream oss;
		oss << v[0] << ' ' << v[1] << ' ' << v[2];
		return oss.str();
	});
}

std::vector<cv::Mat> LoadImagesFromFolderDialog() {
	// Initialize the BROWSEINFO structure
	BROWSEINFO bi	  = {0};
	bi.lpszTitle	  = "Select a folder";
	LPITEMIDLIST pidl = SHBrowseForFolder(&bi);
	if(pidl == nullptr) {
		// User clicked Cancel
		return std::vector<cv::Mat>();
	}
	// Get the path to the selected folder
	TCHAR path[MAX_PATH];
	if(SHGetPathFromIDList(pidl, path) == FALSE) {
		// Error getting folder path
		return std::vector<cv::Mat>();
	}
	// Free the PIDL memory
	CoTaskMemFree(pidl);
	// Load all the images in the folder into a vector
	std::vector<cv::Mat> images;
	WIN32_FIND_DATA		 fileData;
	HANDLE				 hFind = FindFirstFile((std::string(path) + "\\*.*").c_str(), &fileData);
	if(hFind != INVALID_HANDLE_VALUE) {
		do {
			if(fileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
				// Ignore directories
				continue;
			}
			std::string filename = std::string(path) + "\\" + fileData.cFileName;
			cv::Mat		image	 = cv::imread(filename);
			if(!image.empty()) { images.push_back(image); }
		} while(FindNextFile(hFind, &fileData) != 0);
		FindClose(hFind);
	}
	return images;
}

int main(int argc, char* argv[]) {
	CommandLineParser parser(argc, argv, keys);
	parser.about(about);

	int	   squaresX				 = 8;
	int	   squaresY				 = 8;
	float  squareLength			 = 0.04f;
	float  markerLength			 = 0.02f;
	string outputFile			 = "C:\\Users\\Alpas\\OneDrive\\Desktop\\out.txt";

	bool   showChessboardCorners = true;

	int	   calibrationFlags		 = 0;
	float  aspectRatio			 = 1;
	if(parser.has("a")) {
		calibrationFlags |= CALIB_FIX_ASPECT_RATIO;
		aspectRatio = parser.get<float>("a");
	}
	if(parser.get<bool>("zt")) calibrationFlags |= CALIB_ZERO_TANGENT_DIST;
	if(parser.get<bool>("pc")) calibrationFlags |= CALIB_FIX_PRINCIPAL_POINT;

	Ptr<aruco::DetectorParameters> detectorParams = makePtr<aruco::DetectorParameters>();
	if(parser.has("dp")) {
		FileStorage fs(parser.get<string>("dp"), FileStorage::READ);
		bool		readOk = detectorParams->readDetectorParameters(fs.root());
		if(!readOk) {
			cerr << "Invalid detector parameters file" << endl;
			return 0;
		}
	}

	bool					 refindStrategy = parser.get<bool>("rs");
	int						 camId			= parser.get<int>("ci");

	aruco::Dictionary		 dictionary		= cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);

	// create charuco board object
	Ptr<aruco::CharucoBoard> charucoboard	= new aruco::CharucoBoard(Size(squaresX, squaresY), squareLength, markerLength, dictionary);
	Ptr<aruco::Board>		 board			= charucoboard.staticCast<aruco::Board>();

	cv::Mat					 boardImage;
	board->generateImage(cv::Size(800, 800), boardImage, 10, 1);
	cv::imshow("Charuco Board", boardImage);

	// collect data from each frame
	vector<vector<vector<Point2f>>> allCorners;
	vector<vector<int>>				allIds;
	vector<Mat>						allImgs;
	Size							imgSize;

	cv::Mat							imageCopy;
	vector<Mat>						images = LoadImagesFromFolderDialog();

	if(images.empty()) {
		cerr << "Cannot open image file" << endl;
		return 0;
	}

	for(auto image : images) {
		vector<int>				ids;
		vector<vector<Point2f>> corners, rejected;
		cv::resize(image, image, cv::Size(), 0.20, 0.20);

		// detect markers
		aruco::detectMarkers(image, makePtr<aruco::Dictionary>(dictionary), corners, ids, detectorParams, rejected);

		// refind strategy to detect more markers
		if(refindStrategy) aruco::refineDetectedMarkers(image, board, corners, ids, rejected);

		// interpolate charuco corners
		Mat currentCharucoCorners, currentCharucoIds;
		if(ids.size() > 0) aruco::interpolateCornersCharuco(corners, ids, image, charucoboard, currentCharucoCorners, currentCharucoIds);

		// draw results
		image.copyTo(imageCopy);
		if(ids.size() > 0) aruco::drawDetectedMarkers(imageCopy, corners);

		if(currentCharucoCorners.total() > 0) aruco::drawDetectedCornersCharuco(imageCopy, currentCharucoCorners, currentCharucoIds);

		putText(imageCopy, "Press 'c' to add current frame. 'ESC' to finish and calibrate", Point(10, 20), FONT_HERSHEY_SIMPLEX, 0.5, Scalar(255, 0, 0), 2);

		// imshow("out", imageCopy);
		// char key = (char)waitKey(10);
		if(ids.size() > 0) {
			cout << "Image Captured" << endl;
			allCorners.push_back(corners);
			allIds.push_back(ids);
			allImgs.push_back(image);
			imgSize = image.size();
		}
	}

	Mat			cameraMatrix, distCoeffs;
	vector<Mat> rvecs, tvecs;
	double		repError;

	if(calibrationFlags & CALIB_FIX_ASPECT_RATIO) {
		cameraMatrix				  = Mat::eye(3, 3, CV_64F);
		cameraMatrix.at<double>(0, 0) = aspectRatio;
	}

	// prepare data for calibration
	vector<vector<Point2f>> allCornersConcatenated;
	vector<int>				allIdsConcatenated;
	vector<int>				markerCounterPerFrame;
	markerCounterPerFrame.reserve(allCorners.size());
	for(unsigned int i = 0; i < allCorners.size(); i++) {
		markerCounterPerFrame.push_back((int)allCorners[i].size());
		for(unsigned int j = 0; j < allCorners[i].size(); j++) {
			allCornersConcatenated.push_back(allCorners[i][j]);
			allIdsConcatenated.push_back(allIds[i][j]);
		}
	}

	// calibrate camera using aruco markers
	double arucoRepErr;
	arucoRepErr = aruco::calibrateCameraAruco(allCornersConcatenated, allIdsConcatenated, markerCounterPerFrame, board, imgSize, cameraMatrix, distCoeffs,
											  noArray(), noArray(), calibrationFlags);

	// prepare data for charuco calibration
	int			nFrames = (int)allCorners.size();
	vector<Mat> allCharucoCorners;
	vector<Mat> allCharucoIds;
	vector<Mat> filteredImages;
	allCharucoCorners.reserve(nFrames);
	allCharucoIds.reserve(nFrames);

	for(int i = 0; i < nFrames; i++) {
		// interpolate using camera parameters
		Mat currentCharucoCorners, currentCharucoIds;
		aruco::interpolateCornersCharuco(allCorners[i], allIds[i], allImgs[i], charucoboard, currentCharucoCorners, currentCharucoIds, cameraMatrix,
										 distCoeffs);

		allCharucoCorners.push_back(currentCharucoCorners);
		allCharucoIds.push_back(currentCharucoIds);
		filteredImages.push_back(allImgs[i]);
	}

	// calibrate camera using charuco
	repError = aruco::calibrateCameraCharuco(allCharucoCorners, allCharucoIds, charucoboard, imgSize, cameraMatrix, distCoeffs, rvecs, tvecs, calibrationFlags);

	bool saveOk = saveCameraParams(outputFile, imgSize, aspectRatio, calibrationFlags, cameraMatrix, distCoeffs, repError);
	if(!saveOk) {
		cerr << "Cannot save output file" << endl;
		return 0;
	}

	cv::Scalar color = cv::Scalar(255, 0, 0);
	Mat		   image;
	cv::resize(images[0], image, cv::Size(), 0.20, 0.20);
	cv::aruco::drawDetectedCornersCharuco(image, allCharucoCorners[0], allCharucoIds[0], color);
	cv::Vec3d rvec, tvec;
	bool	  valid = cv::aruco::estimatePoseCharucoBoard(allCharucoCorners[0], allCharucoIds[0], charucoboard, cameraMatrix, distCoeffs, rvec, tvec);
	// if charuco pose is valid
	if(valid) {
		// Print the camera's position and orientation
		cout << "Camera position:" << endl << tvec << endl;
		cout << "Camera orientation:" << endl << rvec << endl;

		cv::drawFrameAxes(image, cameraMatrix, distCoeffs, rvec, tvec, 0.1f);
		cv::imshow("Frame Axes", image);
	} else {
		throw;
	}

	// Assume you have a list of light directions in the charuco board coordinate system
	std::vector<cv::Vec3f> charucoLightDirs = readLightDirectionsFromFile("Y:\\Dissertation\\Python Scripts\\directions.txt");

	// Get the transformation matrix from charuco board to camera
	cv::Mat				   rotationMatrix;
	cv::Rodrigues(rvec, rotationMatrix);
	cv::Mat transformMatrix = cv::Mat::eye(4, 4, CV_64FC1);
	rotationMatrix.copyTo(transformMatrix(cv::Rect(0, 0, 3, 3)));
	transformMatrix.at<double>(3, 0) = tvec[0];
	transformMatrix.at<double>(3, 1) = tvec[1];
	transformMatrix.at<double>(3, 2) = tvec[2];

	// Transform light directions to camera coordinate system
	std::vector<cv::Vec3f> cameraLightDirs(charucoLightDirs.size());
	for(int i = 0; i < charucoLightDirs.size(); i++) {
		cv::Vec4f charucoLightDir4(charucoLightDirs[i][0], charucoLightDirs[i][1], charucoLightDirs[i][2],
								   0.0f); // Note the change to 0.0f for the fourth component
		cv::Mat	  charucoLightDirMat = cv::Mat::eye(1, 4, CV_64FC1);
		charucoLightDirMat.row(0)	 = cv::Mat(charucoLightDir4);
		cv::Mat	  cameraLightDirMat	 = transformMatrix * charucoLightDirMat.t();
		cv::Vec3f cameraLightDir3(cameraLightDirMat.at<double>(0, 0), cameraLightDirMat.at<double>(1, 0), cameraLightDirMat.at<double>(2, 0));
		cameraLightDirs[i] = cameraLightDir3;
	}

	writeLightDirectionsToFile("Y:\\Dissertation\\Python Scripts\\directions.txt", cameraLightDirs);

	cout << "Rep Error: " << repError << endl;
	cout << "Rep Error Aruco: " << arucoRepErr << endl;
	cout << "Calibration saved to " << outputFile << endl;

	// // show interpolated charuco corners for debugging
	// if(showChessboardCorners) {
	// 	for(unsigned int frame = 0; frame < filteredImages.size(); frame++) {
	// 		Mat imageCopy = filteredImages[frame].clone();
	// 		if(allIds[frame].size() > 0) {

	// 			if(allCharucoCorners[frame].total() > 0) { aruco::drawDetectedCornersCharuco(imageCopy, allCharucoCorners[frame], allCharucoIds[frame]); }
	// 		}

	// 		imshow("out", imageCopy);
	// 		char key = (char)waitKey(0);
	// 		if(key == 27) break;
	// 	}
	// }

	return 0;
}