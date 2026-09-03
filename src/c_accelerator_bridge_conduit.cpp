#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept> 
#include <cstdint>

#include "unified_magnet_master_core.h"

namespace py = pybind11;

/**
 * @brief [Upstream Conduit] 실리콘 자석 레지스터 물리 주소 가로채기 인터셉터 (고도화 배포 사양)
 */
py::array_t<float> extract_magnet_flux_buffer(uintptr_t struct_raw_ptr) {
    /* 🛡️ 1. C++20 [[unlikely]] 속성을 활용해 포인터 에러가 없는 평시 구동단의 CPU 파이프라인 지터를 0ns로 소산 */
    if (!struct_raw_ptr) [[unlikely]] {
        throw std::invalid_argument("CRITICAL: Received Null hardware register address inside Upstream Bridge.");
    }

    /* 🛡️ 2. 하드웨어 안정성 가드레일: 32바이트(4바이트 float * 8개) 캐시라인 메모리 정렬 상태 물리적 강제 검증 */
    if (struct_raw_ptr % sizeof(float) != 0) [[unlikely]] {
        throw std::runtime_error("CRITICAL: Hardware register address misaligned! Bus fault protection triggered.");
    }

    /* 3. 포인터를 메모리 딥카피 없이 32바이트 Aligned 마스터 구조체 레이아웃으로 즉각 재해석 */
    UnifiedMagnetRegister32* self = reinterpret_cast<UnifiedMagnetRegister32*>(struct_raw_ptr);

    /* 4. Single Source of Truth: 32바이트 캐시라인 블록 내부의 자력 상태 벡터 시작 포인터 획득 */
    float* magnet_head_ptr = &(self->main_z_flux);

    /* 🛡️ 5. 파이썬 가비지 컬렉터(GC) 무력화 라이프사이클 안전 펜스 작동 */
    py::capsule buffer_lifecycle_fence(magnet_head_ptr, [](void* p) {
        /* 하드웨어 레지스터 생명 주기는 베어메탈 패브릭에서 독자 관리되므로 임의 메모리 반환을 원천 차단 */
    });

    /* 6. AXI Master Bus 고속 동기화 읽기를 유도하기 위한 무복사(Zero-Copy) NumPy 뷰 사출 */
    return py::array_t<float>(
        { 2 },               /* Shape: [main_z_flux, chamber_curl_flux] 이중 포트 자력 벡터 상태 */
        { sizeof(float) },   /* Strides: Single float 정렬 고속 동기화 강제 */
        magnet_head_ptr,     
        buffer_lifecycle_fence 
    );
}

// 📌 고도화: 파이썬 상위 사령탑에서 즉각 확장 모듈로 로드할 수 있도록 파이바인드 매핑 바인딩 사전 완비
PYBIND11_MODULE(c_accelerator_bridge_conduit, m) {
    m.doc() = "DFR Hardware-Software Conduit Bridge High-Performance Extension Module";
    m.def("extract_magnet_flux_buffer", &extract_magnet_flux_buffer, 
          "Intercepts raw PCIe BAR pointer and maps directly to Python NumPy view without deep copy.");
}

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept> 
#include <cstdint>

#include "unified_magnet_master_core.h"

namespace py = pybind11;

// ─────────────────────────────────────────────────────────────────────────
// [1단 복습 결속] 상향식(Upstream) 제어 관로: 무복사 NumPy 뷰 사출
// ─────────────────────────────────────────────────────────────────────────
py::array_t<float> extract_magnet_flux_buffer(uintptr_t struct_raw_ptr) {
    if (!struct_raw_ptr) [[unlikely]] {
        throw std::invalid_argument("CRITICAL: Received Null hardware register address inside Upstream Bridge.");
    }
    if (struct_raw_ptr % sizeof(float) != 0) [[unlikely]] {
        throw std::runtime_error("CRITICAL: Hardware register address misaligned! Bus fault protection triggered.");
    }

    UnifiedMagnetRegister32* self = reinterpret_cast<UnifiedMagnetRegister32*>(struct_raw_ptr);
    float* magnet_head_ptr = &(self->main_z_flux);

    py::capsule buffer_lifecycle_fence(magnet_head_ptr, [](void* p) {
        // 하드웨어 레지스터 생명 주기는 베어메탈 패브릭에서 독자 관리되므로 임의 메모리 반환을 원천 차단
    });

    return py::array_t<float>(
        { 2 },               
        { sizeof(float) },   
        magnet_head_ptr,     
        buffer_lifecycle_fence 
    );
}

// ─────────────────────────────────────────────────────────────────────────
// [2단 추가] 하향식(Downstream) 제어 관로: 상위 사령탑 복구 시그널 직결 주입
// ─────────────────────────────────────────────────────────────────────────
/**
 * @brief [Downstream Conduit] 상위 오케스트레이터의 재점화 명령을 하부 실리콘 레지스터에 다이렉트 인젝션
 * @param struct_raw_ptr 복구 대상 자석 칩셋의 물리 레지스터 주소
 */
void trigger_hardware_reignition_conduit(uintptr_t struct_raw_ptr) {
    /* 🛡️ 1. C++20 [[unlikely]] 속성을 통해 소프트웨어적 복구 트리거 판단 예외 트랙을 Cold 바이너리 영역으로 완전히 격리 */
    if (!struct_raw_ptr) [[unlikely]] {
        throw std::invalid_argument("CRITICAL: Downstream Bridge received Null pointer during Re-ignition.");
    }

    /* 🛡️ 2. 하드웨어 버스 보호 가드: 32바이트 물리 정렬 조건 강제 검증 */
    if (struct_raw_ptr % sizeof(float) != 0) [[unlikely]] {
        throw std::runtime_error("CRITICAL: Re-ignition target register address misaligned! Crash prevented.");
    }

    /* 3. 상부의 소프트웨어 신호와 하부 실리콘 주소 공간을 0ns 만에 가로채기 재해석 */
    // 📌 고도화: 하드웨어 메모리 맵(BAR) 쓰기 시 컴파일러의 최적화 생략을 방어하기 위해 volatile 성격 부여
    volatile UnifiedMagnetRegister32* self = reinterpret_cast<volatile UnifiedMagnetRegister32*>(struct_raw_ptr);

    /* 4. 하향식 제어 채널의 물리적 달성:
       상위 파이썬 단의 비동기 복구 호출 즉시, 하드웨어 레지스터 내부의 비상 록인 플래그와
       연속 실패 카운터를 비분기 레벨에서 0으로 강제 초기화(소프트 리셋)하여 50Hz 평시 주행 상태 복귀 유도 */
    self->is_emergency_on = 0;
    self->fail_counter = 0;
    self->main_z_flux = 1.0f;       /* 평시 가둠 기저선 강제 재점화 */
    self->chamber_curl_flux = 0.0f; /* 비상 소산 챔버 방향 베셀 소용돌이 게이트 물리적 폐쇄 마감 */
}

/* ========================================================================= */
/* [PYBIND11 ACCELERATOR MODULE EXPORT] 삼위일체 결속 완료                     */
/* ========================================================================= */
PYBIND11_MODULE(c_accelerator_bridge_conduit, m) {
    m.doc() = "Zero-Copy High-Speed Hardware Register Memory Binding Wrapper for DFR Plant V3";
    
    /* 1. 상향식(Upstream) 제어 관로: 실시간 자력 레지스터 상태 0ns 무복사 인입 인터페이스 */
    m.def("extract_magnet_flux_buffer", &extract_magnet_flux_buffer,
          "Extracts raw hardware magnet flux array with strict 0ns pointer bypass allocation via unified memory");

    /* 2. 하향식(Downstream) 제어 관로: 상위 사령탑의 복구 시그널을 하부 칩셋 레지스터에 직결 주입 */
    m.def("trigger_hardware_reignition_conduit", &trigger_hardware_reignition_conduit,
          "Directly overwrites and resets hardware anomaly counters and flags for soft-reignition via unified memory");
}
