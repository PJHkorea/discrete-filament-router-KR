# 이산형 필라멘트 라우터 (DFR) - 전력 반도체 주입용 고정 위상차 오프셋 행렬 사양서
## (Phase-Shift Resolution Matrix Specification for GaN/SiC Fabric Platform)

## 1. Deployment Overview
본 문서는 `Normal_Operation_Specs.md` 및 `unified_magnet_master_core.h`에 구성된 **50Hz 무연산 정속 파도타기 진행파**를 실제 현장 16개 분산 전자석 인버터 게이트 드라이버 단에 하드와이어드 주입하기 위한 물리 위상 행렬 제약 사양을 정의합니다.

- **기저 시스템 클럭 (sys_clk):** 100 MHz ($\Delta t = 10.000\text{ ns}$ 결정론적 고정 클럭)
- **목표 파도타기 주파수:** 50.0 Hz (1주기 고유 타임 도메인 윈도우 = $20.0\text{ ms}$)
- **동기화 토폴로지:** 각 자석 노드는 오직 자신의 `Sector ID`에 해당되는 고정 타이머 카운터 오프셋만을 로컬 실리콘 패브릭에 고착 바인딩한 채, 이웃 노드 간 1:1 결속 릴레이 전하 통신만으로 루프 전역에 완벽한 시계 방향(CW) 전자기적 유압 미끄럼틀을 자율 실증합니다.

## 2. 자석 섹터별 고정 위상차 오프셋 매트릭스 테이블
아래 산출된 카운터 값들은 `constraints.xdc`의 물리 핀(`AP21`, `AQ22`) 가속 파이프라인 내부 레지스터에 0ns 만에 직접 하드와이어 바인딩 마감될 100% 결정론적 실전 파라미터 자산입니다.

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
1. **[volatile 레지스터 직결 고정]:** 각 섹터의 GaN/SiC 전력 인버터 제어 MCU 칩셋 빌드 시, 상기 명세된 `FPGA Timer Register Offset` 값을 하위 타이머 타이밍 블록의 기저 오프셋 값으로 컴파일 타임 하드코딩 결속하십시오.
2. **[15번 챔버 노드 특수 인터록 보호]:** 15번 섹터는 평시 자력 출력이 `0.0`으로 패시브 유지되다가, 상류 노드 단선 인터럽트(-99.0f) 수신 sub-10ns 이내에 대각선 탈출축 `AQ22` 번 핀으로 `-sin_50hz * 2.0` 역방향 벡터 기하 사출을 집행해야 하므로, 위상 타이머가 50Hz 동기화 카운트를 2,000,000 주기로 무중단 백그라운드 런닝하고 있도록 하드웨어 배리어를 치십시오.
3. **[시계 방향 전진 위상 정합성]:** 본 행렬은 미래 시간축으로 위상을 전방 견인하는 **시계 방향(CW) 부호 행렬곱**을 추종하므로, 섹터 번호가 증가할수록 카운터 및 라디안 위상 각도가 과거가 아닌 미래 방향으로 전진 충족되어 결속되어 있음을 최종 확증합니다.
