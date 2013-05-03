
from struct import pack, unpack
from utils import get_bit, tobits, frombits, Lazy
from systemclock import SYSTEM_CLOCK_FREQUENCY
from adaptationfield import AdaptationField


class TransportPacket():
    SYNC_BYTE = 0x47
    NULL_PACKET_PID = 0x1FFF
    VALID_LENGTH = 188  # bytes

    def __init__(self, data, sync_byte_ts_location=0):
        self.data = data
        self.sync_byte_ts_location = sync_byte_ts_location

        if not data[0] == self.SYNC_BYTE:
            print "First byte of packet is not sync byte!"

    @Lazy
    def _first_bunch_of_settings_bits(self):
        return tobits(self.data[1:3])

    @Lazy
    def _second_bunch_of_settings_bits(self):
        return tobits([self.data[3]])

    @Lazy
    def _adaptation_settings_bits(self):
        if self.adaptation_field_length > 0:
            return tobits(self.data[5:5+self.adaptation_field_length])
        else:
            return []

    @Lazy
    def adaptation_field_length(self):
        if self.adaptation_field_control[0] == 1:
            return self.data[4]
        else:
            return 0

    @Lazy
    def adaptation_field(self):
        return AdaptationField(data_bits_list=self._adaptation_settings_bits)

    ######### First group of settings #########

    @Lazy
    def transport_error(self):
        return bool(self._first_bunch_of_settings_bits[0])

    @Lazy
    def payload_unit_start(self):
        return bool(self._first_bunch_of_settings_bits[1])

    @Lazy
    def transport_priority(self):
        return bool(self._first_bunch_of_settings_bits[2])

    @Lazy
    def pid(self):
        return unpack('>H', frombits(self._first_bunch_of_settings_bits[3:16]))[0]

    ######### Second group of settings #########

    @Lazy
    def transport_scrambling_control(self):
        return self._second_bunch_of_settings_bits[0:2]

    @Lazy
    def adaptation_field_control(self):
        return self._second_bunch_of_settings_bits[2:4]

    @Lazy
    def continuity_counter(self):
        return unpack('>H', frombits(self._second_bunch_of_settings_bits[4:8], pad_to_bytes=2))[0]

