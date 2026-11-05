class ControlUnit:
    def __init__(self):
        self.instruction_register = 0
        self.program_counter = 0
        self.memory = 0 #TODO read from file
        self.instruction_set = 0
        self.halt = False
        self.instruction_decoder = 0
        self.ready = True

    def select_pc(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.program_counter + 1
        elif signal == 1:
            return self.instruction_decoder
        elif signal == 2:
            return self.instruction_set.get("addr")

    def parse_instruction(self, instruction):
        return {
            "latch_s": int(instruction[0], 2),
            "latch_pc": int(instruction[1], 2),
            "latch_sp": int(instruction[2], 2),
            "latch_rsp": int(instruction[3], 2),
            "latch_dr_alu": int(instruction[4], 2),
            "latch_dr_mem": int(instruction[5], 2),
            "latch_r": int(instruction[6], 2),
            "latch_t": int(instruction[7], 2),
            "latch_ar": int(instruction[8], 2),
            "latch_ir": int(instruction[9], 2),
            "latch_sr": int(instruction[10], 2),
            "mux_a_sel": int(instruction[11:14], 2),
            "mux_b_sel": int(instruction[14:17], 2),
            "const_sel": int(instruction[17:19], 2),
            "alu_sel": int(instruction[19:23], 2),
            "mem_sel": int(instruction[23:25], 2),
            "halt": int(instruction[25], 2),
            "cond": int(instruction[26:30], 2),
            "addr": int(instruction[30:38], 2)
        }

    def chose_next_pc(self, cond):
        cond = int(cond, 2)
        if cond == 11:
            return 2
        #TODO conditional jumps
        else:
            return 0
        

    def start(self):
        data_path = DataPath()
        memory = Memory(data_path)
        while not self.halt:
            if (not self.ready):
                continue
            self.instruction_register = self.memory[self.program_counter]
            self.instruction_set = self.parse_instruction(self.instruction_register)
            data_path.deal(self.instruction_set)
            memory.deal(self.instruction_set)
            self.program_counter = self.select_pc(self.chose_next_pc(self.instruction_set.get("cond")))
            
            