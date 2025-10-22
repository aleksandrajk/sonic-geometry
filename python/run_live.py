"""
Glue script: runs audio analyzer and forwards to OSC.
"""
import argparse
import json
from audio_analysis import AudioAnalyzer
from osc_sender import OscSender


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.json')
    args = parser.parse_args()

    cfg = json.load(open(args.config))
    osc = OscSender(host=cfg['osc']['host'], port=cfg['osc']['port'], base_path=cfg['osc']['base_path'])
    analyzer = AudioAnalyzer(samplerate=cfg['audio']['samplerate'], blocksize=cfg['audio']['blocksize'], bands=cfg['features']['bands'], osc_callback=osc.send_features)
    analyzer.start(device=cfg['audio'].get('device'))

if __name__ == '__main__':
    main()
