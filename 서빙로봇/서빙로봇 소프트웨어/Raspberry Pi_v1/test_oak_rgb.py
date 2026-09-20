import time
import cv2
from oak_processor import OakProcessor

def test_rgb():
    print("[TEST] OAK-D-Lite RGB & Depth Stream Test Start")
    try:
        proc = OakProcessor()
        proc.start()
        print("[TEST] OAK-D-Lite successfully started.")
        
        start_time = time.time()
        rgb_success = 0
        depth_success = 0
        
        for i in range(50):
            frame = proc.get_frame()
            if frame is not None:
                depth_success += 1
                if frame.rgb_frame is not None:
                    rgb_success += 1
                    # 최초로 성공한 프레임 정보 출력
                    if rgb_success == 1:
                        print(f"[TEST] First RGB frame shape: {frame.rgb_frame.shape}")
                else:
                    print(f"[TEST] Frame {i}: Depth exists, but RGB is None")
            else:
                print(f"[TEST] Frame {i}: Both Depth & RGB are None (Waiting...)")
            time.sleep(0.05)
            
        print("="*50)
        print(f"[TEST] Results (out of 50 attempts):")
        print(f"  - Depth frames received: {depth_success}")
        print(f"  - RGB frames received: {rgb_success}")
        print("="*50)
        
        proc.stop()
    except Exception as e:
        print(f"[TEST] Error occurred: {e}")

if __name__ == "__main__":
    test_rgb()
