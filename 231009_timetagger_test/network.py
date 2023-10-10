import TimeTagger
# import pulsestreamer as pstreamer
import matplotlib.pyplot as plt
import numpy as np
# ip = '192.168.0.139'
# ps = pstreamer.PulseStreamer(ip)
# seq = ps.createSequence()
# Laser_sequence = [(0.2e-6 * 1e9, 1), (1.05e-6 * 1e9, 0)]
# seq.setDigital([5], Laser_sequence)
# tagger = TimeTagger.createTimeTagger() # this is the usb connection way
tagger = TimeTagger.createTimeTaggerNetwork('192.168.0.159:41101') # network
# ps.stream(seq)
print(tagger.isConnected())
tagger.setTriggerLevel(channel=1, voltage=0.08) # unit:mV
tagger.setTriggerLevel(channel=2, voltage=0.08) # unit:mV

tagger.setTestSignal(1, False) # channel 1, built-in test signal, ~0.8-0.9 MHz
tagger.setTestSignal(2, False) # channel 1, built-in test signal, ~0.8-0.9 MHz


cr_instance = TimeTagger.Countrate(tagger, [1,2]) # read channel 1 countrate, could be [0,1,2, ..]
cr_instance.startFor(capture_duration = int(1e-2*1E12)) # acquire 5s
cr_instance.waitUntilFinished()
cr = cr_instance.getData() # [xxx], countrate for channel 1 within the time period
print(cr)

bin_width=1e-9
num_bin=100
corr_instance = TimeTagger.Correlation(tagger, 1, 2, bin_width*1e12, num_bin) # measuring correlation btw channel 0,1
corr_instance.startFor(capture_duration = int(360*1E12)) # acquire 5s
corr_instance.waitUntilFinished()
# correlation = corr_instance.getData() # [xxx, xxx, ...] length = 1000
g2 = corr_instance.getDataNormalized() # [xxx, xxx, ...] length = 1000
t=np.linspace(-(num_bin/2)*bin_width,(num_bin/2)*bin_width,num_bin)*1e9
plt.scatter(t,g2,marker="+",alpha=0.5)
plt.axhline(y=1, color='r', linestyle='-')
plt.ylim(0,1.2)
plt.xlabel('Delay (ns)')
plt.ylabel(r'$g^{(2)}$')

TimeTagger.freeTimeTagger(tagger) # close timetagger reference
plt.savefig("g2_laser.png", dpi=300, bbox_inches='tight')
plt.show()