import TimeTagger
import pulsestreamer as pstreamer
import matplotlib.pyplot as plt
# ip = '192.168.0.139'
# ps = pstreamer.PulseStreamer(ip)
# seq = ps.createSequence()
# Laser_sequence = [(0.2e-6 * 1e9, 1), (1.05e-6 * 1e9, 0)] 
# seq.setDigital([5], Laser_sequence)
# ps.stream(seq)

# tagger = TimeTagger.createTimeTagger() # this is the usb connection way
tagger = TimeTagger.createTimeTaggerNetwork('192.168.0.159:41101') # network
print(tagger.isConnected())

tagger.setTestSignal(1, False) # channel 1, built-in test signal, ~0.8-0.9 MHz


cr_instance = TimeTagger.Countrate(tagger, [1]) # read channel 1 countrate, could be [0,1,2, ..]
cr_instance.startFor(capture_duration = int(1E12)) # acquire 5s
cr_instance.waitUntilFinished()
cr = cr_instance.getData() # [xxx], countrate for channel 1 within the time period
print(cr)


TimeTagger.freeTimeTagger(tagger) # close timetagger reference