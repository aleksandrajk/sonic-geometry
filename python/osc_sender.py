"""
Small OSC wrapper to send features to TouchDesigner.
Uses python-osc to send concise messages.
"""

import json
import argparse
from pythonosc import udp_client


class OscSender:
    def __init__(self, host='127.0.0.1', port=8000, base_path='/sonic'):
        self.client = udp_client.SimpleUDPClient(host, port)
        self.base = base_path.rstrip('/')

    def send_features(self, payload: dict):
        # Send scalar features
        self.client.send_message(f'{self.base}/rms', float(payload['rms']))
        self.client.send_message(f'{self.base}/centroid', float(payload['centroid']))
        self.client.send_message(f'{self.base}/onset', int(payload['onset']))
        # Send band energies as a single bundle (flattened)
        bands = payload.get('bands', [])
        # TouchDesigner OSC In DAT will parse this list into columns
        self.client.send_message(f'{self.base}/bands', list(map(float, bands)))
        self.client.send_message(f'{self.base}/timestamp', float(payload.get('timestamp', 0.0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()

    sender = OscSender(host=args.host, port=args.port)
    # quick example payload
    sender.send_features({
        'rms': 0.0123,
        'centroid': 2600.0,
        'onset': True,
        'bands': [0.1] * 12,
        'timestamp': 0.0
    })
