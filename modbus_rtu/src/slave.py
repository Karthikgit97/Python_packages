import serial

class ModbusNode:
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

    def convert_to_8_bit_array(self, data_list):
        data_byte_array = []
        for data in data_list:
            msb = (data >> 8) & 0xFF  # Shift and extract the most significant byte
            lsb = data & 0xFF  # Extract the least significant byte
            data_byte_array.append(msb)
            data_byte_array.append(lsb)

        print("data_byte_array", data_byte_array)

        return data_byte_array

    def write_registers(self, slave_id, function_code, data_values):
        data_byte_array = self.convert_to_8_bit_array(data_values)

        request_data = [slave_id, function_code, len(data_byte_array)]
        request_data.extend(data_byte_array)

        crc_bytes = self.calculate_crc(request_data)
        request_data.extend(crc_bytes)

        print("write_registers", request_data)

        request_byte_array = bytearray(request_data)
        self.serial_connection.write(request_byte_array)

    def read_request(self, num_bytes=8):
        response = self.serial_connection.read(num_bytes)
        return list(response[:-2])  # Remove CRC bytes and convert to list
