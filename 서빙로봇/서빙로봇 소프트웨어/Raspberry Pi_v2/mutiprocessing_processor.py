# cd '.\Video-analysis\'
# deactivate # 가상 환경에서 빠져 나오기
# python -m venv .venv # 처음 한번 가상환경 생성...
# C:\GitHub\solimatics\Video-analysis\.venv\Scripts\Activate.ps1

from analysis import AnalysisApp
import time
import socket
from Network_Manager import manage_network
from koceti_worker import koceti_worker
from laser_worker import laser_worker
from transmit_Crane_Data_Worker import transmit_Crane_Data_Worker
from Update_Can_Data import Update_Can_Data
from shared_state import SharedState
from flask import Flask, request # request 임포트 필요
import requests # API 호출을 위해 임포트
from Crane_MQTT import MQTTClient # Crane_MQTT.py 파일이 있다고 가정
from multiprocessing.managers import BaseManager

# [추가] mDNS 라이브러리 임포트
from zeroconf import ServiceInfo, Zeroconf

# 1. 매니저 설정
class MyManager(BaseManager):
    pass

def make_local_url(port=5000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    return f"http://{ip}:{port}"

def get_cpu_serial():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    # "Serial		: 10000000deadbeef" 형태에서 값만 추출
                    return line.split(':')[1].strip().upper()
    except:
        return "ERROR"
    return "0000000000000000"

def main():
    # 1. 일단 변수들을 None으로 초기화 (에러 대비)
    shared_state = None
    manager = None

    # 1. 부팅 직후 시스템 안정화를 위해 무조건 10초 대기
    print("시스템 대기 중 (3s)...")
    time.sleep(3)
    
    # 2. 네트워크 관리는 별도의 try로 감싸서 실패해도 프로그램은 돌게 함
    try:
        # 1. 네트워크 상태 관리
        id_addr = manage_network()
    except Exception as e:
        print(f"[Warning] 네트워크 설정 중 오류 발생 (무시하고 진행): {e}")
        id_addr = "127.0.0.1"
            
    try: 
        # 2. 클래스 등록 (이 시점에 BaseManager가 필요함)
        MyManager.register('SharedState', SharedState)
        MyManager.register('MQTTClient', MQTTClient)

        # 3. 매니저 시작
        manager = MyManager()
        manager.start()

        # 4. 공유 객체(Proxy) 생성
        shared_state = manager.SharedState() 
        shared_mqtt = manager.MQTTClient() 
            
        # 2. 각 워커 객체 생성. 'shared_state'를 공통으로 전달합니다.
        koceti_poller = koceti_worker(
            target_ip='0.0.0.0',    # Client Address
            port=5005,    # Client port
            main_crane_port='/dev/ttyUSB0', # Server (Passive)
            shared_state=shared_state, 
            period_sec=0.05
        )

        laser_poller = laser_worker(
            parents=None, 
            port="/dev/laser_sensor",     
            rate=9600, 
            h=1530.0,
            alpha=44.50,
            speed_kmh=1.0,
            shared_state=shared_state, 
            period_sec=1.0 # 측정 주기/
        )
        
        can_data = Update_Can_Data( # 
            shared_state=shared_state,
            mqttclient=shared_mqtt,
            period_sec=0.2
        )

        data_simulator = transmit_Crane_Data_Worker( # 
            shared_state=shared_state,
            mqttclient=shared_mqtt,
            period_sec=0.5
        )

        app = AnalysisApp(
            host="0.0.0.0", 
            port=5000,
            shared_state=shared_state
        )
            
        # mDNS(ZeroConf) 객체 변수 준비
        zeroconf = None 
                       
        # --- MQTT 연결 및 루프 시작 ---
        shared_mqtt.connecting()
        shared_mqtt.loop_start()
        
        url = make_local_url()
        device_id = get_cpu_serial()
        shared_state.set_serial_info(device_id)
        print(f"url: {url} , device_id: {device_id}")
        print("[Main] Modbus 폴러와 데이터 시뮬레이터를 시작합니다.")
        app.start_background_capture()
        app.start_server()
        koceti_poller.start()
        can_data.start()
        data_simulator.start()
        laser_poller.start()
        
        # mDNS 서비스 등록 (여기서 네트워크에 방송 시작)
        try:
            desc = {'path': '/radar.png'}
            info = ServiceInfo(
                "_http._tcp.local.",
                "RadarServer._http._tcp.local.",  # 자바 앱이 찾을 이름
                addresses=[socket.inet_aton(id_addr)], # send_ip()로 찾은 IP
                port=5000,
                properties=desc,
                server=f"radar-host.local."
            )
            zeroconf = Zeroconf()
            zeroconf.register_service(info)
            print(f"[Main] mDNS Broadcasting started on {id_addr}:5000 (RadarServer)")
        except Exception as e:
            print(f"[Main] [WARNING] mDNS 등록 실패: {e}")
                
        # 3. 메인 프로그램은 최종 통합된 데이터를 큐에서 꺼내 사용합니다.
        while True:
            try:
                detections = app.get_current_detections_list()
                if detections:  # 리스트가 비어있지 않으면 True
                    print(detections)
                time.sleep(0.2)
            except Exception:
                # 워커들이 살아있는지 확인
                if not koceti_poller._th.is_alive() or not data_simulator._th.is_alive():
                    print("[Main] [ERROR] 하나 이상의 워커 쓰레드가 중지되었습니다.")
                    break
                continue
                
    except KeyboardInterrupt:
        print("\n[Main] 종료 요청 수신.")
    
    except Exception as e:
        print(f"초기화 중 치명적 에러 발생: {e}")
        if manager:
            manager.shutdown()
            
    finally:
        print("[Main] 모든 워커와 리소스를 정리합니다...")
        if zeroconf: # mDNS 방송 종료
            try:
                print("[Main] mDNS 방송을 중단합니다.")
                zeroconf.unregister_all_services()
                zeroconf.close()
            except Exception as e:
                print(f"mDNS 해제 중 에러: {e}")
                    
        # 2. 서버 종료 API 호출
        try:
            # 서버 스레드를 종료시키기 위해 shutdown API를 호출합니다.
            requests.post(f"http://127.0.0.1:{app.port}/shutdown")
            print("[Main] 서버 종료 요청 전송 완료.")
        except requests.exceptions.ConnectionError:
            # 서버가 이미 내려갔거나 다른 이유로 연결이 안될 수 있습니다.
            print("[Main] 서버에 연결할 수 없어 종료 요청을 보내지 못했습니다.")

        app.stop_background_capture()
        koceti_poller.stop()
        data_simulator.stop()
        can_data.stop()
        laser_poller.stop()

        # 3. 모든 스레드가 종료될 때까지 기다립니다.
        if app.server_thread and app.server_thread.is_alive():
            print("[Main] 서버 스레드가 종료될 때까지 대기합니다...")
            app.server_thread.join(timeout=2.0) # 타임아웃과 함께 대기

        koceti_poller.join()
        data_simulator.join()
        can_data.join()
        laser_poller.join()

        print("[Main] MQTT 연결을 종료합니다.")
        shared_mqtt.loop_stop()
        shared_mqtt.disconnect()

        # 매니저 종료
        manager.shutdown()
        
        print("[Main] 모든 워커가 성공적으로 종료되었습니다.")
        print("[Main] 프로그램 종료.")

# [필수] 멀티프로세싱을 사용하므로 이 가드가 반드시 있어야 합니다.
if __name__ == "__main__":
    main()

