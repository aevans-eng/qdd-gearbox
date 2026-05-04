# QDD Thermistor Logger

Arduino sketch for logging gearbox or motor temperature from a thermistor voltage-divider circuit.

## Default Wiring

Default sketch constants assume:

```text
5V --- 10k fixed resistor --- A0 --- 10k NTC thermistor --- GND
```

If your circuit is reversed:

```text
5V --- 10k NTC thermistor --- A0 --- 10k fixed resistor --- GND
```

change this line in the sketch:

```cpp
const DividerMode DIVIDER_MODE = THERMISTOR_TO_GND;
```

to:

```cpp
const DividerMode DIVIDER_MODE = THERMISTOR_TO_VCC;
```

## Calibration Values

Tune these first:

```cpp
const float VREF_VOLTS = 4.35f;
const float FIXED_RESISTOR_OHMS = 10000.0f;
const float NOMINAL_RESISTANCE_OHMS = 10000.0f;
const float NOMINAL_TEMPERATURE_C = 25.0f;
const float BETA_K = 3435.0f;
```

Notes:

- `VREF_VOLTS` is set to `4.35 V`, measured on the Arduino 5V rail on 2026-05-03.
- Use the real fixed-resistor value if you can measure it.
- This setup is configured for a 10k NTC thermistor with Beta 3435.

## Upload

Open this file in Arduino IDE:

```text
testing/temperature-logger/arduino/qdd_thermistor_logger/qdd_thermistor_logger.ino
```

Use:

- Board: your Arduino model, likely Uno or Nano
- Baud: `115200`
- Serial Monitor output: CSV
- Serial Plotter: set `SERIAL_PLOTTER_MODE = true` in the sketch first

## Output Columns

```text
time_ms,adc_counts,voltage_v,resistance_ohm,temp_c,temp_f
```

## Python Logger

Install the serial dependency once:

```powershell
C:\Users\aaron\miniconda3\python.exe -m pip install -r C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\temperature-logger\requirements.txt
```

Start a log:

```powershell
C:\Users\aaron\miniconda3\python.exe C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\temperature-logger\log_thermistor.py --port COM6
```

Stop with `Ctrl+C`.

The logger writes timestamped CSV files to:

```text
testing/data/
```

Suggested filename:

```text
thermistor-log-YYYYMMDD-HHMMSS.csv
```

It adds a PC timestamp column ahead of the Arduino columns:

```text
pc_timestamp,time_ms,adc_counts,voltage_v,resistance_ohm,temp_c,temp_f
```

## Test-Day Workflow

1. Plug in the Arduino.
2. Confirm the port if needed:

```powershell
C:\Users\aaron\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe board list
```

3. Start the Python logger:

```powershell
C:\Users\aaron\miniconda3\python.exe C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\temperature-logger\log_thermistor.py --port COM6
```

4. Start the gearbox/motor test.
5. Stop logging with `Ctrl+C`.
6. Add the CSV filename and test notes to `testing/validation/test-log.md`.

## Motor Test Integration

Use this wrapper when you want one motor command and a synchronized temperature CSV:

```powershell
PowerShell -ExecutionPolicy Bypass -File C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\temperature-logger\run_motor_temp_test.ps1 -Command velocity -Profile gearbox -Ratio 5 -Rpm 10 -Seconds 5
```

What it does:

1. Starts `log_thermistor.py` on `COM6`.
2. Logs a short baseline before motion.
3. Runs the selected MKS motor command through `testing/mks-xdrive-mini/10-agent-control.ps1`.
4. Keeps logging briefly after motion.
5. Prints the temperature CSV path.

Supported commands:

```powershell
-Command velocity  -Rpm 10 -Seconds 5
-Command torque    -Nm 0.5 -Seconds 5
-Command position  -Deg 45
-Command status
-Command calibrate
-Command idle
```

For bare-motor tests:

```powershell
PowerShell -ExecutionPolicy Bypass -File C:\Users\aaron\Documents\c-projects\qdd-gearbox\testing\\temperature-logger\run_motor_temp_test.ps1 -Command velocity -Profile bare -Ratio 1 -Rpm 5 -Seconds 3
```

Use `-Calibrate` only when you intentionally want the wrapper to calibrate before the motion command.

Current bench setup verified on 2026-05-03:

- Arduino Uno detected on `COM6`
- Baud rate `115200`
- Thermistor: `10k NTC`, `Beta 3435`
- Divider mode in sketch: `THERMISTOR_TO_GND`
- Room-temperature sanity check: about `23.8 C`

For a cleaner live graph in Arduino Serial Plotter, change:

```cpp
const bool SERIAL_PLOTTER_MODE = false;
```

to:

```cpp
const bool SERIAL_PLOTTER_MODE = true;
```

That prints only `temp_c` and `voltage_v`, without the large `time_ms` value stretching the plot scale.

## Optional LCD

The sketch has disabled support for a common I2C 16x2 LCD.

To enable it:

1. Install `LiquidCrystal_I2C` in Arduino IDE.
2. Set:

```cpp
#define USE_I2C_LCD 1
```

3. Confirm the I2C address is correct:

```cpp
LiquidCrystal_I2C lcd(0x27, 16, 2);
```

Some LCD backpacks use `0x3F` instead of `0x27`.
