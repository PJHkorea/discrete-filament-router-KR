# =========================================================================
# @file constraints.xdc
# @brief DFR V3 전 구간 자석 공용 통합 마스터 코어 하드웨어 물리 핀 제약 조건
# @details 50Hz 전력망(Grid) 고정 리듬 동기화를 위한 초정밀 물리 클록을 정의하고,
#          이중 독립 드라이버 포트(직진 코일, 대각 탈출 코일)의 실리콘 핀을 매핑함.
# =========================================================================

# -------------------------------------------------------------------------
# 1. 기저 주파수 및 타임 인터벌 물리 클럭 정의 (Clock Constraints)
# -------------------------------------------------------------------------
# 상용 전력망(Grid) 동기화 50Hz 파도타기 리듬의 소산 지터를 차단하기 위해 
# FPGA 패브릭 내부 메인 시스템 클럭(100MHz 기저선) 및 전역 타이머 클럭 유도 정의 수행
create_clock -period 10.000 -name sys_clk_pin [get_ports sys_clk]

# -------------------------------------------------------------------------
# 2. 하드웨어 주소 식별 및 동기화 인풋 핀 매핑 (Input Port Mappings)
# -------------------------------------------------------------------------
# [is_chamber_node_pin]: 현장 배선 단계에서 0V(일반) 또는 3.3V(챔버) 전원에 직결되는 물리 핀
# 컴파일러의 임의 부동(Floating) 오동작에 따른 수치적 환각 현상을 내부 풀다운 저항으로 원천 차단
set_property PACKAGE_PIN AK17      [get_ports is_chamber_node_pin]
set_property IOSTANDARD LVCMOS33   [get_ports is_chamber_node_pin]
set_property PULLDOWN TRUE          [get_ports is_chamber_node_pin]

# 상류(N-1) 자석 전선으로부터 나노초(ns) 단위로 직결 인입되는 고속 하드와이어 전하 시널 포트 
set_property PACKAGE_PIN AL18      [get_ports upstream_wire_signal]
set_property IOSTANDARD LVCMOS33   [get_ports upstream_wire_signal]

# 50Hz 삼각함수 테이블 교류 동기화 입전 와이어 포트 명세
set_property PACKAGE_PIN AM19      [get_ports cos_50hz]
set_property IOSTANDARD LVCMOS33   [get_ports cos_50hz]
set_property PACKAGE_PIN AN20      [get_ports sin_50hz]
set_property IOSTANDARD LVCMOS33   [get_ports sin_50hz]

# -------------------------------------------------------------------------
# 3. 이중 독립 드라이버 물리 코일 출력 포트 매핑 (Output Port Mappings)
# -------------------------------------------------------------------------
# 📌 포트 1: 평시 Z축 주행 가둠 및 직진 가속용 GaN/SiC 인버터 게이트 드라이버 직결 선로
# 고주파 스위칭 시 전력 반도체의 열화 스트레스를 억제하기 위해 FAST 슬루레이트 및 8mA 전류 세기 고정 각인
set_property PACKAGE_PIN AP21      [get_ports out_main_z_coil_wire]
set_property IOSTANDARD LVCMOS33   [get_ports out_main_z_coil_wire]
set_property SLEW FAST             [get_ports out_main_z_coil_wire]
set_property DRIVE 8               [get_ports out_main_z_coil_wire]

# 📌 포트 2: 비상시 대각 탈출축 자석 세트 역방향 2배 폭발 가동용 게이트 드라이버 직결 선로
# 평시에는 0V 공선 상태를 유지하다가 비상 순간 0ns 스왑을 유도하도록 최외각 고속 드라이버 핀에 결속 마감
set_property PACKAGE_PIN AQ22      [get_ports out_chamber_curl_coil_wire]
set_property IOSTANDARD LVCMOS33   [get_ports out_chamber_curl_coil_wire]
set_property SLEW FAST             [get_ports out_chamber_curl_coil_wire]
set_property DRIVE 8               [get_ports out_chamber_curl_coil_wire]

# -------------------------------------------------------------------------
# 4. 연산 지연 및 크로스토크 상쇄를 위한 타이밍 경로 격리 (Timing Exceptions)
# -------------------------------------------------------------------------
# 무분기 MUX(uni_branchless_select) 및 부호 대칭 가드로 인해 비상 플래그가 전파되는 경로는
# 일반적인 동기식 타이밍 분석 루프에서 완전히 격리(False Path 설정)하여 지터 병목을 제거함.
set_false_path -from [get_ports is_chamber_node_pin] -to [get_ports out_main_z_coil_wire]
set_false_path -from [get_ports is_chamber_node_pin] -to [get_ports out_chamber_curl_coil_wire]

# 고온 열 잡음 도메인 축소용 파데 필터 가속 파이프라인의 물리적 배치 최적화 고정
set_max_delay -from [get_ports upstream_wire_signal] -to [get_ports out_main_z_coil_wire] 10.000
set_max_delay -from [get_ports upstream_wire_signal] -to [get_ports out_chamber_curl_coil_wire] 10.000

