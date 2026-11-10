#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <mach/mach.h>
#include <stdbool.h>

struct cpu {
  host_t host;
  host_cpu_load_info_data_t previous;
  bool ready;
  char command[256];
};

static inline void cpu_init(struct cpu* cpu) {
  cpu->host = mach_host_self();
  cpu->ready = false;
  cpu->command[0] = '\0';
}

static inline void cpu_update(struct cpu* cpu) {
  host_cpu_load_info_data_t current;
  mach_msg_type_number_t count = HOST_CPU_LOAD_INFO_COUNT;
  cpu->command[0] = '\0';
  if (host_statistics(cpu->host, HOST_CPU_LOAD_INFO, (host_info_t)&current, &count) != KERN_SUCCESS) return;
  if (cpu->ready) {
    uint32_t user = current.cpu_ticks[CPU_STATE_USER] - cpu->previous.cpu_ticks[CPU_STATE_USER];
    uint32_t system = current.cpu_ticks[CPU_STATE_SYSTEM] - cpu->previous.cpu_ticks[CPU_STATE_SYSTEM];
    uint32_t nice = current.cpu_ticks[CPU_STATE_NICE] - cpu->previous.cpu_ticks[CPU_STATE_NICE];
    uint32_t idle = current.cpu_ticks[CPU_STATE_IDLE] - cpu->previous.cpu_ticks[CPU_STATE_IDLE];
    double total = (double)user + system + nice + idle;
    if (total > 0) {
      double busy = ((double)user + system + nice) / total;
      const char* color = getenv(busy >= .7 ? "RED" : busy >= .3 ? "ORANGE" : busy >= .1 ? "YELLOW" : "LABEL_COLOR");
      snprintf(cpu->command, sizeof(cpu->command), "--set cpu.percent label=%.0f%% label.color=%s",
               busy * 100, color ? color : "0xfffbfbf9");
    }
  }
  cpu->previous = current;
  cpu->ready = true;
}
