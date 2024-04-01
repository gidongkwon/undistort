import numpy as np
import cv2 as cv

def select_img_from_video(video_file, board_pattern, total_select_count=-1, wait_msec=10, wnd_name='Camera Calibration'):
    # Open a video
    video = cv.VideoCapture(video_file)
    assert video.isOpened()

    video_length = int(video.get(cv.CAP_PROP_FRAME_COUNT))

    # Select images
    img_select = []
    current_frame = 0
    while True:
        # Grab an images from the video
        valid, img = video.read()
        if not valid:
            break

        if total_select_count != -1:
            every_n = max(int(video_length / total_select_count), 1)
            if (current_frame != 0) and (current_frame % every_n) == 0:
              img_select.append(img)
              print(f'Adding frame: {current_frame} / {video_length}')
        else:
            # Show the image
            display = img.copy()
            cv.putText(display, f'Selected N: {len(img_select)}', (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))
            cv.imshow(wnd_name, display)

            # Process the key event
            key = cv.waitKey(wait_msec)
            if key == ord(' '):             # Space: Pause and show corners
                complete, pts = cv.findChessboardCorners(img, board_pattern)
                cv.drawChessboardCorners(display, board_pattern, pts, complete)
                cv.imshow(wnd_name, display)
                key = cv.waitKey()
                if key == ord('\r'):
                    img_select.append(img) # Enter: Select the image
            if key == 27:                  # ESC: Exit (Complete image selection)
                break
        
        current_frame += 1

    cv.destroyAllWindows()
    return img_select

def calib_camera_from_chessboard(images, board_pattern, board_cellsize, K=None, dist_coeff=None, calib_flags=None):
    # Find 2D corner points from given images
    img_points = []
    for index, img in enumerate(images):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)
        if complete:
            print(f'Finding chessboard corners: {index + 1} / {len(images)}')
            img_points.append(pts)
    assert len(img_points) > 0

    # Prepare 3D points of the chess board
    obj_pts = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_points = [np.array(obj_pts, dtype=np.float32) * board_cellsize] * len(img_points) # Must be `np.float32`

    print('Calibrating camera...')

    # Calibrate the camera
    return cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], K, dist_coeff, flags=calib_flags)

if __name__ == '__main__':
    video_file = './data/chessboard_2x2.mp4'
    board_pattern = (9, 7)
    board_cellsize = 0.02

    img_select = select_img_from_video(video_file, board_pattern, 40)
    assert len(img_select) > 0, 'There is no selected images!'
    rms, K, dist_coeff, rvecs, tvecs = calib_camera_from_chessboard(img_select, board_pattern, board_cellsize)

    # Print calibration results
    print('## Camera Calibration Results')
    print(f'* The number of selected images = {len(img_select)}')
    print(f'* RMS error = {rms}')
    print(f'* Camera matrix (K) = \n{K}')
    print(f'* Distortion coefficient (k1, k2, p1, p2, k3, ...) = {dist_coeff.flatten()}')