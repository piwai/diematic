class Boiler:
    def __init__(self, index, logger):
        self.registers = []
        self.attribute_list = []
        self.index = index
        self.logger = logger
        for register in self.index:
            if register['type'] == 'bits':
                for varname in register['bits']:
                    setattr(self, varname, None)
                    self.attribute_list.append(varname)
            else:
                setattr(self, register['name'], None)
                self.attribute_list.append(register['name'])

    def _decode_decimal(self, value_int, decimals=0):
        if (value_int == 65535):
            return None
        else:
            output = value_int & 0x7FFF
        if (value_int >> 15 == 1):
            output = -output
        return float(output)/10**decimals


    def _decode_modeflag(self, value_int):
        """ Decodes and normalizes the working mode of the boiler.
            0 -> Anti-freeze
            2 -> Night
            4 -> Day
        """ 
        if value_int not in (0, 2, 4):
            return None
        if value_int == 4:
            return 1
        if value_int == 2:
            return 0
        if value_int == 0:
            return -1

    def browse_registers(self):
        for register in self.index:
            if not isinstance(register['id'], int):
                continue
            register_value = self.registers[register['id']]
            if register_value is None:
                self.logger.debug('Browsing register id {:d} value: None'.format(register['id']))
                continue
            self.logger.debug('Browsing register id {:d} value: {:#04x}'.format(register['id'], register_value))
            if register['type'] == 'bits':
                for i in range(len(register['bits'])):
                    bit_varname = register['bits'][i]
                    bit_value = register_value >> i & 1
                    setattr(self, bit_varname, bit_value)
            else:
                varname = register.get('name')
                if varname and varname.strip(): #test name exists
                    if register['type'] == 'DiematicOneDecimal':
                        setattr(self, varname, self._decode_decimal(register_value, 1))
                    elif register['type'] == 'DiematicModeFlag':
                        setattr(self, varname, self._decode_modeflag(register_value))
                    else:
                        setattr(self, varname, register_value)
                else:
                    continue

    def dump_registers(self):
        output = ''
        for id in range(len(self.registers)):
            if self.registers[id] is None:
                output += "{:d}: None\n".format(id)
            else:
                output += "{:d}: {:#04x}\n".format(id, self.registers[id])
        return output

    def fetch_data(self):
        output = { }
        for varname in self.attribute_list:
            output[varname] = getattr(self, varname)
        return output

    def dump(self):
        output = ''
        for varname,value in self.fetch_data().items():
            output += varname + ' = ' + str(value) + "\n"
        return output
