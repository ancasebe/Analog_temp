import spidev
import time
import matplotlib.pyplot as plt
from collections import deque

# MCP3008 channel where the temperature sensor is connected
TEMP_SENSOR_CHANNEL = 0

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, chip select 0
spi.max_speed_hz = 1350000  # Set the SPI speed

# Set up the deque for a rolling temperature history (last 60 readings)
time_data = deque(maxlen=60)
temperature_data = deque(maxlen=60)

# Setup Matplotlib figure and axis
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 60)
ax.set_ylim(0, 100)  # Adjust based on expected temperature range

def read_adc(channel):
    """
    Read data from MCP3008 via SPI.
    Channel should be an integer between 0 and 7.
    """
    if channel < 0 or channel > 7:
        return -1
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def convert_to_temperature(adc_value):
    """
    Convert the ADC value to temperature.
    This formula assumes the use of an LM35 sensor which gives 10 mV/°C.
    """
    # Assuming a reference voltage of 3.3V
    voltage = (adc_value * 3.3) / 1023
    temperature_celsius = voltage * 100  # LM35 outputs 10 mV per °C
    return temperature_celsius

def update_plot():
    """
    Update the Matplotlib plot with new data.
    """
    line.set_xdata(range(len(temperature_data)))
    line.set_ydata(temperature_data)
    ax.set_xlim(0, len(temperature_data))
    ax.set_ylim(min(temperature_data, default=0) - 5, max(temperature_data, default=50) + 5)
    fig.canvas.draw()
    fig.canvas.flush_events()

try:
    while True:
        # Read temperature and add to the data deque
        adc_value = read_adc(TEMP_SENSOR_CHANNEL)
        temperature = convert_to_temperature(adc_value)
        
        # Add the current reading to the deques
        time_data.append(time.time())
        temperature_data.append(temperature)
        
        # Print the temperature in the console for reference
        print(f"Temperature: {temperature:.2f}°C")
        
        # Update the plot
        update_plot()
        
        # Wait 1 second before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    spi.close()  # Close the SPI connection
