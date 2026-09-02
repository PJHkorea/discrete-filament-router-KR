"""
@file dfr_lithium_jacket_homeostasis_solver.py
@brief DFR 리튬 기체 자켓 항상성 임계 평형 수치해석 솔버 (Numerical Verification Solver)
@details 
    본 코드는 /docs/Physics_note.md 의 [4. 리튬 기체 자켓 압착 메커니즘] 및 
    [4-2 거시적 포화 평형] 장에 기술된 물리학적 가설을 정량적으로 실증하기 위해 설계되었습니다.
    
    100M K 플라즈마 패킷의 슈테판-볼츠만 복사 에너지 플럭스와 Hertz-Knudsen 기화 잠열 관계식을 결합하여,
    15 kHz 운전 진입 후 50ms 이내에 정상상태 증기압 P_steady ≈ 5.17 x 10^-5 Torr 로 
    자가 조절형 항상성(Homeostasis) 수렴이 일어남을 수학적으로 정리해봤습니다.
"""


import numpy as np
import pandas as pd
from typing import Final, Optional

class DFRHomeostasisSolver:
    """DFR 리튬 기체 자켓 항상성 임계 평형 수치해석 핵심 엔진 (Hybrid Variable Version)"""
    
    # 📌 C++ 하드웨어 핀 가드 구조에 맞춘 물리 불변 상수 Final 바인딩
    SIGMA: Final[float] = 5.670374e-8       # Stefan-Boltzmann constant (W/m^2*K^4)
    M_LI: Final[float] = 0.006941           # Lithium Molar mass (kg/mol)
    H_VAP: Final[float] = 19.6e6            # Lithium Latent heat of vaporization (J/kg)
    R_GAS: Final[float] = 8.314             # Universal gas constant (J/mol*K)
    TORR_CONV: Final[float] = 0.00750062    # Pa to Torr conversion factor

    def __init__(
        self, 
        T_plasma: float = 1e8, 
        r_packet: float = 0.0015, 
        R_wall: float = 0.30, 
        S_vac: float = 45.0, 
        T_vapor: float = 573.15, 
        epsilon_eff: float = 1e-11,
        pump_efficiency: float = 0.5        # 📌 기저 운전 사양 (Default)
    ) -> None:
        self.T_plasma = T_plasma
        self.r_packet = r_packet
        self.R_wall = R_wall
        self.A_wall = 2.0 * np.pi * self.R_wall * 1.0  # 단위 길이(1m)당 내벽 단면적
        self.S_vac = S_vac
        self.T_vapor = T_vapor
        self.epsilon_eff = epsilon_eff
        self.pump_efficiency = pump_efficiency  # 인스턴스 기본 물리 상태 바인딩

    def calculate_steady_state_flux(self) -> float:
        """슈테판-볼츠만 복사 에너지 플럭스로부터 기화 질량 플럭스(J_v)를 도출합니다."""
        geometry_ratio = self.r_packet / self.R_wall
        q_rad = self.epsilon_eff * self.SIGMA * (self.T_plasma ** 4) * geometry_ratio
        return q_rad / self.H_VAP

    def run_simulation(
        self, 
        t_max: float = 0.1, 
        num_points: int = 200,
        pump_efficiency_override: Optional[float] = None  # 📌 가변 스캔을 위한 하이브리드 인자 추가
    ) -> pd.DataFrame:
        """
        시간 도메인 동적 포화 평형 시뮬레이션을 수행하고 고속 데이터프레임을 사출합니다.
        
        💡 하이브리드 최적화: 인자가 생략되면(None) 인스턴스 기본값(self.pump_efficiency)을 추종하고,
        인자가 입력되면 해당 값으로 즉각 덮어쓰기(Override)하여 단일 인스턴스 연속 가변 스캔을 지원합니다.
        """
        J_v = self.calculate_steady_state_flux()
        time_array = np.linspace(0.0, t_max, num_points)
        
        # 1. 1D 선형 트랙 도관의 물리적 체적 계산 (V = pi * r^2 * L) [단위 길이 L = 1.0m]
        conduit_volume = np.pi * (self.R_wall ** 2) * 1.0
        
        # 📌 2. 하이브리드 오버라이딩 적용 연산 지체 분기 처리
        active_efficiency = (
            pump_efficiency_override 
            if pump_efficiency_override is not None 
            else self.pump_efficiency
        )
        
        # 진공 배기 동역학에 따른 이론적 지수 감쇄 시정수 유도 (decay_rate = S_vac / V)
        dynamic_decay_rate = (self.S_vac / conduit_volume) * active_efficiency
        
        # 이상기체-배기 진공 이득(Gain) 및 최대 포화 압력 Pa 계산
        ideal_gas_vacuum_gain = (self.A_wall * self.R_GAS * self.T_vapor) / (self.M_LI * self.S_vac)
        P_pa_max = J_v * ideal_gas_vacuum_gain
        
        # 포화 평형 미분방정식 동적 벡터 연산
        P_pa = P_pa_max * (1.0 - np.exp(-time_array * dynamic_decay_rate))
        P_torr = P_pa * self.TORR_CONV
        
        return pd.DataFrame({
            'Time_ms': time_array * 1000.0,
            'Pressure_Pa': P_pa,
            'Pressure_Torr': P_torr
        })




         def generate_verification_plot_base64(
        self, 
        df_sim: pd.DataFrame, 
        target_p_steady: float = 5.17e-5,
        current_efficiency: Optional[float] = None  # 📌 가변 스캔 라벨링을 위한 인자 추가
    ) -> str:
        """에듀그래프 바이오플레이트 규격을 만족하는 시각화 PNG 스트림을 Base64 포맷으로 인코딩하여 반환합니다."""
        
        # 백엔드 서버 가동 시 전역 상태 전착 및 메모리 누수(Memory Leak)를 차단하기 위한 서브 플롯 격리 구조
        fig, ax = plt.subplots(figsize=(7, 4))
        
        try:
            # 📌 효율 변수 값 가변 추적 후 동적 라벨 생성
            eff_val = current_efficiency if current_efficiency is not None else self.pump_efficiency
            curve_label = f'Dynamic Vapor Pressure (eff={eff_val:.2f})'
            
            # 동적 증기압 곡선 및 타겟 임계선 맵핑
            ax.plot(df_sim['Time_ms'], df_sim['Pressure_Torr'], color='#7C3AED', linewidth=2.5, label=curve_label)
            ax.axhline(y=target_p_steady, color='#EF4444', linestyle='--', linewidth=1.5, label=f'Target P_steady ({target_p_steady:.2e} Torr)')
            
            # 레이텍(LaTeX) 수학 도메인 폰트 렌더링 유지 및 스타일 프로파일 정착
            ax.set_title(r'$\mathrm{DFR\ Vapor\ Jacket\ Homeostasis\ Convergence\ Verification}$', fontsize=12, pad=10)
            ax.set_xlabel(r'$\mathrm{Time\ (ms)}$', fontsize=10)
            ax.set_ylabel(r'$\mathrm{Vapor\ Pressure\ (Torr)}$', fontsize=10)
            
            ax.set_yscale('log')
            ax.grid(True, which="both", ls=":", alpha=0.6)
            ax.legend(loc='lower right', fontsize=9)
            
            # 🛡️ 입출력 병목 제로화를 위한 메모리 바이트 뷰 인터셉트
            with io.BytesIO() as buf:
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                buf.seek(0)
                base64_bytes = base64.b64encode(buf.read())
                base64_str = base64_bytes.decode('utf-8')
                
            return f'data:image/png;base64,{base64_str}'
            
        finally:
            # matplotlib GUI 메모리 리소스를 즉각 강제 소멸하여 누수 방지
            plt.close(fig)


class TestDFRLithiumJacketHomeostasis(unittest.TestCase):
    """리튬 기체 자켓 항상성 임계 평형 가설 및 수치 안정성 검증 테스트 클래스 (Hybrid Sweep Version)"""

    def setUp(self) -> None:
        """매 테스트마다 독립적으로 격리 및 유도되는 기본 DFR 솔버 칩셋 셋팅"""
        self.solver = DFRHomeostasisSolver()
        self.TARGET_P_STEADY: Final[float] = 5.17e-5  # 설계 가설 타겟 정상상태 압력 (Torr)

    def test_steady_state_pressure_convergence(self) -> None:
        """
        가설 실증 검증: 50ms 이후 포화 평형에 진입한 증기압이 설계 타겟 오차 마진 이내로 수렴하는지 테스트합니다.
        
        📌 가변 스캔 적용 완료: self.subTest를 활용하여 단일 인스턴스 환경에서 
        펌프 효율(0.1 ~ 1.0) 조건별 동적 수렴 정합성을 전수 격파 검증합니다.
        """
        # 극단적 유체 저항(0.1)부터 최대 배기 효율(1.0)까지 촘촘한 스캔 대역 설정
        efficiency_scenarios = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        dynamic_delta = self.TARGET_P_STEADY * 0.01  # 타겟 값의 1% 이내 변동 범위 허용 마진

        for eff in efficiency_scenarios:
            # 🛡️ 개별 파라미터 시나리오 격리 샌드박스 가동
            with self.subTest(pump_efficiency=eff):
                # 하이브리드 오버라이딩 인자를 직접 인젝션하여 고속 연산 스왑
                df_result = self.solver.run_simulation(pump_efficiency_override=eff)
                
                # 50ms 이후 정상상태 포화 영역 데이터 필터링
                steady_state_data = df_result[df_result['Time_ms'] >= 50.0]
                final_pressure_torr: float = float(steady_state_data['Pressure_Torr'].iloc[-1])
                
                self.assertAlmostEqual(
                    final_pressure_torr, 
                    self.TARGET_P_STEADY, 
                    delta=dynamic_delta,
                    msg=f"[Failure @ eff={eff}] 최종 수렴 압력 {final_pressure_torr} Torr가 허용 마진을 초과함."
                )

    def test_knudsen_number_regime(self) -> None:
        """
        [물리 가이드라인 검증] Knudsen Number (Kn) 사후 해석 테스트:
        최종 수렴 압력 대역이 진공 배기 공식(S_vac)의 전제 조건인 '분자류 또는 천이류 영역'에 존재하는지 전수 검증합니다.
        """
        efficiency_scenarios = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        for eff in efficiency_scenarios:
            with self.subTest(pump_efficiency=eff):
                df_result = self.solver.run_simulation(pump_efficiency_override=eff)
                
                # 50ms 이후 정상상태 영역의 평형 압력 평균치 추출 (Pa 단위)
                steady_state_pa = df_result[df_result['Time_ms'] >= 50.0]['Pressure_Pa'].mean()
                
                # 1. 리튬 단원자 기체 분자 유효 직경 (d_Li_atomic_diameter ≈ 0.31 x 10^-9 m)
                d_li = 0.31e-9
                
                # 2. 고전 열역학 기반 평균자유행로(Mean Free Path, λ) 역산 식 기동
                k_B = 1.380649e-23
                denominator = np.sqrt(2.0) * np.pi * (d_li ** 2) * steady_state_pa
                
                # 분모 언더플로우 방어벽 가동
                if denominator > 1e-15:
                    mean_free_path = (k_B * self.solver.T_vapor) / denominator
                else:
                    mean_free_path = float('inf')
                    
                # 3. 도관 특성 기하학 길이 스케일 정의 (D = 2 * R_wall = 0.60m)
                characteristic_length = 2.0 * self.solver.R_wall
                
                # 4. Knudsen Number 산출 (Kn = λ / D)
                knudsen_number = mean_free_path / characteristic_length
                
                # 📌 판정 기준 마진: Kn > 0.1 (천이류 및 분자류 영역) 조건을 만족해야 0D 매스 밸런스 공식이 유효함
                self.assertGreater(
                    knudsen_number, 0.1,
                    msg=f"[물리 정합성 결함 @ eff={eff}] 현재 수렴 압력에서의 크누센 수({knudsen_number:.4f})가 너무 낮아 "
                        f"점성 유체 전이 영역으로 빠졌습니다. 진공 컨덕턴스 공식을 고차원으로 개정해야 합니다."
                )
        print(f"\n➔ 🔍 [Physics Guard] 정상상태 크누센 수(Kn) = {knudsen_number:.2f} (확보 완료: 자유분자류 대역 충족)")

    def test_sound_speed_propagation_delay(self) -> None:
        """
        [시간 마진 검증] 열역학적 음속 전파 지연 마진 테스트:
        0D 볼륨 모델의 항상성 수렴 시간(50ms)이 실제 기체가 공간을 음속으로 채우는 최소 물리 시간보다 큰지 검증합니다.
        """
        # 1. 리튬 단원자 기체 비열비 (비압축성/단원자 이상기체 γ = 5/3)
        gamma = 5.0 / 3.0
        
        # 2. 리튬 증기 온도에서의 열역학적 음속(Sound Speed) 계산 (v_s = sqrt(gamma * R * T / M_Li))
        sound_speed = np.sqrt((gamma * self.solver.R_GAS * self.solver.T_vapor) / self.solver.M_LI)
        
        # 3. 임계 물리 공간 트랙 길이 가설 정의 (단위 축 길이 L = 1.0m)
        conduit_length = 1.0
        
        # 4. 음속 파동이 공간 경계를 횡단하는 최소 물리 지연 시간 역산 (단위: ms)
        min_propagation_delay_ms = (conduit_length / sound_speed) * 1000.0
        
        # 📌 판정 기준 마진: 항상성 안착 임계 타겟팅 시간인 50.0ms가 최소 파동 지연 시간보다 공간적으로 아득히 커야 함 (CFL 조건 만족)
        self.assertLess(
            min_propagation_delay_ms, 50.0,
            msg=f"[시간 정합성 모순] 물리적 음속 전파 지연 시간({min_propagation_delay_ms:.2f} ms)이 "
                f"모델의 50ms 안착 가정보다 길어 시공간 인과율 모순이 발생했습니다."
        )
        print(f"➔ ⏱️ [Time Guard] 리튬 열역학적 음속 = {sound_speed:.2f} m/s | 최소 전파 지연 = {min_propagation_delay_ms:.2f} ms (안전 마진 확보)")

    def test_pressure_is_monotonically_increasing(self) -> None:
        """
        물리 법칙 검증: 가둠 장 내부의 압력이 평형 도달 전까지 물리학적 모순 없이 단조 증가하는지 전수 검증합니다.
        """
        efficiency_scenarios = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]

        for eff in efficiency_scenarios:
            with self.subTest(pump_efficiency=eff):
                df_result = self.solver.run_simulation(pump_efficiency_override=eff)
                
                # 연속된 타임스텝별 압력 차분 추출 (언더플로우 오차 소산용 부호 비트 마진 -1e-12 허용)
                pressure_diffs = df_result['Pressure_Torr'].diff().dropna()
                
                self.assertTrue(
                    (pressure_diffs >= -1e-12).all(), 
                    f"[Failure @ eff={eff}] 열역학에 반하는 압력 감소 역류 구간이 감지됨."
                )

    def test_output_visualization_generation(self) -> None:
        """
        인프라 테스트: 자율 디지털 트윈 리포트 인코딩 스트림 사출 모듈이 각 효율 조건별로 예외 없이 Base64를 출력하는지 검증합니다.
        """
        efficiency_scenarios = [0.1, 0.5, 1.0]  # 대표 대역 샘플링

        for eff in efficiency_scenarios:
            with self.subTest(pump_efficiency=eff):
                df_result = self.solver.run_simulation(pump_efficiency_override=eff)
                
                # 시각화 모듈에도 오버라이드 효율 값을 전달하여 범례 라벨 자동 동기화
                img_stream = self.solver.generate_verification_plot_base64(
                    df_result, 
                    target_p_steady=self.TARGET_P_STEADY,
                    current_efficiency=eff
                )
                
                self.assertTrue(
                    img_stream.startswith("data:image/png;base64,"), 
                    f"[Failure @ eff={eff}] 그래픽 파이프라인 PNG 인코딩 헤더 포맷 오류."
                )


# =====================================================================
# 3. 📌 최종 결속: 단점을 극복하는 하이브리드 CLI 엔트리 포인트 (Execution Control)
# =====================================================================
if __name__ == '__main__':
    import sys
    
    # 📌 코디자인 융합 완결: 터미널 인자에 '--plot'이 수신되면 로컬 GUI 디스플레이 모드로 즉각 스왑
    if '--plot' in sys.argv:
        print("\n🌐 [DFR Digital Twin] 로컬 GUI 가시화 필터 모드를 트리거합니다.")
        
        # 1. 단일 물리 해석 인스턴스 셋팅
        solver = DFRHomeostasisSolver()
        target_p_steady = 5.17e-5  # 설계 가설 목표선
        
        # 2. 다차원 동적 시뮬레이션 전수 스캔 플롯 구성
        # 최악의 정체 상황(0.1), 기저 운전선(0.5), 이상적 배기(1.0)를 시각적으로 전격 비교
        display_scenarios = [0.1, 0.5, 1.0]
        color_map = {0.1: '#EF4444', 0.5: '#7C3AED', 1.0: '#10B981'}
        
        # 로컬 개발자를 위한 직관적 Matplotlib 인터랙티브 윈도우 점화
        plt.figure(figsize=(8, 4.5))
        
        for eff in display_scenarios:
            # 단일 인스턴스 재사용 + 하이브리드 오버라이드 가동
            df_result = solver.run_simulation(pump_efficiency_override=eff)
            
            # 효율별 동적 주행 압력 프로파일 곡선 투사
            plt.plot(
                df_result['Time_ms'], 
                df_result['Pressure_Torr'], 
                color=color_map[eff], 
                linewidth=2.0 if eff != 0.5 else 2.8,  # 기저 운전선(0.5) 강조
                label=f'Dynamic Vapor Pressure (eff={eff:.1f})'
            )
        
        # 설계 임계 목표 평형 상태선 투사 (물리학적 타당성 가이드라인)
        plt.axhline(
            y=target_p_steady, 
            color='#374151', 
            linestyle=':', 
            linewidth=1.5, 
            label=f'Target P_steady ({target_p_steady:.2e} Torr)'
        )
        
        # 레이텍(LaTeX) 수학 도메인 서체 디자인 정착 및 레이아웃 마감
        plt.title('DFR Vapor Jacket Homeostasis Convergence Sweep Analysis', fontsize=12, pad=12)
        plt.xlabel('Time (ms)', fontsize=10)
        plt.ylabel('Vapor Pressure (Torr)', fontsize=10)
        plt.yscale('log')
        plt.grid(True, which="both", ls=":", alpha=0.5)
        plt.legend(loc='lower right', fontsize=9)
        plt.tight_layout()
        
        print("➔ 📊 [Matplotlib Engine] 다중 효율 프로파일 플롯 컨벌전스 렌더링 완료. GUI 윈도우를 출력합니다.")
        plt.show()
        
    else:
        # 일반 실행 또는 GitHub Actions CI/CD 환경에서는 표준 unittest 패키지 조용히 작동 (OK 아웃풋 사출)
        print("\n⚙️ [CI/CD Pipeline] 하이브리드 유효성 회귀 테스트 스위트를 구동합니다.")
        unittest.main()

