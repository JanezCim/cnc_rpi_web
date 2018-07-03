from bottle import run, route, redirect, request
#import RPi.GPIO as GPIO
import time

pump_pin = 23
initial_value_duty = 42
initial_freq = 5

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pump_pin, GPIO.OUT)


@route("/")
def index():
#	return '''
#        <button action="/pumpon" method="get" value="Pump On" type="submit" />
#
#        <form action="/pumpoff" method="get">
#            <input value="Pump Off" type="submit" onmousedown="/test" />
#        </form>
#    '''
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
  		<div id="slider_val">'''+str(initial_value_duty*initial_freq*0.01)+'''</div>
		
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
	print "turn pump on"
	return redirect("/")

@route("/pumpoff", method="PUT")
def pumpoff():
	print "turn pump off"
	return redirect("/")

@route("/duty", method="PUT")
def set_duty():
	print request.query.duty

@route("/number", method="PUT")
def set_duty():
	print request.query.number

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