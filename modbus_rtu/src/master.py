import serial

class ModbusHost:
    def __init__(self, port, baudrate, timeout=0.1):
        self.serial_connection = serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=timeout)

    def calculate_crc(self, buffer):
        length = len(buffer)
        crc = 0xFFFF
        cr2 = 0

        for pos in range(length):
            crc ^= buffer[pos]  # XOR byte into least significant byte of crc

            for i in range(8, 0, -1):  # Loop over each bit
                if (crc & 0x0001) != 0:  # If the LSB is set
                    crc >>= 1  # Shift right and XOR 0xA001
                    crc ^= 0xA001
                else:  # Else LSB is not set
                    crc >>= 1  # Just shift right

        cr2 = crc >> 8
        crc = (crc << 8) | cr2
        crc &= 0xFFFF

        cr1 = crc & 0xFF  # Extract the least significant byte
        cr2 = (crc >> 8) & 0xFF  # Shift and extract the most significant byte

        crc_bytes = [cr2, cr1]
        return crc_bytes
    
    def convert_to_16_bit_array(self, bit_8_array):
        data_buf_list = []
        i = 3
        while i < (len(bit_8_array) - 2): # = length - 2(crc)
            msb = bit_8_array[i]  # Replace with your first 8-bit hex value
            lsb = bit_8_array[i+1] # Replace with your second 8-bit hex value
            hex_c = (msb << 8) | lsb
            data_buf_list.append(hex_c)
            i += 2

        return data_buf_list

    def read_registers(self, slave_id, function_code, start_address, num_registers):
        request_data = [slave_id, function_code, 0, start_address, 0, num_registers]
        crc_bytes = self.calculate_crc(request_data)

        request_data.extend(crc_bytes)
        print("read_registers", request_data)
        request_byte_array = bytearray(request_data)

        self.serial_connection.write(request_byte_array)

        for _ in range(10):  # Wait for 1000 milliseconds
            response = self.serial_connection.read(100)
            if response:
                response = self.convert_to_16_bit_array(list(response))
                return (response)  # Extract and return data values

        return [0, 0]
