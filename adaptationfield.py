from struct import pack, unpack
from utils import get_bit, tobits, frombits, Lazy
from systemclock import SYSTEM_CLOCK_FREQUENCY


class AdaptationField:
    def __init__(self, data_bits_list):
        self.data_bits_list = data_bits_list

    ######### Adaptation Field Values #########

    @Lazy
    def discontinuity_indicator(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[0])
        else:
            return None

    @Lazy
    def random_access_indicator(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[1])
        else:
            return None

    @Lazy
    def elementary_stream_priority_indicator(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[2])
        else:
            return None

    @Lazy
    def pcr_flag(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[3])
        else:
            return None

    @Lazy
    def opcr_flag(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[4])
        else:
            return None

    @Lazy
    def splicing_point_flag(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[5])
        else:
            return None

    @Lazy
    def transport_private_data_flag(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[6])
        else:
            return None

    @Lazy
    def adaptation_field_extension_flag(self):
        if len(self.data_bits_list):
            return bool(self.data_bits_list[7])
        else:
            return None

    @Lazy
    def program_clock_reference_base(self):
        """
        Based on a 90kHz clock
        """
        if self.pcr_flag:
            return unpack('>Q', frombits(self.data_bits_list[8:41], pad_to_bytes=4))[0]
        else:
            return None

    @Lazy
    def program_clock_reference_extension(self):
        """
        Based on a 27MHz clock
        """
        if self.pcr_flag:
            return unpack('>H', frombits(self.data_bits_list[47:56]))[0]
        else:
            return None

    @Lazy
    def program_clock_reference(self):
        if self.pcr_flag:
            return self.program_clock_reference_base * 300 + self.program_clock_reference_extension
        else:
            return None

    @Lazy
    def original_program_clock_reference_base(self):
        """
        Based on a 90kHz clock
        """
        if self.opcr_flag:
            offset = 0
            if self.pcr_flag:
                offset += 48

            return unpack('>Q', frombits(self.data_bits_list[8+offset:41+offset], pad_to_bytes=4))[0]
        else:
            return None

    @Lazy
    def original_program_clock_reference_extension(self):
        """
        Based on a 27MHz clock
        """
        if self.opcr_flag:
            offset = 0
            if self.pcr_flag:
                offset += 48

            return unpack('>H', frombits(self.data_bits_list[47+offset:56+offset]))[0]
        else:
            return None

    @Lazy
    def original_program_clock_reference(self):
        if self.opcr_flag:
            return self.original_program_clock_reference_base * 300 + self.original_program_clock_reference_extension
        else:
            return None

    @Lazy
    def splice_countdown(self):
        if self.splicing_point_flag:
            offset = 0
            if self.pcr_flag:
                offset += 48
            if self.opcr_flag:
                offset += 48

            return unpack('>b', frombits(self.data_bits_list[8+offset:16+offset]))
        else:
            return None

    @Lazy
    def transport_private_data(self):
        if self.transport_private_data_flag:
            offset = 0
            if self.pcr_flag:
                offset += 48
            if self.opcr_flag:
                offset += 48
            if self.splicing_point_flag:
                offset += 8
            private_data_length = unpack('>B', frombits(self.data_bits_list[8+offset:16+offset]))[0]
            return frombits(self.data_bits_list[16+offset:16+offset+private_data_length*8])

    # TODO: Adapatation field extension
