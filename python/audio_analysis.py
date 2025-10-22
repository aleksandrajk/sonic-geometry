"""
Realtime audio feature extraction for Sonic Geometry.
Captures audio, computes FFT bands, RMS, spectral centroid and onsets (via aubio).
Sends results to an OSC sender function (callable) which you can implement in "osc_sender.py".
"""

import json
import time
import queue
import argparse
import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq

try:
    import aubio
    AUBIO_AVAILABLE = True
except Exception:
    AUBIO_AVAILABLE = False

# Helper to compute band energies (log-spaced or mel-like)

def _make_log_bands(n_bins, fft_size, sr, fmin=20, fmax=None):
    if fmax is None:
        fmax = sr / 2
    freqs = np.geomspace(fmin, fmax, n_bins + 1)
    fft_freqs = rfftfreq(fft_size, 1 / sr)
    band_bins = []
    for i in range(n_bins):
        low_f, high_f = freqs[i], freqs[i + 1]
        idx = np.where((fft_freqs >= low_f) & (fft_freqs < high_f))[0]
        if idx.size == 0:
            idx = np.array([i])
        band_bins.append(idx)
    return band_bins


class AudioAnalyzer:
    def __init__(self, samplerate=44100, blocksize=1024, bands=12, osc_callback=None):
        self.sr = samplerate
        self.block = blocksize
        self.bands = bands
        self.q = queue.Queue()
        self.fft_size = blocksize
        self.band_bins = _make_log_bands(bands, self.fft_size, samplerate)
        self.osc_callback = osc_callback

        if AUBIO_AVAILABLE:
            self._onset = aubio.onset(method='default', buf_size=self.fft_size, hop_size=self.block, samplerate=self.sr)
        else:
            self._onset = None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print('Audio status:', status)
        mono = np.mean(indata, axis=1) if indata.ndim > 1 else indata
        self.q.put(mono.copy())

    def start(self, device=None):
        self.stream = sd.InputStream(channels=1, samplerate=self.sr, blocksize=self.block, callback=self.audio_callback, device=device)
        self.stream.start()
        print('Audio stream started')
        try:
            while True:
                frame = self.q.get()
                self.process_frame(frame)
        except KeyboardInterrupt:
            print('Stopping')
            self.stream.stop()

    def process_frame(self, frame):
        # RMS
        rms = np.sqrt(np.mean(frame**2))
        # FFT
        fft = np.abs(rfft(frame * np.hanning(len(frame)), n=self.fft_size))
        # band energies
        band_energies = np.array([np.mean(fft[idx]) for idx in self.band_bins])
        # spectral centroid
        freqs = rfftfreq(self.fft_size, 1 / self.sr)
        sc_num = (fft * freqs).sum()
        sc_den = fft.sum() + 1e-9
        centroid = sc_num / sc_den

        # onset detection
        onset = False
        if self._onset is not None:
            if self._onset(frame.astype('float32')):
                onset = True

        payload = {
            'rms': float(rms),
            'centroid': float(centroid),
            'bands': band_energies.tolist(),
            'onset': bool(onset),
            'timestamp': time.time()
        }

        if self.osc_callback:
            self.osc_callback(payload)
        else:
            print('payload:', payload)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=int, default=None)
    parser.add_argument('--sr', type=int, default=44100)
    parser.add_argument('--block', type=int, default=1024)
    parser.add_argument('--bands', type=int, default=12)
    args = parser.parse_args()

    analyzer = AudioAnalyzer(samplerate=args.sr, blocksize=args.block, bands=args.bands, osc_callback=None)
    analyzer.start(device=args.device)
