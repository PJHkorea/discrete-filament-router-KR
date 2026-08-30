# System Architecture Comparison (FNG V3 Application Domain)

본 문서는 기존의 3D 입체 토카막(Volumetric Tokamak) 패러다임과 제가 구상중인 실험 구조체 **이산 유체 패킷 라우팅(Discrete Fluidic Packet Routing, DFR)** 간의 비교 매트릭스를 제공합니다.

> 💡 **아키텍처 변경 사항 (Architectural Amendment):** 본 구성은 "연속적인 3D 입체 플라즈마 질량"(토카막 방식)에서 **"1D 선형 궤적을 탐색하는 불연속적이고 분리된 마이크로 번치(micro-bunch) 패킷"**으로 전환됩니다. 그로써 장파장 킹크 불안정성(long-wavelength kink instabilities)을 우회하고, 구조적 차원 축소를 통해 실시간 제어에 이점을 가져오려 합니다.


---

## Technical Specification Matrix (기술 사양 매트릭스) - 대략적인 예측 및 방향성입니다.

| Metric / Feature (지표 / 특징) | Legacy Volumetric Tokamak (70-Year Foundation) <br>(기존 입체 토카막 - 70년 기반) | Next-Gen Discrete Filament Router (DFR/FNG-V3) <br>(차세대 이산 필라멘트 라우터) |
| :--- | :--- | :--- |
| **Core Infrastructure**<br>(핵심 인프라) | 대형 3D 입체 진공 용기 + 거대 다축 자기 코일 시스템 (Massive 3D Volumetric Vacuum Vessel + Gigantic Multi-Axis Magnetic Coil Systems) | 단일 튜브 폐루프 (**1D 선형 궤적 변환 매핑**) <br>(Single-Tube Closed Loop [**1D Linear Trajectory Transformation Mapping**]) |
| **Plasma Morphology**<br>(플라즈마 형태학) | 연속적인 매크로 3D 플라즈마 구성 (비선형 MHD 프로파일 발산에 취약) (Contiguous Macro 3D Plasma Configuration) | **분리된 순차적 마이크로 번치 패킷** (0.5mm - 1.5mm 마이크로 스케일 이산 스트리밍 토폴로지) <br>(**Decoupled Sequential Micro-Bunch Packets**) |
| **Thermal Operating Envelope**<br>(열적 운전 영역) | 100M K (표준 D-T) ~ 600M K (고급 무중성자 He-3 표적 탐사) (100M K to 600M K) | 100M K (물리 공학적 예측 가능성에 최적화된 표준화된 D-T 구성) (100M K Standardized D-T configuration) |
| **Duty Cycle / Duty Time**<br>(듀티 사이클 / 운전 시간) | 유도성/비유도성 펄스 운전 (장기 정상 상태 유지방식으로 발전 중) (Inductive/Non-Inductive Pulse Operations) | **연속적인 정상 상태 스트림** (365일 / 24시간 중단 없는 운전을 위해 설계됨) <br>(**Continuous Steady-State Stream**) |
| **Containment & Shielding**<br>(가둠 및 차폐) | 고체 텅스텐(W) / 탄소 제일벽 타일 (고용량 열응력 및 열속 흡수) (Solid Tungsten / Carbon First-Wall Tiles) | **레이어 3 전방벽 (W-Cu FGM)** + **표면 액체 리튬-납 (Li-Pb) 필름** (자가 조절 증발식 기화 차폐 쿠션) <br>(**Layer 3 Forward Wall** + **Surface Liquid Li-Pb Film**) |
| **Control Ingress Loop**<br>(제어 인입 루프) | 자기 전류를 통한 중앙 집중식 피드백 변조 (밀리초 스케일의 진단 프로세싱) (Centralized Feedback Modulation) | **3계층 하드웨어 융합 제어 루프** + 항상성 커널 (10ns 미만 하드웨어 게이팅 및 0ns 카피프리 메모리 라우팅) <br>(**3-Tier Hardware-Fused Control Loop** + Homeostasis Kernel) |
| **Energy Conversion Efficiency**<br>(에너지 전환 효율)| ~30% - 40% (열역학적 증기 사이클과 결합된 기존의 중성자-열 전환 방식) (~30% - 40% Neutron-thermal conversion) | **~60% - 70% 복합 효율** (80% 고급 열 회수 + 20% 직접 전하 차이 하이브리드 전력 회수) <br>(**~60% - 70% Compound Efficiency**) |
| **Plant Footprint / Land Mass**<br>(플랜트 부지 / 면적) | 광범위한 극저온 및 보조 가열 시스템을 포함하는 대규모 중앙 집중식 시설 (Large-scale centralized facilities) | 모듈형 고온 초전도(HTS) 매트릭스 (**SMR 스케일의 확장 가능한 컴팩트 폼 팩터**) <br>(Modular HTS Matrix [**SMR-scale scalable compact form factor**]) |
| **Neutron Flux Mitigation**<br>(중성자 속 완화) | 360도 등방성 무작위 산란 (상당한 수준의 다층 전역 구조 차폐 필요) (360-degree Isotropic Random Scattering) | **전방 운동 벡터 정렬** (정의된 후방 클린 존을 갖춘 포획 허브 지향 전방-대각선 빔 방출) <br>(**Forward Kinetic Vector Alignment**) |


---

💡 **참고 (See Also):** 상세한 기계적 계층 및 소프트웨어 루프 구현은 [System_Specs.md]를 참조하십시오.

