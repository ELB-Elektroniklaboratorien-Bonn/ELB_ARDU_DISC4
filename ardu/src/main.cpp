/*
This firmware uses the following open-source libraries:

1. Vrekrer_SCPI_Parser
   - Author: Victor Pérez
   - License: MIT License
   - Repository: https://github.com/Vrekrer/Vrekrer_scpi_parser

2. TimerOne
   - Author: Paul Stoffregen
   - License: Creative Commons Attribution 3.0 United States (CC BY 3.0 US)
   - Repository: https://github.com/PaulStoffregen/TimerOne

3. ArduinoLog
   - Author: Jeroen S. C.
   - License: MIT License
   - Repository: https://github.com/jsc/ArduinoLog

All libraries are used according to their respective licenses.

Firmware to set thresholds of the ELB_ARDU_DISC4.

Hardware required:
ELB_ARDU_DISC4

Commands:
  *IDN?
    Gets the instrument's identification string
  
  SYSTem:SPI:SENd <index>, <command>, <payload>
    Send 24 bit of data via SPI.
    Use chip select <index>, 8 bit <command>, and 16 bit <payload>.
    Answer:
    SPIRESP,<index>,<command>,<payload>,<data_read_from_spi>

  SYSTem:PULser:ENAble
    Enble the integrated testpulser.

  SYSTem:PULser:DISable
    Disable the integrated testpulser.

*/

#include <ArduinoLog.h>
#include <SPI.h>
#include <TimerOne.h>
#include <inttypes.h>

#include "Arduino.h"
#include "Vrekrer_scpi_parser.h"

#define TEST_PULSER_PIN 9

#define CS_LOGIC_TIMING_I 2
#define CS_PULSE_I 3
#define CS_DELAY_I 4
#define CS_CHANNEL_HYS 5
#define CS_CHANNEL_THR 6
#define CS_LOGIC_TIMING_TH 7
#define CS_PULSE_TH 8
#define CS_DELAY_TH 10

#define CS_COUNT 8

#define ARDU_DISC_FW_VER "0.0.1"

// this array needs to have the same order in python:
const int CS_ARRAY[8] = {CS_LOGIC_TIMING_I, CS_PULSE_I,     CS_DELAY_I,
                         CS_CHANNEL_HYS,    CS_CHANNEL_THR, CS_LOGIC_TIMING_TH,
                         CS_PULSE_TH,       CS_DELAY_TH};

SCPI_Parser my_instrument;

const int intensity[11] = {0, 3, 5, 9, 15, 24, 38, 62, 99, 159, 255};

void Init_CS() {
    for (uint8_t i = 0; i < CS_COUNT; i++) {
        pinMode(CS_ARRAY[i], OUTPUT);
        digitalWrite(CS_ARRAY[i], HIGH);
    }
}

void Set_CS(uint8_t cs_index, uint8_t value) {
    if (cs_index >= CS_COUNT) {
        Log.error("Invalid CS Index: %d", cs_index);
        cs_index = 0;
    }
    uint8_t pin = CS_ARRAY[cs_index];
    digitalWrite(pin, value);
}

uint32_t SPI_IO(uint8_t cs_index, uint8_t command, uint16_t data) {

    SPISettings spiSettings(1000000, MSBFIRST, SPI_MODE0);
    SPI.beginTransaction(spiSettings);

    Set_CS(cs_index, LOW);
    uint8_t ret1 = SPI.transfer(command);
    uint16_t ret2 = SPI.transfer16(data);
    Set_CS(cs_index, HIGH);
    SPI.endTransaction();

    return ((uint32_t)ret1 << 16) | ret2;
}


void send_identify_message(Stream *interface) {
    interface->println(F("ELB,ARDUDISC,#00," ARDU_DISC_FW_VER));
    // *IDN? Suggested return string should be in the following format:
    // "<vendor>,<model>,<serial number>,<firmware>"
}

void Identify(SCPI_C commands, SCPI_P parameters, Stream &interface) {  // NOLINT
  send_identify_message(&interface);
}

void SendSpi(SCPI_C commands, SCPI_P parameters, Stream &interface) { // NOLINT
    Log.info(F("SPI IO"));

    // Parameters: Index, command, data

    const char *paramStr = parameters[0];
    uint8_t cs_index = strtol(paramStr, NULL, 0);
    Log.info("Chip Select Index: %d\n", cs_index);

    const char *paramStr1 = parameters[1];
    uint8_t command = strtol(paramStr1, NULL, 0);
    command = constrain(command, 0, 0xff);
    Log.info("Command: %d\n", command);

    const char *paramStr2 = parameters[2];
    uint16_t payload_data = strtol(paramStr2, NULL, 0);

    Log.info("Payload: %d\n", payload_data);

    uint32_t answer = SPI_IO(cs_index, command, payload_data);

    char response[32];
    snprintf(response, sizeof(response),
             "SPIRESP,%u,%u,%u,%lu\r\n",
             cs_index, command, payload_data, (unsigned long)answer);
    interface.print(response);
}

void DoTimer(SCPI_C commands, SCPI_P parameters, Stream &interface) { // NOLINT
    String last_header = String(commands.Last());

    last_header.toUpperCase();
    if (last_header.startsWith("ENA")) {
        Timer1.start();
        interface.print("Pulser,1\n");
    } else if (last_header.startsWith("DIS")) {
        Timer1.stop();
        interface.print("Pulser,0\n");
    } else {
        interface.print("Invalid Paramter\n");
    }
}

void setup() {
    my_instrument.RegisterCommand(F("*IDN?"), &Identify);

    my_instrument.SetCommandTreeBase(F("SYSTem:SPI"));
    my_instrument.RegisterCommand(F(":SENd"), &SendSpi);

    my_instrument.SetCommandTreeBase(F("SYSTem:PULser"));
    my_instrument.RegisterCommand(F(":DISable"), &DoTimer);
    my_instrument.RegisterCommand(F(":ENAble"), &DoTimer);

    Serial.begin(115200);
    Log.begin(LOG_LEVEL_ERROR, &Serial);

    Init_CS();

    SPI.begin();
    SPI.setClockDivider(SPI_CLOCK_DIV8);

    pinMode(TEST_PULSER_PIN, OUTPUT);
    Timer1.initialize(500);
    Timer1.pwm(TEST_PULSER_PIN, 512);
    Timer1.stop();

    send_identify_message(&Serial);
}

void loop() { my_instrument.ProcessInput(Serial, "\n"); }
