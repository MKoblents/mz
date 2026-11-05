from typeguard import value


class DataPath:
    def __init__(self):
        self.second=0
        self.program_counter=0
        self.stack_pointer=4096 #TODO ?
        self.return_stack_pointer=5000 #TODO ?
        self.data_register=0
        self.return_register=0
        self.top=0
        self.address_register=0
        self.instruction_register=0
        self.const=0
        self.status_register=0

    def select_a(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.sign_extend(self.instruction_register)
        elif signal == 1:
            return self.second
        elif signal == 2:
            return self.program_counter
        elif signal == 3:
            return self.stack_pointer
        elif signal == 4:
            return self.return_stack_pointer
        elif signal == 5:
            return self.data_register

    def sign_extend(self, value:bytes):
        x=value[24]
        return x*8+value[24:] #TODO

    def select_b(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.data_register
        elif signal == 1:
            return self.return_register
        elif signal == 2:
            return self.top
        elif signal == 3:
            return self.const #TODO
        elif signal == 4:
            return self.address_register

    def select_constant(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return 0
        elif signal == 1:
            return 1
        elif signal == 2:
            return 4
        elif signal == 3:
            return 8
        
    def select_alu(self, signal, A, B):
        signal = int(signal, 2)
        if signal == 0:
            return A + B
        elif signal == 1:
            return A - B
        elif signal == 2:
            return A * B
        elif signal == 3:
            return A // B
        elif signal == 4:
            return A % B
        elif signal == 5:
            return A & B
        elif signal == 6:
            return A | B
        elif signal == 7:
            return A ^ B
        elif signal == 8:
            return A
        elif signal == 9:
            return B
        #TODO shifts
        #TODO flags
    
    def deal(self, instruction_set):
        self.const = self.select_constant(instruction_set.get("const_sel"))
        res = self.select_alu(instruction_set.get("alu_sel"), self.select_a(instruction_set.get("mux_a_sel")), self.select_b(instruction_set.get("mux_b_sel")))
        if instruction_set.get("latch_s"):
            self.second = res
        if instruction_set.get("latch_pc"):
            self.program_counter = res
        if instruction_set.get("latch_sp"):
            self.stack_pointer = res
        if instruction_set.get("latch_rsp"):
            self.return_stack_pointer = res
        if instruction_set.get("latch_dr_alu"):
            self.data_register = res
        # if instruction_set.get("latch_dr_mem"):
            # self.data_register = res
        if instruction_set.get("latch_r"):
            self.return_register = res
        if instruction_set.get("latch_t"):
            self.top = res
        if instruction_set.get("latch_ar"):
            self.address_register = res
        if instruction_set.get("latch_ir"):
            self.instruction_register = res
        if instruction_set.get("latch_sr"):
            self.status_register = res

    