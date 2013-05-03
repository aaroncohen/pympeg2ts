from collections import deque

from transportstream import TransportStream

import cProfile

# test_file = "/Users/cohena/Downloads/football.ts"
# test_file = "/Users/cohena/Downloads/repaired.ts"
# test_file = "/Users/cohena/Downloads/crasher.ts"
test_file = "/Users/cohena/Downloads/1022_20080103210000_Fixed.ts"
# test_file = "/Users/cohena/Downloads/parkrun1280_12mbps.ts"  # before lazy: 103 secs
# test_file = "/Users/cohena/Downloads/1080p25.ts"



transport_stream = TransportStream(input_file=test_file)


# for i in xrange(3000):
#     packets.append(transport_stream.next())

packets = deque([], maxlen=16)

def consume_packets():
    for packet in transport_stream:
        # if packet.pcr_flag and packet.opcr_flag:
        # if len(packets):
        #     transport_rate = transport_stream.calc_transport_rate(current_packet=packet, previous_packet=packets[-1])
        #     if transport_rate is not None:
        #         print "PID: %s -- Transport Rate: %s" % (packet.pid, transport_rate)
        if packet.adaptation_field.transport_private_data_flag:
            print "Private data length: %s" % len(packet.transport_private_data)
        if packet.adaptation_field.splicing_point_flag:
            print "Splice countdown: %s" % packet.splice_countdown
        packets.append(packet)

if __name__ == "__main__":
    cProfile.run('consume_packets()')