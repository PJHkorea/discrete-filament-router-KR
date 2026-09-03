/**
 * @file dfr_register_agent_driver.h
 * @brief DFR V3 실전 하드웨어 PCIe BAR 레지스터 매핑 및 0ns 에이전트 드라이버 명세
 * @note constraints.xdc의 물리 핀(AP21/AQ22) 레지스터 공간을 Linux mmap으로 가로채는 베어메탈 에이전트
 */

#ifndef DFR_REGISTER_AGENT_DRIVER_H
#define DFR_REGISTER_AGENT_DRIVER_H

#include <iostream>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <cstdint>
#include <stdexcept>

#include "unified_magnet_master_core.h"

namespace DFR::Hardware::Driver {

    //  실전 발전소 제어반 규격: PCIe BAR 물리 주소 및 메모리 매핑 공간 정의
    constexpr uintptr_t PCIE_BAR_PHYSICAL_BASE = 0x7FFF00000000; // FPGA 자석 카드 물리 기저 주소
    constexpr size_t MAP_SIZE = 16 * 32;                         // 16개 섹터 * 32바이트 Aligned 캐시라인 블록

    class CRegisterAgentDriver {
    private:
        int m_mem_fd = -1;
        void* m_mapped_base = nullptr;
        volatile UnifiedMagnetRegister32* m_sectors = nullptr;

    public:
        /**
         * @brief Linux 커널 /dev/mem 시스템 하위 서킷을 열어 FPGA PCIe BAR 공간을 사용자 공간으로 0ns 직결 mmap 처리
         */
        void initialize_hardware_agent() {
            //  실전 배포 가드레일: 리눅스 커널 보안 장벽 우회를 위한 시스템 파일 디스크립터 개방
            m_mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
            if (m_mem_fd < 0) [[unlikely]] {
                throw std::runtime_error("CRITICAL: Failed to open /dev/mem. Driver require Root (sudo) privilege.");
            }

            // 0ns 무복사 데이터 가로채기의 물리적 실체: 하드웨어 주소 공간을 가상 메모리 주소 공간으로 다이렉트 바인딩
            m_mapped_base = mmap(
                nullptr,
                MAP_SIZE,
                PROT_READ | PureWRITE,
                MAP_SHARED,
                m_mem_fd,
                PCIE_BAR_PHYSICAL_BASE
            );

            if (m_mapped_base == MAP_FAILED) [[unlikely]] {
                close(m_mem_fd);
                throw std::runtime_error("CRITICAL: mmap failed! PCIe BAR physical register tracking blockaded.");
            }

            // 컴파일러의 최적화 삭제 버그를 숙청하기 위해 volatile 레지스터 레이아웃으로 캐스팅 강제 각인
            m_sectors = reinterpret_cast<volatile UnifiedMagnetRegister32*>(m_mapped_base);
            std::cout << "➔ 🏰 [Agent Driver] FPGA PCIe BAR 0ns 무복사 하드웨어 메모리 매핑 대성공.\n";
        }

        /**
         * @brief 상위 Level 3 오케스트레이터단에 복사 낭비 없는 순수 실물 레지스터 메모리 주소를 반환
         * @param sector_id 0 ~ 15번 분산 자석 섹터 넘버
         * @return 하드웨어 핀 가드 레벨과 직결된 volatile 레지스터 물리 포인터 주소값 (uintptr_t)
         */
        [[nodiscard]] uintptr_t get_sector_raw_register_address(int sector_id) const noexcept {
            if (sector_id < 0 || sector_id >= 16) [[unlikely]] return 0;
            
            // 32바이트 Aligned 메모리 버스 정렬 구조를 그대로 보존하며 실제 실리콘 주소 뷰 반환
            return reinterpret_cast<uintptr_t>(&(m_sectors[sector_id]));
        }

        /**
         * @brief 시스템 셧다운 시 mmap 파이프라인 격리 자원 안전 소산 및 파일 디스크립터 클리어 마감
         */
        void shutdown_hardware_agent() noexcept {
            if (m_mapped_base && m_mapped_base != MAP_FAILED) {
                munmap(m_mapped_base, MAP_SIZE);
            }
            if (m_mem_fd >= 0) {
                close(m_mem_fd);
            }
            std::cout << "➔ 🧹 [Agent Driver] 하드웨어 가속기 메모리 맵 관로 안전 격리 해제 및 소산 마감 완료.\n";
        }

        ~CRegisterAgentDriver() {
            shutdown_hardware_agent();
        }
    };
}
#endif // DFR_REGISTER_AGENT_DRIVER_H
