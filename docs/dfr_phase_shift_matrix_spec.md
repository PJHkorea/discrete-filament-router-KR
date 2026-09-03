# 이산형 필라멘트 라우터 (DFR) - 전력 반도체 주입용 고정 위상차 오프셋 행렬 사양서
## (Phase-Shift Resolution Matrix Specification for GaN/SiC Fabric Platform)

## 1. Deployment Overview
본 문서는 `Normal_Operation_Specs.md` 및 `unified_magnet_master_core.h`에 정의된 **50Hz 진행파(Traveling Wave)**를 16개의 분산형 전자석 인버터 게이트 드라이버에 하드와이어드(Hardwired) 방식으로 직접 주입하기 위한 물리 위상 오프셋 제약 사양을 정의합니다.

- **기저 시스템 클럭 (sys_clk):** 100 MHz ($\Delta t = 10.000\text{ ns}$ 결정론적 고정 클럭)
- **목표 진행파 주파수:** 50.0 Hz (1주기 고유 타임 윈도우 = $20.0\text{ ms}$)
- **동기화 토폴로지:** 각 자석 노드는 자신의 `Sector ID`에 할당된 고정 타이머 카운터 오프셋 값을 로컬 FPGA/ASIC 패브릭 상수에 정적으로 바인딩합니다. 이후 인접 노드 간 1:1 릴레이 통신만을 이용하여 전체 루프에 완벽한 시계 방향(CW) 전자기적 이송 필드를 구성합니다.

## 2. 자석 섹터별 고정 위상차 오프셋 매트릭스 테이블
본 카운터 파라미터는 `constraints.xdc`에 정의된 마스터 동기 및 클럭 물리 핀(`AP21`, `AQ22`)과 내부 가속 파이프라인 레지스터 간의 경로를 다이렉트 IOB(입출력 블록)에 매핑하여, 배선 지연을 최소화하고 타이밍 마감(Timing Closure)을 완벽히 충족하도록 설계되었습니다.


| Sector ID | Role | Spatial Angle (°) | Phase Offset (rad) | Phase Offset (°) | FPGA Timer Register Offset (100MHz sys_clk) |
|:---|:---|:---|:---|:---|:---|
| Sector 00 | GENERAL (AP21) | 0.00° | 0.0000 π_rad | 0.00° | 0 Counts |
| Sector 01 | GENERAL (AP21) | 22.50° | 0.1250 π | 22.50° | 125,000 Counts |
| Sector 02 | GENERAL (AP21) | 45.00° | 0.2500 π | 45.00° | 250,000 Counts |
| Sector 03 | GENERAL (AP21) | 67.50° | 0.3750 π | 67.50° | 375,000 Counts |
| Sector 04 | GENERAL (AP21) | 90.00° | 0.5000 π | 90.00° | 500,000 Counts |
| Sector 05 | GENERAL (AP21) | 112.50° | 0.6250 π | 112.50° | 625,000 Counts |
| Sector 06 | GENERAL (AP21) | 135.00° | 0.7500 π | 135.00° | 750,000 Counts |
| Sector 07 | GENERAL (AP21) | 157.50° | 0.8750 π | 157.50° | 875,000 Counts |
| Sector 08 | GENERAL (AP21) | 180.00° | 1.0000 π | 180.00° | 1,000,000 Counts |
| Sector 09 | GENERAL (AP21) | 202.50° | 1.1250 π | 202.50° | 1,125,000 Counts |
| Sector 10 | GENERAL (AP21) | 225.00° | 1.2500 π | 225.00° | 1,250,000 Counts |
| Sector 11 | GENERAL (AP21) | 247.50° | 1.3750 π | 247.50° | 1,375,000 Counts |
| Sector 12 | GENERAL (AP21) | 270.00° | 1.5000 π | 270.00° | 1,500,000 Counts |
| Sector 13 | GENERAL (AP21) | 292.50° | 1.6250 π | 292.50° | 1,625,000 Counts |
| Sector 14 | GENERAL (AP21) | 315.00° | 1.7500 π | 315.00° | 1,750,000 Counts |
| Sector 15 | CHAMBER (AQ22) | 337.50° | 1.8750 π | 337.50° | 1,875,000 Counts |

## 3. 현장 엔지니어 주입 지침 및 가드레일 (Deployment Guardrails)
1. **[상수 컴파일 타임 고정]:** 각 섹터의 GaN/SiC 전력 인버터 제어 MCU 빌드 시, 상기 명세된 타이머 오프셋(`Timer Register Offset`) 값을 변경 불가능한 정적 상수(Constant)로 선언하여 컴파일 타임에 물리적으로 하드코딩 결속하십시오.
2. **[Sector 15 노드 특수 인터록 보호]:** Sector 15는 평시 자력 출력을 `0.0`으로 유지하는 패시브 모드로 동작합니다. 단, 상류 노드 단선 인터럽트 수신 시 **10ns 이내에 대각선 탈출축 물리 핀(`AQ22`)으로 역방향 벡터(`-sin_50hz * 2.0`)를 즉시 사출**해야 합니다. 이를 위해 위상 타이머가 50Hz 동기화 카운트(2,000,000 사이클)를 백그라운드에서 중단 없이 상시 러닝하도록 하드웨어 독립 배리어를 구성하십시오.
3. **[시계 방향 위상 정합성 검증]:** 본 행렬은 시간축에 따라 위상을 순방향으로 견인하는 **시계 방향(CW) 부호 행렬곱**을 추종합니다. 섹터 번호가 증가할수록 카운터 및 라디안 위상 각도가 시간축상 미래 방향으로 전진하여 동기화되는지 최종 확증하십시오.
