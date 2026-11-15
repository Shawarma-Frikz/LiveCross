# Run_1003 Visual Camera 7 Projection Audit

**Audit date:** 15 November 2026  
**Decision:** 3D-to-image projection is possible from the supplied calibration chain, but projected boxes are **not validated for image-space evaluation** on this run/camera.

## Inputs and transform chain

- Ground truth: `data/raw/inspection/Run_1003_GT.csv`; 758 rows with 3D box centers, dimensions, and orientations in the LiDAR 2 reference frame.
- Video: `data/raw/inspection/VisualCamera7_Run_1003.mp4`; 1280×720, container-reported 30 FPS, 1,968 decoded frames.
- Frame timing: `data/raw/inspection/VisualCamera7_Run_1003_frame-timing.csv`; 1,968 rows. The first and last timestamps span 73.044 seconds. Mean interval is 37.135 ms (26.93 Hz), median 34.753 ms, minimum 5.451 ms, maximum 113.329 ms. Use these per-frame timestamps, not nominal FPS, for temporal alignment.
- Intrinsics/distortion: `CameraIntrinsicsv2.xlsx`, VisualCamera7 sheet in `metadata-and-supporting-docs.zip`. Intrinsics are reported at 1920×1080 and were scaled by 2/3 in both image axes for this 1280×720 MP4. Distortion values were used in OpenCV order `[k1, k2, p1, p2, k3]`.
- LiDAR-to-camera extrinsic: LiDAR2–VisualCamera6 calibration in `LidarCameraExtrinsicCalibResultsv2.xlsx`, reported mean reprojection error 3.89 pixels.
- Camera-to-camera extrinsic: VisualCamera6–VisualCamera7 calibration in `CameraCameraExtrinsicCalibResultsv2.xlsx`, reported mean reprojection error 0.50 pixels.
- GT UTC timestamps were matched to the camera timestamps interpreted as Eastern Standard Time (the recording date is in November); nearest GT and video times were compared rather than assuming constant frame rate.

## What was checked

The metadata defines the 18 road-user subclasses and states that GT boxes are expressed in the LiDAR 2 frame. The calibration files provide a chain into Visual Camera 7. The chain was applied to GT actor centers and cuboid corners, with the video-resolution correction and lens distortion included. Several timestamp-matched frames were inspected with projected overlays.

The resulting overlays did not reliably coincide with visible road users: examples place actor centers on apparently empty roadway or project boxes beyond the frame. This means the mathematical transform is available, but its usability for this camera/run has not been demonstrated.

## Decision and next action

Do **not** evaluate RGB detector boxes against these projected GT boxes for Run_1003 / Visual Camera 7. Keep the original GT in its LiDAR 2 coordinate frame. For RGB evaluation, use independently reviewed 2D annotations unless a later audit resolves the mismatch.

Possible causes still to investigate before reusing the projections include camera/GT visibility differences, frame correspondence, transform direction or calibration quality, and the exact semantics of GT dimensions/orientations. This audit does not claim which cause is responsible. Validate any proposed fix against multiple clearly visible actors and frames, including scenes where actor motion is evident.

## Roadmap outcome

Phase 01.2's requested decision—whether the chosen 3D boxes can be projected into the selected image and used there—is complete: **not approved as image-space ground truth at this stage**. This is a documented negative feasibility result, not a claim that the full DOT dataset cannot be projected with another camera or a corrected/validated calibration workflow.
