import m5
from m5.objects import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--l1d_size", type=str, default="64kB")
parser.add_argument("--binary", type=str, required=True)
parser.add_argument("--l2_size", type=str, default="256kB")
parser.add_argument("--l1_assoc", type=int, default=2)
parser.add_argument("--l2_assoc", type=int, default=8)
args = parser.parse_args()

# Cache Definitions
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def __init__(self, options=None):
        super(L1Cache, self).__init__()
        if options:
            self.size = options.l1d_size if options.l1d_size else '16kB'
            self.assoc = options.l1_assoc if options.l1_assoc else 2
        pass
    
    def connectBus(self, bus):
        self.mem_side = bus.cpu_side_ports

class L1_ICache(L1Cache):
    size = '16kB' # Size icache

    def __init__(self, options=None):
        super(L1_ICache, self).__init__(options)

    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

class L1_DCache(L1Cache):
    def __init__(self, options=None):
        super(L1_DCache, self).__init__(options)
        if options and options.l1d_size:
            self.size = options.l1d_size
        else:
            self.size = '16kB' # Default

    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port

class L2Cache(Cache):
    size = '256kB'
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def __init__(self, options=None):
        super(L2Cache, self).__init__()
        if options:
            if options.l2_size:
                self.size = options.l2_size
            if options.l2_assoc:
                self.assoc = options.l2_assoc

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports


# Creating System object
system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Using RISC-V CPU
system.cpu = RiscvTimingSimpleCPU()

# Interrupt Controller
system.cpu.createInterruptController()

# Initialize Caches
system.cpu.icache = L1_ICache(args)
system.cpu.dcache = L1_DCache(args)
system.l2cache = L2Cache(args)

# Create Buses
system.l2bus = L2XBar()
system.membus = SystemXBar()

# Wiring: CPU -> L1 -> L2Bus -> L2 -> MemBus
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

# Connect system port to membus
system.system_port = system.membus.cpu_side_ports

# Memory Controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Workload setup
# Using SE mode
system.workload = SEWorkload.init_compatible(args.binary)
process = Process()
process.cmd = [args.binary]
system.cpu.workload = process
system.cpu.createThreads()

# Simulation
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Starting simulation with L1D size: {args.l1d_size}")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))