class DataPath:
    def __ininit__(self):
        self.second=0
        self.programm_counter=0
        self.stack_pointer=0 #TODO ?
        self.return_stack_pointer=0 #TODO ?
        self.data_registr=0
        self.return_registr=0
        self.top=0
        self.adress_registr=0
        self.instruction_register=0
        self.const=0
        self.status_register=0

    def select_a(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.instruction_register #TODO sign_extend
        elif signal == 1:
            return self.second
        elif signal == 2:
            return self.programm_counter
        elif signal == 3:
            return self.stack_pointer
        elif signal == 4:
            return self.return_stack_pointer
        elif signal == 5:
            return self.data_registr

    def select_b(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.data_registr
        elif signal == 1:
            return self.return_registr
        elif signal == 2:
            return self.top
        elif signal == 3:
            return self.const
        elif signal == 4:
            return self.adress_registr

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
        
    def select_alu(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.select_a(signal) + self.select_b(signal)
        elif signal == 1:
            return self.select_a(signal) - self.select_b(signal)
        elif signal == 2:
            return self.select_a(signal) * self.select_b(signal)
        elif signal == 3:
            return self.select_a(signal) // self.select_b(signal)
        elif signal == 4:
            return self.select_a(signal) % self.select_b(signal)
        elif signal == 5:
            return self.select_a(signal) & self.select_b(signal)
        elif signal == 6:
            return self.select_a(signal) | self.select_b(signal)
        elif signal == 7:
            return self.select_a(signal) ^ self.select_b(signal)
        elif signal == 8:
            return self.select_a(signal)
        elif signal == 9:
            return self.select_b(signal)
        #TODO shifts

    