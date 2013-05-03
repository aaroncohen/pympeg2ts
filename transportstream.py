
import os.path
from threading import Event
from transportpacket import TransportPacket
from systemclock import SYSTEM_CLOCK_FREQUENCY


class TransportStream():
    NO_DATA_TIMEOUT = 10  # secs

    def __init__(self, input_file=None):
        self.byte_buffer = bytearray()
        self.byte_buffer_pos = 0
        self.got_new_data = Event()
        self.input_file = input_file
        self.input_file_handle = None
        self.end_of_file = False
        self.last_continuity_values = {}
        self.proper_continuances = 0 # remove me
        self.last_pid = None
        self.packet_number = 0

        if self.input_file is not None:
            if os.path.exists(self.input_file):
                self.input_file_handle = open(self.input_file, mode='r')

    def read_input_file_chunk(self, chunk_size=TransportPacket.VALID_LENGTH * 1024):
        print "%.2f MB consumed" % (int(self.input_file_handle.tell()) / 1024 / 1024.)
        return self.input_file_handle.read(chunk_size)

    def calc_byte_arrival_time(self, byte_index, current_packet, previous_packet):
        pass

    def calc_transport_rate(self, current_packet, previous_packet):
        if current_packet.program_clock_reference is not None and previous_packet.program_clock_reference is not None:
            sync_byte_diff = (current_packet.sync_byte_ts_location - previous_packet.sync_byte_ts_location)

            return (sync_byte_diff * SYSTEM_CLOCK_FREQUENCY) / \
                (current_packet.program_clock_reference - previous_packet.program_clock_reference)
        else:
            return None

    def verify_continuity(self, packet):
        if packet.pid == TransportPacket.NULL_PACKET_PID:
            return

        curr_value = packet.continuity_counter
        if not packet.adaptation_field_control == [0, 0] and not packet.adaptation_field_control == [1, 0]:
            if packet.pid in self.last_continuity_values:
                last_value = self.last_continuity_values[packet.pid]
                if last_value == 15:
                    if not curr_value == 0 and not (curr_value == last_value and packet.adaptation_field_control[-1] == 1):
                        self.proper_continuances -= 1
                        print "Packet number: %s" % self.packet_number
                        print "Continuity interruption -- pid: %s, counter: %s, prevcounter: %s (should rollover)" % \
                              (packet.pid, curr_value, last_value)
                else:
                    if not curr_value == last_value + 1 and not (curr_value == last_value and packet.adaptation_field_control[-1] == 1):
                        self.proper_continuances -= 1
                        print "Packet number: %s" % self.packet_number
                        print "Continuity interruption -- pid: %s, counter: %s, prevcounter: %s" % \
                              (packet.pid, curr_value, last_value)
            self.last_continuity_values[packet.pid] = curr_value
        self.proper_continuances += 1

    def data_in(self, data_chunk):
        self.byte_buffer = self.byte_buffer[self.byte_buffer_pos:]
        self.byte_buffer_pos = 0
        self.byte_buffer.extend(list(data_chunk))
        self.got_new_data.set()

    def __iter__(self):
        return self

    def next(self, ):
        incomplete_packet = True

        while incomplete_packet and not self.end_of_file:
            if self.byte_buffer_pos >= (len(self.byte_buffer) - TransportPacket.VALID_LENGTH):
                if self.input_file_handle:
                    new_data = self.read_input_file_chunk()
                    if len(new_data):
                        self.data_in(new_data)
                    else:
                        self.end_of_file = True
                else:  # not reading from a file
                    self.got_new_data.wait(timeout=self.NO_DATA_TIMEOUT)
                    if self.got_new_data:
                        self.got_new_data.clear()
                    else:
                        raise NoDataTimeoutException(
                            "Didn't receive any new transport stream data for %s seconds." % self.NO_DATA_TIMEOUT)

            for i, byte in enumerate(self.byte_buffer[self.byte_buffer_pos:]):
                if byte == TransportPacket.SYNC_BYTE:
                    # found first sync byte, might be packet start
                    # look ahead a packetlength, if that much data is available
                    if len(self.byte_buffer) - self.byte_buffer_pos >= TransportPacket.VALID_LENGTH:
                        start_of_packet = self.byte_buffer_pos + i
                        end_of_packet = start_of_packet + TransportPacket.VALID_LENGTH
                        if self.end_of_file or self.byte_buffer[end_of_packet] == TransportPacket.SYNC_BYTE:
                            # if sync byte present, we've got a packet
                            packet_data = self.byte_buffer[start_of_packet:end_of_packet]
                            self.byte_buffer_pos = end_of_packet
                            transport_packet = TransportPacket(data=packet_data)
                            self.verify_continuity(transport_packet)
                            self.packet_number += 1
                            return transport_packet
                        else:
                            # we probably didn't have an actual packet sync byte, iterate until the next one
                            continue
                    else:
                        # not enough data is available to assemble packet, wait until it is
                        break
        else:  # end of file
            print "Proper continuances: %s" % self.proper_continuances
            raise StopIteration


class NoDataTimeoutException(Exception):
    pass


class IncompletePacketException(Exception):
    pass
