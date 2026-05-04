/*
  QDD gearbox thermistor logger

  Serial output is CSV so the Arduino IDE Serial Monitor, Serial Plotter,
  PuTTY, or a Python logger can capture it directly.

  Default assumptions:
  - Arduino Uno/Nano style 10-bit ADC
  - Thermistor divider measured on A0
  - 10k NTC thermistor, Beta = 3435 K
  - 10k fixed resistor
  - Divider orientation: Vcc -> fixed resistor -> A0 -> thermistor -> GND
*/

#include <Arduino.h>

// Set to 1 if you add an I2C 16x2 LCD and have LiquidCrystal_I2C installed.
#define USE_I2C_LCD 0

#if USE_I2C_LCD
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);
#endif

enum DividerMode {
  THERMISTOR_TO_GND,
  THERMISTOR_TO_VCC
};

const uint8_t THERMISTOR_PIN = A0;
const DividerMode DIVIDER_MODE = THERMISTOR_TO_GND;
const bool SERIAL_PLOTTER_MODE = false; // false = CSV log, true = live plot

const float ADC_MAX_COUNTS = 1023.0f;
const float VREF_VOLTS = 4.35f;         // Measured Arduino 5V rail, 2026-05-03.
const float FIXED_RESISTOR_OHMS = 10000.0f;

const float NOMINAL_RESISTANCE_OHMS = 10000.0f;
const float NOMINAL_TEMPERATURE_C = 25.0f;
const float BETA_K = 3435.0f;

const unsigned long SAMPLE_INTERVAL_MS = 1000;
const uint8_t ADC_SAMPLES = 16;

unsigned long lastSampleMs = 0;
bool headerPrinted = false;

float readAdcAverage() {
  unsigned long sum = 0;

  for (uint8_t i = 0; i < ADC_SAMPLES; i++) {
    sum += analogRead(THERMISTOR_PIN);
    delay(2);
  }

  return (float)sum / (float)ADC_SAMPLES;
}

float adcToVoltage(float adcCounts) {
  return (adcCounts / ADC_MAX_COUNTS) * VREF_VOLTS;
}

float voltageToThermistorResistance(float voltage) {
  const float epsilon = 0.0001f;

  if (voltage <= epsilon || voltage >= (VREF_VOLTS - epsilon)) {
    return NAN;
  }

  if (DIVIDER_MODE == THERMISTOR_TO_GND) {
    return FIXED_RESISTOR_OHMS * voltage / (VREF_VOLTS - voltage);
  }

  return FIXED_RESISTOR_OHMS * (VREF_VOLTS - voltage) / voltage;
}

float resistanceToTemperatureC(float resistanceOhms) {
  if (isnan(resistanceOhms) || resistanceOhms <= 0.0f) {
    return NAN;
  }

  const float nominalTempK = NOMINAL_TEMPERATURE_C + 273.15f;
  const float invTempK = (1.0f / nominalTempK) +
                         (1.0f / BETA_K) *
                         log(resistanceOhms / NOMINAL_RESISTANCE_OHMS);

  return (1.0f / invTempK) - 273.15f;
}

void printCsvHeader() {
  Serial.println(F("time_ms,adc_counts,voltage_v,resistance_ohm,temp_c,temp_f"));
  headerPrinted = true;
}

void printCsvRow(unsigned long nowMs,
                 float adcCounts,
                 float voltage,
                 float resistance,
                 float tempC) {
  Serial.print(nowMs);
  Serial.print(',');
  Serial.print(adcCounts, 1);
  Serial.print(',');
  Serial.print(voltage, 4);
  Serial.print(',');

  if (isnan(resistance)) {
    Serial.print(F("nan"));
  } else {
    Serial.print(resistance, 1);
  }

  Serial.print(',');

  if (isnan(tempC)) {
    Serial.print(F("nan,nan"));
  } else {
    Serial.print(tempC, 2);
    Serial.print(',');
    Serial.print((tempC * 9.0f / 5.0f) + 32.0f, 2);
  }

  Serial.println();
}

void printPlotterRow(float voltage, float tempC) {
  Serial.print(F("temp_c:"));
  if (isnan(tempC)) {
    Serial.print(F("nan"));
  } else {
    Serial.print(tempC, 2);
  }

  Serial.print(F(" voltage_v:"));
  Serial.println(voltage, 4);
}

void updateDisplay(float tempC, float voltage) {
#if USE_I2C_LCD
  lcd.setCursor(0, 0);
  lcd.print(F("Temp: "));
  if (isnan(tempC)) {
    lcd.print(F("sensor? "));
  } else {
    lcd.print(tempC, 1);
    lcd.print((char)223);
    lcd.print(F("C   "));
  }

  lcd.setCursor(0, 1);
  lcd.print(F("Vadc: "));
  lcd.print(voltage, 3);
  lcd.print(F(" V   "));
#else
  (void)tempC;
  (void)voltage;
#endif
}

void setup() {
  Serial.begin(115200);

#if USE_I2C_LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print(F("QDD temp logger"));
#endif

  analogReference(DEFAULT);
}

void loop() {
  const unsigned long nowMs = millis();

  if (!headerPrinted) {
    if (!SERIAL_PLOTTER_MODE) {
      printCsvHeader();
    }
    headerPrinted = true;
  }

  if ((nowMs - lastSampleMs) < SAMPLE_INTERVAL_MS) {
    return;
  }

  lastSampleMs = nowMs;

  const float adcCounts = readAdcAverage();
  const float voltage = adcToVoltage(adcCounts);
  const float resistance = voltageToThermistorResistance(voltage);
  const float tempC = resistanceToTemperatureC(resistance);

  if (SERIAL_PLOTTER_MODE) {
    printPlotterRow(voltage, tempC);
  } else {
    printCsvRow(nowMs, adcCounts, voltage, resistance, tempC);
  }

  updateDisplay(tempC, voltage);
}
