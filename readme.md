## Hot Plate temperature controller code for a raspberry pi

This contains code to control a hot plate and display the temperature. The raspberry pi is connected to a thermocouple, a solid-state-relay, and an OLED display.

# pinouts
<span style="color:green">HOTBIT</span> = 18 -- the pin with the switch
<span style="color:green">FANBIT</span> = 22 -- the pin with the switch

# graphicslib

graphicslib contains the graphics routines

# pigpio

pighelp is a simple helper for the PI-GPIO gpio code for the raspberry pi.

<i>see</i>: https://github.com/joan2937/pigpio for the source

# Power requirement

At 100 percent duty cycle it uses 1000W

# Measurements

| Percentage | Stable Temperature |
|---| ------------- | ----- |
|20|293|
|25|340|
|30|375|
|35|425|

# Reflow Profile
---
see: http://micro.apitech.com/pdf/Surface_Mount_Reflow_Soldering.pdf

* <b>Initial Pre-Heat Stage</b>. PWBs should be preheated prior to solder reflow. During the pre-heat stage, the solder paste begins to dry as volatile ingredients are allowed to evaporate. The initial pre-heat stage takes place during the first 90 seconds of the reflow profile as the temperature is slowly increased from room ambient conditions to approximately +155°C. 
 
* <b>Flux Activation and Pre-Heat Soak Stage</b>. Following the initial pre-heat stage, the temperature is gradually increased to +183°C over a period of approximately 90 seconds so the flux in the solder paste can clean the bonding surfaces properly. During the pre-heat soak (also know as the flux activation stage), the solder paste and soldering surfaces should be roughly the same temperature. 

* <b>Ramp Up</b>.   The PWB now enters the solder reflow stage. Over a period of 30 seconds, the temperature should be increased to the appropriate peak reflow temperature shown below. Depending on package dimensions, exposure time at peak temperature should be minimized (re. J-STD-020A). 
 
* <b>Peak Reflow Temperatures</b>: • +220°C to +225°C for IR and FC Reflow Systems. • +215°C to +220°C for most VPR Systems. 
 
* <b>Ramp Down</b>.   The reflow stage is completed as the temperature is reduced to +183°C (the original melting point of the solder paste) over a period of approximately 30 seconds. Caution - Over baking the solder paste and/or exceeding the glass transition temperature of the FR-4 printed wiring board material should be avoided.  
 
 * The profile is completed as the temperature is gradually reduced from +183°C to < +40°C over a period of approximately 3 minutes. The gradual cooling of the printed wiring board after reflow is important. It is during this period that the molten solder solidifies to form a strong joint fillet.      

## <span style="color:green">Summary</span>
---
* <b><span style="color:green">Pre heat</span></b>: <2.5C per second. Get to Flux activation temp of 160C.
* <b><span style="color:green">Soak</span></b>: 60-90 seconds (120 seconds max). Rate of 0.5-0.6C/sec up to Liquid temp (183C).  
* <b><span style="color:green">Reflow</span></b>: Go from 183C to 210-220 at 1.3-1.6C/sec then return to liquid (183). 30-50 seconds recommended. 70 seconds max.
* <b><span style="color:green">Cooling</span></b>: 180 secs minimum.

# Fan Testing
I've got a high powered 12V fan and an aluminum foil shroud. This is all Fahrenheit and values per second.

|Fan| Heating Rate | Cooling Rate |
|-|-|-|
|None|1.2|-.35|
|6V|1|-1.2|
|12V|1.1|-1.6|

So, the heating rate isn't quite linear. It starts at maybe 1.4 (when cold) and decreases to 1.0 when hot.

With the 500W heating cartridges

|type|0-200F|200-300F|300-400F|
|-|-|-|-|
|250W|1.2|1.3|1|
|500W|2.4|2.6|1.6|





