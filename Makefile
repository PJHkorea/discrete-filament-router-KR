# =========================================================================
# 🎛️ DISCRETE FILAMENT ROUTER (DFR V3) HYBRID INFRASTRUCTURE MASTER MAKEFILE
# =========================================================================

# 컴파일러 표준 및 명령어 최적화 배리어 고착
CXX      := g++
CXXFLAGS := -O3 -Wall -std=c++20 -shared -fPIC

# pybind11 고속 데이터 관로 인클루드 경로 자율 추적 확장 매핑
PYTHON_INCLUDES  := $(shell python3 -m pybind11 --includes)
EXTENSION_SUFFIX := $(shell python3-config --extension-suffix)

# 최종 타겟 바이너리 확장 모듈 명세 고정 (Single Source of Truth)
TARGET := c_accelerator_bridge_conduit$(EXTENSION_SUFFIX)
SRC    := src/c_accelerator_bridge_conduit.cpp

.PHONY: all test clean run-sim help

# 1. 기저 명령: 하드웨어 브릿지 관로 컴파일 사출
all: $(TARGET)
	@echo "➔ 🏰 [C++ Core Bridge] 0ns 무복사 데이터 도관 바이너리 빌드 완공 성공."
	@echo "   | 확장 플러그인 모듈 사출 완료: $(TARGET)"

$(TARGET): $(SRC)
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) $(PYTHON_INCLUDES) $< -o $@

# 2. 유효성 검증: 다중물리 가드레일 자동화 회귀 테스트 집행 (TDD)
test: $(TARGET)
	@echo ""
	@echo "➔ 🔬 [CI/CD INFRASTRUCTURE] 다중물리 가드레일 유효성 검증 회귀 테스트 스위트 가동..."
	PYTHONPATH=. python3 src/sim/dfr_lithium_jacket_homeostasis_solver.py

# 3. 통합 실증: 16개 전 구간 자석 섹터 실시공간 통합 에뮬레이션 주행
run-sim: $(TARGET)
	@echo ""
	@echo "➔ 🚀 [Digital Twin Engine] 50Hz 진행파 동기화 및 밸브 비상 차단 자가 안정화 런타임 점화!"
	PYTHONPATH=. python3 src/sim/magnet_stream_sim.py

# 4. 인프라 청소: 레지스터 빌드 오염 찌꺼기 전면 포맷팅
clean:
	rm -f $(TARGET)
	rm -f dfr_homeostasis_sweep.png
	@echo "➔ 🧹 [Safe Purge] 하이브리드 빌드 파이프라인 누수 찌꺼기 포맷 완료. 청정 하드웨어 상태 회복."

# 5. 도움말 매뉴얼
help:
	@echo "====================================================================="
	@echo "🖨️ [DFR V3 INFRASTRUCTURE] 현장 엔지니어 빌드 및 배포 자동화 매뉴얼"
	@echo "====================================================================="
	@echo "  • make          : C++ PCIe BAR 제로카피 브릿지 관로 컴파일 (.so 사출)"
	@echo "  • make test     : 다중물리(크누센수, CFL 음속 마진 등) 가드레일 자율 검증"
	@echo "  • make run-sim  : 4개 핵심 계층 통합 실증 디지털 트윈 에뮬레이터 가동"
	@echo "  • make clean    : 빌드 바이너리 및 잔여 그래픽 플롯 전면 청소"
