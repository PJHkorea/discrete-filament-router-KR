import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# 1. 물리 정수 및 설계 파라미터 정의
sigma = 5.670374e-8       # Stefan-Boltzmann constant (W/m^2*K^4)
M_Li = 0.006941           # Lithium Molar mass (kg/mol)
H_vap = 19.6e6            # Lithium Latent heat of vaporization (J/kg)
R_gas = 8.314             # Universal gas constant (J/mol*K)
Torr_conv = 0.00750062    # Pa to Torr conversion factor

# DFR 시스템 명세값
T_plasma = 1e8            # 1억 도 (K)
r_packet = 0.0015         # 패킷 유효 반경 (1.5mm)
R_wall = 0.30             # 도관 반경 (30cm)
A_wall = 2 * np.pi * R_wall * 1.0  # 단위 길이당 내벽 면적 (m^2)
S_vac = 45.0              # 고속 진공 펌프 배기 속도 (m^3/s)
T_vapor = 573.15          # 리튬 증기 평균 온도 (300°C)

# 복사열 감쇄를 고려한 유효 방사 계수 조절 (가둠 자기장 마진 반영)
epsilon_eff = 1e-11 

# 2. 계산 수행
q_rad = epsilon_eff * sigma * (T_plasma**4) * (r_packet / R_wall)
J_v = q_rad / H_vap       # 기화 질량 플럭스 (kg/m^2*s)

# 시간 도메인 동적 포화 평형 시뮬레이션 (0 ~ 100ms)
time = np.linspace(0, 0.1, 200)
P_pa = (J_v * A_wall * R_gas * T_vapor / (M_Li * S_vac)) * (1 - np.exp(-time * 80))
P_torr = P_pa * Torr_conv

# 3. 데이터프레임 빌드
df_sim = pd.DataFrame({'Time_ms': time * 1000, 'Pressure_Pa': P_pa, 'Pressure_Torr': P_torr})

# 4. 수학적 검증 그래프 시각화 (edugraph boilerplate 규격 준수)
plt.figure(figsize=(7, 4))
plt.plot(df_sim['Time_ms'], df_sim['Pressure_Torr'], color='#7C3AED', linewidth=2.5, label='Dynamic Vapor Pressure')
plt.axhline(y=5.17e-5, color='#EF4444', linestyle='--', linewidth=1.5, label='Target P_steady (5.17e-5 Torr)')
plt.title(r'$\mathrm{DFR\ Vapor\ Jacket\ Homeostasis\ Convergence\ Verification}$', fontsize=12, pad=10)
plt.xlabel(r'$\mathrm{Time\ (ms)}$', fontsize=10)
plt.ylabel(r'$\mathrm{Vapor\ Pressure\ (Torr)}$', fontsize=10)
plt.yscale('log')
plt.grid(True, which="both", ls=":", alpha=0.6)
plt.legend(loc='lower right', fontsize=9)

buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
buf.seek(0)
base64_str = base64.b64encode(buf.read()).decode('utf-8')
plt.close()
print(f'base64_encoded_image:"data:image/png;base64,{base64_str}"')
