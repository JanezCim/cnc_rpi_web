from bottle import run, route, redirect, request
import time
import threading

running_on_rpi = True

if running_on_rpi:
	import RPi.GPIO as GPIO

loop_thread = None

pump_pin = 23
button_pins = [17,27,22,18]

#create status lists with sam length of button_pins list filled with zeroes
phy_btn_status = [0]*len(button_pins)
old_phy_btn_status = [0]*len(button_pins)


initial_value_duty = 42
initial_freq = 5

button_status = False
old_button_status = False
slider_status = initial_value_duty
old_slider_status = slider_status
duty_freq = initial_freq
old_duty_freq = duty_freq

pump_with_freq = False
old_pump_with_freq = pump_with_freq
pumping_time_on = slider_status*duty_freq*0.01
pumping_time_off = duty_freq-pumping_time_on
pump_on_off = False
old_pump_on_off = False

start_time = time.time()

if running_on_rpi:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pump_pin, GPIO.OUT)
	for btn in button_pins:
		GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)


@route("/")
def index():
    return '''
	<html>
	<title> Rpi CNC </title>
	<h1>RPi CNC </h1>
	<div style="display: inline-block;margin-top: 50px;vertical-align:top;">
		<h3> PUMPA </h3>
		<div id="pumpa" onmousedown="mDown(this)" onmouseup="mUp(this)" ontouchstart="mDown(this)" ontouchend="mUp(this)" unselectable="on" 	onselectstart="return false;" > OFF	</div>
	</div>
	<div class="slidecontainer" style="display: inline-block;">
		<h3> Duty cycle </h3>
  		<input type="range" min="1" max="100" value="'''+str(initial_value_duty)+'''" class="slider" id="slider1">
  		<div id="slider_val">'''+str(pumping_time_on)+'''</div>
		
	</div>	
	<div style="display: inline-block;margin-top: 50px;vertical-align:top;">
		<h3> Frequency </h3>
		<input type="number" name="quantity" min="1" max="5" value="'''+str(initial_freq)+'''" id="number1">
	</div>

	<script type="text/javascript">

		xmlHttp=new XMLHttpRequest();
		function mDown(obj) {
		    obj.style.backgroundColor = "#0F0";
		    obj.innerHTML = "ON";

			if(xmlHttp.readyState==0 || xmlHttp.readyState==4){
				xmlHttp.open('PUT','/pumpon',true);
				xmlHttp.onreadystatechange=handleServerResponse;
				xmlHttp.send(null);	
				console.log("req sent");			
			}

		}

		function mUp(obj) {
		    obj.style.backgroundColor="#F00";
		    obj.innerHTML="OFF";

		    if(xmlHttp.readyState==0 || xmlHttp.readyState==4){
				xmlHttp.open('PUT','/pumpoff',true);
				xmlHttp.onreadystatechange=handleServerResponse;
				xmlHttp.send(null);	
				console.log("req sent");			
			}
		}

		function handleServerResponse(){
			if(xmlHttp.readyState==4 && xmlHttp.status==200){
				console.log("resp received")
			}
		}


		var slider = document.getElementById("slider1");
		var output = document.getElementById("slider_val");
		var number = document.getElementById("number1")
		//output.innerHTML = slider.value; // Display the default slider value

		// Update the current slider value (each time you drag the slider handle)
		slider.oninput = function() {
			console.log(this.value);
		    output.innerHTML = Math.round(number.value*slider.value)*0.01;

		    if(xmlHttp.readyState==0 || xmlHttp.readyState==4){
				xmlHttp.open('PUT','/duty?duty='+this.value,true);
				xmlHttp.onreadystatechange=handleServerResponse;
				xmlHttp.send(null);	
				console.log("req sent");			
			}
		}

		number.oninput = function() {
			console.log(this.value);
			output.innerHTML = Math.round(number.value*slider.value)*0.01;
		   
		    if(xmlHttp.readyState==0 || xmlHttp.readyState==4){
				xmlHttp.open('PUT','/number?number='+this.value,true);
				xmlHttp.onreadystatechange=handleServerResponse;
				xmlHttp.send(null);	
				console.log("req sent");			
			}
		}


	</script>
	<style>
	html {
	font-family:arial
	}
	h3 {
		text-align:center;
	}
	#pumpa {
		width:100px;
		height:100px;
		font-family:arial;
		vertical-align:middle;
		cursor:wait;
		 color:#000;
		 background-color:#F00;
		 text-align:center;
		 
		 margin: 25px;
	}
	.slidecontainer {
	    width: 75%;
	    margin: 20px;
	    margin-top: 50px;
	}

	.slider {
	    -webkit-appearance: none;
	    width: 100%;
	    height: 25px;
	    background: #d3d3d3;
	    outline: none;
	    opacity: 0.7;
	    -webkit-transition: .2s;
	    transition: opacity .2s;
	}

	.slider:hover {
	    opacity: 1;
	}

	.slider::-webkit-slider-thumb {
	    -webkit-appearance: none;
	    appearance: none;
	    width: 25px;
	    height: 25px;
	    background: #4CAF50;
	    cursor: pointer;
	}

	.slider::-moz-range-thumb {
	    width: 25px;
	    height: 25px;
	    background: #4CAF50;
	    cursor: pointer;
	}

	#slider_val{
		margin:auto;
		padding-left:49%;
	}
	</style>

	</html>


    '''


@route("/pumpon", method="PUT")
def pumpon():
	global button_status
	button_status = True
	return redirect("/")

@route("/pumpoff", method="PUT")
def pumpoff():
	global button_status
	button_status = False
	return redirect("/")

@route("/duty", method="PUT")
def set_duty():
	global slider_status
	slider_status = request.query.duty
	#print slider_status

@route("/number", method="PUT")
def set_duty_freq():
	global duty_freq
	duty_freq = request.query.number
	

def main_loop():
	global old_button_status
	global old_duty_freq
	global old_slider_status
	global button_status
	global duty_freq
	global slider_status
	global pumping_time_on
	global pumping_time_off
	global start_time
	global old_pump_with_freq
	global pump_with_freq
	global pump_on_off
	global old_pump_on_off

	while True:
		#if running on raspberry pi, check statuses of physical buttons
		if(running_on_rpi):
			read_phy_buttons()

		#check status of web button
		if(button_status != old_button_status):
			pump_on_off = button_status

			#everytime button is pressed turn pumping off
			pump_with_freq = False

		#check separatelly status of physical button number 0
		if(phy_btn_status[0] != old_phy_btn_status[0]):
			pump_on_off = phy_btn_status[0]

			#everytime button is pressed turn pumping off
			pump_with_freq = False

		#if there is a change eather in slider status or duty frequency number, start periodic pumping and caluclate times of intervals	
		if((slider_status != old_slider_status) or (duty_freq != old_duty_freq)):
			#everytime there is a change on slider var, turn pumping on
			pump_with_freq = True
			try:
				#calculation of interval times
				pumping_time_on = float(slider_status)*float(duty_freq)*0.01
				pumping_time_off = float(duty_freq)-float(pumping_time_on)
			except:
				print "There was an error calculating on off pump times"
		
		#if this is the first cycle of pumping, start timer freshly 	
		if(old_pump_with_freq==False and pump_with_freq ==True):
			start_time = time.time()

		#if flag for periodic pumping is activated, we pump!	
		if(pump_with_freq):
			elapsed_time = time.time()-start_time
			if(pump_on_off):
				if(elapsed_time>pumping_time_on):
					pump_on_off = False
					start_time = time.time()
			else:
				if(elapsed_time>pumping_time_off):
					pump_on_off = True
					pump_on_off = True
					start_time = time.time()

		#actually activate or deactivate the pump according to pump_on_off flag			
		if(pump_on_off != old_pump_on_off):
			if(pump_on_off == True):
				print "ON"
				GPIO.output(pump_pin, 1)
			else:
				print "OFF"
				GPIO.output(pump_pin, 0)

		old_button_status = button_status
		old_duty_freq = duty_freq
		old_slider_status = slider_status
		old_pump_with_freq = pump_with_freq
		old_pump_on_off = pump_on_off
		remember_phy_button_states()
		time.sleep(0.05)

#read physical buttons
def read_phy_buttons():
	#go thru all the physical buttons and check if they are pressed
	global phy_btn_status
	global old_phy_btn_status
	for i in range (0,len(button_pins)):
		if GPIO.input(button_pins[i]) == GPIO.LOW:
			phy_btn_status[i]=True
		else:
			phy_btn_status[i]=False

def remember_phy_button_states():
	#go thru all button statuses and remember them for the next loop
	for i in range(0,len(button_pins)):
		old_phy_btn_status[i]=phy_btn_status[i]

if __name__=="__main__":
	global loop_thread
	loop_thread = threading.Thread(target=main_loop)
	loop_thread.daemon = True
	loop_thread.start()

	run(host='0.0.0.0', port=8080, debug=True)
	
	if(running_on_rpi):
		GPIO.cleanup()
