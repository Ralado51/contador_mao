# contador_mao

Browser prototype that counts open/close repetitions of a hand using the phone camera.
Everything runs on the device: video frames are processed in memory and discarded.
The page draws only the hand skeleton and keeps only derived events (repetition number,
duration, amplitude, model confidence). No image, video or raw landmark is stored or sent.

Part of an exploratory test for a "between sessions" reporting tool for occupational therapy.
This is a measurement prototype, not a medical device and not a clinical tool.

## Use

1. Open `index.html` over HTTPS (the camera API requires a secure context), for example with GitHub Pages.
2. Tap **Start**, keep the whole hand visible with good light, and open and close it.
3. Optional: tap **Calibrate (10 s)** and open/close the hand slowly to adapt thresholds to your range of motion.
4. **Download events** exports a JSON with events only.

For offline use, place `hand_landmarker.task` (MediaPipe Hand Landmarker model) next to `index.html`.
The page tries the local file first and falls back to the public model URL.

## How the count works

- `openness` = mean distance from the four fingertips to the wrist, divided by the wrist-to-middle-knuckle distance (about 2.0 open, about 1.0 fist).
- A small state machine (waiting, open, closed) with two thresholds (hysteresis) counts a repetition when the hand goes open, closed, open.
- Cycles shorter than 0.4 s or with small amplitude are ignored; losing the hand for more than 0.6 s discards the partial cycle.

## Tests

The counting logic is separate from the camera code and is tested on synthetic signals:

    node test_contador.js index.html

These tests check the logic only. Accuracy with real hands is measured separately by comparing the on-screen count with a manual count.

## Privacy check

The code uses no `MediaRecorder`, `toDataURL`, `toBlob` or `getImageData`. A counter on the page shows network requests made by the page after the camera starts; the browser network tab is the full check.
