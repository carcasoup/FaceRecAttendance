from client.config import STUDENTS_DIR
from client.recognize_live import recognize_live
from client.collect_data import collect_data
import argparse
mode = ['collect', 'recognize']
parser = argparse.ArgumentParser(description='Board client for attendance project')
parser.add_argument('--mode', choices=['collect', 'recognize'], default=mode[1],
                    help=f'working mode: collect data or recognize live (default: {mode[1]})')
parser.add_argument('--interval', type=float, default=30,
                    help='interval between captures in seconds (only for collect)')
parser.add_argument('--output', type=str, default=STUDENTS_DIR,
                    help='directory to save collected images')
parser.add_argument('--camera', type=int, default=0,
                    help='camera index')
args = parser.parse_args()

print(f"Running in '{args.mode}' mode.")
if args.mode == 'collect':
    collect_data(args.interval, args.output, args.camera)
else:
    recognize_live(args.camera)
