# Sonic Geometry

**Interactive art that makes geometry sing.**

Sonic Geometry transforms live audio (music, environment, microphone input) into dynamic 2D/3D visuals using **TouchDesigner + Python**.  
This repository contains a complete README, example Python helper scripts for audio analysis and OSC messaging, suggested TouchDesigner network notes and snippets, configuration files, and troubleshooting tips to get you started quickly.

---

## 📖 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture & Data Flow](#architecture--data-flow)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [TouchDesigner Setup](#touchdesigner-setup)
   - Network overview (CHOPs, DATs, TOPs)
   - Example DAT Python snippets to receive OSC / TCP
   - Example recommended node layout
8. [Design Patterns & Mapping Strategies](#design-patterns--mapping-strategies)
9. [Performance & Latency Tuning](#performance--latency-tuning)
10. [Extending the Project](#extending-the-project)
11. [Troubleshooting](#troubleshooting)


---

## 🌀 Project Overview

Sonic Geometry is an interactive art project where geometric primitives (points, lines, polygons, parametric surfaces) react to audio using rule-based mappings:

- Amplitude → Scale  
- Spectral centroid → Color temperature  
- Beat events → Geometry spawn/decay  
- Spectral bins → Per-vertex displacement  

This repository provides:

- Realtime audio capture + feature extraction in Python  
- OSC sender examples to push data into TouchDesigner  
- Recommended TouchDesigner network structure and Python DAT snippets to use those messages  
- Configuration and mapping examples so you can iterate fast  

> The TouchDesigner `.toe` project is **not included** (binary), but this README provides full code and node instructions to reproduce the visuals. Treat this repo as the code + documentation companion for building your own TouchDesigner scene.

---

## Features

- Low-latency microphone or system audio capture  
- Per-frame spectral features: RMS, spectral centroid, spectral flux, band energies  
- Beat / onset detection (via **aubio** or built-in algorithm)  
- OSC transport to TouchDesigner (configurable address/port)  
- Mapping suggestions for translating audio features into geometry and animation parameters  
- Performance and stability tips for installations or laptops  

---

## ⚙️ Architecture & Data Flow

1. **Audio Input** — microphone, loopback, or line-in  
2. **Python audio process** — captures frames, computes features  
3. **OSC / TCP transport** — sends compact feature packets to TouchDesigner  
4. **TouchDesigner** — receives data, drives CHOP/TOP/Geometry parameters to animate visuals  
5. **Optional feedback** — TouchDesigner sends OSC back to Python for bidirectional interaction  

---

## 🧩 Prerequisites

- **TouchDesigner** (version `2021.10000+` recommended)  
- **Python 3.9+** (tested on 3.10–3.11)  
- **Python packages:** see below  

### Recommended Python Packages (also in `requirements.txt`)
numpy
sounddevice
scipy
python-osc
aubio # optional but recommended for beat/onset detection
librosa # optional for offline analysis / extra features


---

## ⚙️ Configuration

You’ll find or create a file named `config.json` in the project root to define parameters such as audio device, sample rate, OSC host/port, etc.

### Example

```json
{
  "audio": {
    "device": null,
    "samplerate": 44100,
    "blocksize": 1024
  },
  "osc": {
    "host": "127.0.0.1",
    "port": 8000,
    "base_path": "/sonic"
  },
  "features": {
    "bands": 12
  }
}

---

## 🖥️ TouchDesigner Setup

### Suggested Workflow

1. Create an OSC In DAT (or OSC In CHOP) in TouchDesigner listening on the same port (8000 by default)
2. Convert the incoming OSC Table to CHOP channels (DAT → CHOP or Table DAT parsing)
3. Use CHOP outputs to drive SOP transforms, instancing attributes, TOP uniforms, or GLSL shader uniforms

### Example Channel Mappings

- **rms** → global scale / emission intensity
- **centroid** → color hue / shader parameter
- **bands[0..N]** → per-instance scale or displacement attributes
- **onset** → spawn a new geometry burst or trigger a timed effect

### Example CHOP Execute DAT snippet

Put this in a Text DAT or CHOP Execute DAT to react to incoming changes:

```python
def onValueChange(channel, sampleIndex, val, prev):
    if channel.name == 'onset' and val > 0.5:
        # trigger spawn on geo network - replace with your operator paths
        op('geo_spawn').par.spawnpulse.pulse()
    if channel.name == 'rms':
        op('geo_main/transform1').par.scale = 1.0 + val * 4.0
    return

---

## 🧩 Design Patterns & Mapping Strategies

| Audio Feature | Visual Mapping |
|---------------|----------------|
| RMS | Global scale, brightness |
| Spectral centroid | Color hue / temperature |
| Bands | Instance size or shape deformation |
| Onset | Burst, spawn, or camera shake |

### Mapping tips:

- Normalize band energies before mapping to avoid huge parameter ranges
- Use smoothing filters (CHOP Filter or low-pass) for aesthetically pleasing motion
- Use thresholds for onset to avoid repeated triggers from noisy input

---

## ⚡ Performance & Latency Tuning

- **Blocksize**: smaller → lower latency (e.g., 256–1024) but higher CPU usage
- **Onset detection**: use aubio for efficient realtime onsets
- **Band count**: keep it modest (8–16) to reduce OSC and TouchDesigner cook overhead
- **OSC payloads**: avoid sending full waveforms; send small arrays and scalars
- **GPU**: offload rendering-heavy tasks to GLSL / GPU-based TOPs and SOPs

---

## 🧩 Extending the Project

**Ideas for extension:**

- Add MIDI or Ableton Link for tempo/BPM sync
- Use ML models to map audio features to complex visual styles or presets
- Build a small web UI or TouchDesigner UI to adjust mapping scalars live (via OSC)
- Implement feedback from TouchDesigner to Python for two-way generative systems

---

## Troubleshooting

### No OSC messages in TouchDesigner?

- Ensure the OSC port matches in both Python and TouchDesigner (default 8000)
- Check firewall or network settings that may block UDP
- Test with a UDP listener: `nc -ul 8000` (macOS/Linux) or an OSC monitor

### High CPU usage

- Increase blocksize in config.json
- Reduce band count and feature computations
- Offload heavy offline computations (e.g., librosa) to separate processes

### Lag / Latency

- Use smaller blocksize but balance CPU load
- Reduce TouchDesigner cook frequency for heavy nodes
- Use CHOP caching and optimize node resolution (TOPs/SOPs)

---

## License & Credits

**Built with:**
- TouchDesigner
- sounddevice
- python-osc
- aubio
