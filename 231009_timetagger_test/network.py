import TimeTagger

# tagger = TimeTagger.createTimeTagger() # this is the usb connection way
tagger = TimeTagger.createTimeTaggerNetwork('192.168.0.135:41101') # network

tagger.setTestSignal(1, True) # channel 1, built-in test signal, ~0.8-0.9 MHz

cr_instance = TimeTagger.Countrate(tagger, [1]) # read channel 0 countrate, could be [0,1,2, ..]
cr_instance.startFor(capture_duration = int(10E12)) # acquire 20s
cr_instance.waitUntilFinished()
cr = cr_instance.getData() # [xxx], countrate for channel 0 within the time period
print(cr)


TimeTagger.freeTimeTagger(tagger) # close timetagger reference