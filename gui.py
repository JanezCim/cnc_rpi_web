from bottle import run, route, redirect
import RPi.GPIO as GPIO
import time

pump_pin = 23


GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT)


@route("/")
def index():
	return '''
        <button action="/pumpon" method="get" value="Pump On" type="submit" />

        <form action="/pumpoff" method="get">
            <input value="Pump Off" type="submit" onmousedown="/test" />
        </form>
    '''

@route("/pumpon", method="GET")
def pumpon():
	print "turn pump on"
	return redirect("/")

@route("/pumpoff", method="GET")
def pumpoff():
	print "turn pump off"
	return redirect("/")



@route("/test", method="GET")
def test():
	print "test"
	return redirect("/")

if __name__=="__main__":
	run(host='0.0.0.0', port=8080, debug=True)

	# try:
	# 	i = 0
	# 	while i<5:
	# 		GPIO.output(pump_pin, True)
	# 		time.sleep(1)
	# 		print "Pump on"
	# 		GPIO.output(pump_pin, False)
	# 		time.sleep(1)
	# 		print "Pump off"
	# 		i = i+1
	# except KeyboardInterrupt:
	# 	print "Keyboard Interrupt. Exiting cleanly..."
	# except:
	# 	print "Unknown error, Exiting cleanly..."
	# finally:
	# 	GPIO.cleanup()