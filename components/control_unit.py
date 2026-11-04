class ControlUnit:
    def __init__(self):
        self.instruction_register = 0
        self.programm_counter = 0
        self.memory = 0 #TODO read from file
        self.instruction_set = parse_instruction(self.instruction_register)
        self.halt = False
        self.instruction_decoder = 0
        self.ready = True

    def select_pc(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.programm_counter + 1
        elif signal == 1:
            return self.instruction_decoder
        elif signal == 2:
            return self.instruction_set.get("addr")

    def parse_instruction(self, instruction):
        return {
            "latch_s": instruction[0],
            "latch_pc": instruction[1],
            "latch_sp": instruction[2],
            "latch_rsp": instruction[3],
            "latch_dr_alu": instruction[4],
            "latch_dr_mem": instruction[5],
            "latch_r": instruction[6],
            "latch_t": instruction[7],
            "latch_ar": instruction[8],
            "latch_ir": instruction[9],
            "latch_sr": instruction[10],
            "mux_a_sel": instruction[11:14],
            "mux_b_sel": instruction[14:17],
            "const_sel": instruction[17:19],
            "alu_sel": instruction[19:23],
            "mem_sel": instruction[23:25],
            "halt": instruction[25],
            "cond": instruction[26:30],
            "addr": instruction[30:38]
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
            self.instruction_register = self.memory[self.programm_counter]
            self.instruction_set = self.parse_instruction(self.instruction_register)
            data_path.deal(self.instruction_set)
            memory.deal(self.instruction_set)
            self.programm_counter = self.select_pc(self.chose_next_pc(self.instruction_set.get("cond")))
            
            