/**
 * @file unified_magnet_master_core.h
 * @brief [최종 마스터] 챔버 독립 포트 대응 전 구간 자석 공용 통합 커널
 * @details 하드웨어 물리 핀 설정에 따라 자신이 [일반 구역]인지 [챔버 직전 구역]인지 자율 판별하며,
 *          이중 드라이버 자석 세트 하드웨어 사양에 맞춰 두 개의 와이어 출력을 동시에 통제합니다.
 */

#ifndef UNIFIED_MAGNET_MASTER_CORE_H
#define UNIFIED_MAGNET_MASTER_CORE_H

#include <stdint.h>
#include <string.h>

/* ========================================================================= */
/* [MASTER SHIELD ALIGNED STRUCT]                                            */
/* ========================================================================= */
typedef struct {
    float main_z_flux;         /* 포트 1 직결: 평시 Z축 주행 가둠 자기장 상태 벡터 */
    float chamber_curl_flux;   /* 포트 2 직결: 비상 챔버 대각선 흡입 소용돌이 자기장 상태 벡터 */
    float p00_shield;          /* 조셉 폼(Joseph Form) 기반 수치해석적 음수반전 방어벽 */
    uint32_t fail_counter;     /* 상류 노드로부터 유입된 -99.0f 연속 누적 카운터 */
    uint32_t is_emergency_on;  /* 0: 평시 50Hz 정속 제어 모드 | 1: 비상 시퀀스 집행 모드 */
    uint8_t reserved[12];      /* AXI Master Bus 버스트 및 strict 32바이트 정렬 마감용 방화벽 */
} UnifiedMagnetRegister32;

_Static_assert(sizeof(UnifiedMagnetRegister32) == 32, "CRITICAL ERROR: Size mismatch on unified master cacheline!");

/* ========================================================================= */
/* [BRANCHLESS REAL-TIME MUX]                                                */
/* ========================================================================= */
static inline uint32_t uni_branchless_select_u32(uint32_t condition, uint32_t true_val, uint32_t false_val) {
#pragma HLS INLINE
    uint32_t mask = -(condition != 0);
    return (true_val & mask) | (false_val & ~mask);
}

static inline float uni_branchless_select_float(uint32_t condition, float true_val, float false_val) {
#pragma HLS INLINE
    uint32_t true_bits, false_bits, final_bits;
    __builtin_memcpy(&true_bits, &true_val, sizeof(float));
    __builtin_memcpy(&false_bits, &false_val, sizeof(float));
    final_bits = uni_branchless_select_u32(condition, true_bits, false_bits);
    float final_val;
    __builtin_memcpy(&final_val, &final_bits, sizeof(float));
    return final_val;
}

/* ========================================================================= */
/* [CORE OPERATIONAL MATRIX PROCESSOR]                                       */
/* ========================================================================= */
/**
 * @brief 전 구간 자석 및 챔버 독립 포트 공용 통제 엔진
 * @param self 마스터 레지스터 구조체 포인터
 * @param upstream_signal 상류에서 실시간 하드와이어 전선으로 타고 들어온 전하 신호
 * @param is_chamber_node 0: 일반 위치 자석 노드 | 1: 챔버 직전 자석 노드 (물리 핀 바인딩 대상)
 * @param cos_50hz 50Hz 그리드 동기화 코사인 테이블 값
 * @param sin_50hz 50Hz 그리드 동기화 사인 테이블 값
 */
static inline void unified_magnet_master_process(
    UnifiedMagnetRegister32* const self,
    float upstream_signal,
    uint32_t is_chamber_node,
    float cos_50hz,
    float sin_50hz
) {
#pragma HLS INLINE
#pragma HLS DATA_PACK variable=self

    /* 1. 상류 결함 토큰(-99.0f) 및 아노말리 비분기 탐지 */
    uint32_t is_nan = (upstream_signal != upstream_signal);
    uint32_t is_over = (upstream_signal > 1e6f) || (upstream_signal < -1e6f);
    uint32_t is_dead = (upstream_signal == -99.0f);
    uint32_t is_anomaly = is_nan | is_over | is_dead;

    /* 2. 무분기 카운터 누적 및 비상 상태 전체 록인(Lock-in) */
    self->fail_counter = uni_branchless_select_u32(is_anomaly, self->fail_counter + 1, 0);
    uint32_t trigger_emergency = (self->fail_counter >= 5) || (self->is_emergency_on == 1);
    self->is_emergency_on = uni_branchless_select_u32(trigger_emergency, 1, 0);

    /* 3. 평시 50Hz 정속 파도타기 및 파데 노치 필터 수리 계산 */
    float main_z_pred = (cos_50hz * self->main_z_flux) - (sin_50hz * self->chamber_curl_flux);
    float curl_pred   = (sin_50hz * self->main_z_flux) + (cos_50hz * self->chamber_curl_flux);

    float K_gain = self->p00_shield / (self->p00_shield + 1.0f);
    float ImKH = 1.0f - K_gain;
    self->p00_shield = (ImKH * self->p00_shield * ImKH) + (K_gain * 1.0f * K_gain);

    float scaled_energy = (main_z_pred * main_z_pred) + (curl_pred * curl_pred);
    float noise_notch = (6.0f * scaled_energy) / (12.0f + (scaled_energy * scaled_energy));
    float normal_flux_output = main_z_pred + (K_gain * (upstream_signal - main_z_pred)) * noise_notch;

    /* 4. 📌 비상 발동 시: 위치 핀(is_chamber_node) 세라믹 마킹에 따른 역할 분담 집행 */
    
    /* [분기 1] 일반 노드(0)일 때의 비상 출력 설정: 챔버 자력은 0, 직진축 최대 가속(Hz Max Up) */
    float gen_emergency_z = 1.5f; /* 강력한 후방 청소 펌핑 */
    float gen_emergency_curl = 0.0f;

    /* [분기 2] 챔버 노드(1)일 때의 비상 출력 설정: 직진 차단(0), 대각선 소용돌이 게이트 최대 개방 */
    float cham_emergency_z = 0.0f; /* 고장 구역 전방 가상 격벽 형성 */
    float cham_emergency_curl = -curl_pred * 2.0f; /* 챔버 흡입 유도 */

    /* 하드웨어 핀 마킹 기준 일차 취합 (MUX) */
    float target_emergency_z = uni_branchless_select_float(is_chamber_node, cham_emergency_z, gen_emergency_z);
    float target_emergency_curl = uni_branchless_select_float(is_chamber_node, cham_emergency_curl, gen_emergency_curl);

    /* 5. 최종 운전 상태 스왑 및 이중 포트 레지스터 갱신 (0ns 와이어 사출 준비 마감) */
    self->main_z_flux = uni_branchless_select_float(self->is_emergency_on, target_emergency_z, normal_flux_output);
    self->chamber_curl_flux = uni_branchless_select_float(self->is_emergency_on, target_emergency_curl, curl_pred);
}

#endif /* UNIFIED_MAGNET_MASTER_CORE_H */
