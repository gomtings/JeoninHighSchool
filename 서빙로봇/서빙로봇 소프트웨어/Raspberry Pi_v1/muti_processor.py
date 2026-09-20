import multiprocessing # threading 대신 사용
import socket
import time
from datetime import datetime
# koceti_Read_Modbus는 _run 내부에서 import 하거나 상단에 둡니다.

class koceti_worker:
    def __init__(self, target_ip, port, main_crane_port, shared_state, period_sec=1.0):
        self.period_sec = period_sec
        # threading.Event 대신 multiprocessing.Event 사용
        self._stop = multiprocessing.Event()
        self._process = None # _th 대신 _process
        
        self.target_ip = target_ip        # Client용 Address
        self.port = port                  # Client용 포트
        self.main_crane_port = main_crane_port # Server용 포트
        self.shared_state = shared_state  # Manager Proxy 객체

        # [중요] __init__에서는 연결 객체를 생성하지 않습니다.
        # 여기서 생성하면 프로세스 시작 시 "Pickling Error"가 발생합니다.

    def _run(self):
        """이 코드는 자식 프로세스 메모리 공간에서 실행됩니다."""
        
        print(f"[Worker] Modbus 프로세스 시작 (Target: {self.target_ip})")
        # 1. 자식 프로세스 안에서 객체 생성 및 연결
        while not self._stop.is_set():
                start_time = time.time()
                ts = datetime.now().strftime("%H:%M:%S")
                """
                    # --- AML 데이터 읽기 ---
                    main_data = crane_tester.get_aml_data_receive()
                    if main_data is None:
                        print(f"[{ts}][WORKER] Modbus 데이터 수신 실패")
                    else:
                        # 공유 상태(SharedState Proxy) 업데이트
                        self._update_modbus_shared_state(main_data)
                        print(f"[{ts}][WORKER] Modbus 사이클 OK")
                    """
    def _update_udp_shared_state(self, data):
        """전달받은 데이터를 shared_state 프록시에 저장"""
        s = self.shared_state
        try:
            s.set_danger_level(data.get("roll_over_flag", 0))
            s.set_boom_length(data.get("boom length(m)", 0))
            s.set_boom_angle(data.get("boom angle(deg)", 0))
            s.set_weight(data.get("load weight(ton)", 0))
            s.set_engine_speed(data.get("engine speed(rpm)", 0))
            s.set_wind_speed(data.get("wind speed(m/s)", 0))
            s.set_swing_angle(data.get("swing angle(deg)", 0))
            s.set_specifications(data.get("specifications", 0))
            s.set_radius_main(data.get("radius main(m)", 0))
            s.set_radius_aux(data.get("radius aux(m)", 0))
            s.set_battery_voltage(data.get("battery voltage(V)", 0))
            s.set_engine_temp(data.get("engine temp(C)", 0))
            s.set_oil_pressure(data.get("oil pressure", 0))
            s.set_hydraulic_oil_temp(data.get("hydraulic oil temp(C)", 0))
            s.set_main_height(data.get("main height(m)", 0))
            s.set_aux_height(data.get("aux height(m)", 0))
            s.set_rd_height(data.get("3rd height(m)", 0))
            s.set_status_1(data.get("status_1", 0))
            s.set_status_2(data.get("status_2", 0))
            s.set_lower_angle(data.get("chassis_angle", 0))
        except Exception as e:
            print(f"[Worker] 데이터 업데이트 오류: {e}")

    def _update_modbus_shared_state(self, data):
        """전달받은 데이터를 shared_state 프록시에 저장"""
        s = self.shared_state
        try:
            s.set_boom_length(data.get("boom length(m)", 0))
            s.set_boom_angle(data.get("boom angle(deg)", 0))
            s.set_weight(data.get("load weight(ton)", 0))
            s.set_engine_speed(data.get("engine speed(rpm)", 0))
            s.set_wind_speed(data.get("wind speed(m/s)", 0))
            s.set_swing_angle(data.get("swing angle(deg)", 0))
            s.set_specifications(data.get("specifications", 0))
            s.set_radius_main(data.get("radius main(m)", 0))
            s.set_radius_aux(data.get("radius aux(m)", 0))
            s.set_battery_voltage(data.get("battery voltage(V)", 0))
            s.set_engine_temp(data.get("engine temp(C)", 0))
            s.set_oil_pressure(data.get("oil pressure", 0))
            s.set_hydraulic_oil_temp(data.get("hydraulic oil temp(C)", 0))
            s.set_main_height(data.get("main height(m)", 0))
            s.set_aux_height(data.get("aux height(m)", 0))
            s.set_rd_height(data.get("3rd height(m)", 0))
            s.set_status_1(data.get("status_1", 0))
            s.set_status_2(data.get("status_2", 0))
            s.set_lower_angle(data.get("chassis_angle", 0))
        except Exception as e:
            print(f"[Worker] 데이터 업데이트 오류: {e}")


    def start(self):
        if self._process and self._process.is_alive():
            return
        self._stop.clear()
        # Thread 대신 Process 사용
        self._process = multiprocessing.Process(target=self._run, daemon=True)
        self._process.start()

    def stop(self):
        self._stop.set()
        # 프로세스에서는 외부에서 객체를 닫을 수 없으므로 
        # _run의 finally에서 닫히도록 유도합니다.

    def join(self, timeout=None):
        if self._process:
            self._process.join(timeout)