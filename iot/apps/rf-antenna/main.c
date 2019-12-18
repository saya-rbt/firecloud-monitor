/****************************************************************************
 * rf-sub1ghz/receptor/main.c
 *
 * Gateway microcontroller between the sensors one and the Raspberry Pi
 *
 * Copyright 2019 sayabiws@gmail.com
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 *
 *************************************************************************** */

// Fair credit where it's due: most of the code come from the examples from
// Nathaël Pajani, I merely adapted them to fit the assignment that was given
// to me.
// I'm still proud of what I did, though :)

#include "core/system.h"
#include "core/systick.h"
#include "core/pio.h"
#include "lib/stdio.h"
#include "drivers/serial.h"
#include "drivers/gpio.h"
#include "drivers/ssp.h"
#include "drivers/i2c.h"

#include "drivers/adc.h"
#include "extdrv/cc1101.h"
#include "extdrv/status_led.h"
#include "extdrv/bme280_humidity_sensor.h"
#include "extdrv/ssd130x_oled_driver.h"
#include "extdrv/ssd130x_oled_buffer.h"
#include "extdrv/veml6070_uv_sensor.h"
#include "extdrv/tsl256x_light_sensor.h"
#include "lib/font.h"


#define MODULE_VERSION  0x01
#define MODULE_NAME "Firecloud Monitor - RF antenna"
// The address is arbitrary and set at compile time through Make macros
// #define MODULE_ADDRESS  0x1E // TODO: change it to a macro

#define SELECTED_FREQ FREQ_SEL_48MHz

// Error codes to be displayed on the screen
// Since we can't use minicom through UART0 since this is used to send message on rf,
// we display error codes on the last line of the screen instead so we know if
// something goes wrong and what.
//
// Misc errors go from 0x01 to 0x0F
#define ERROR_FAULT_INFO	  0x01

// Communication errors go from 0x10 to 0x1F
#define ERROR_CC1101_SEND        0x10
#define ERROR_CC1101_RECEIVE     0x11
#define ERROR_INCORRECT_CHECKSUM 0x12

// PART ID INFO
// This has been gotten from lpcprog.
// The idea initially was to use UID as a salt for an encryption key,
// but due to the lack of time, encryption couldn't be implemented in the end.
//
// Part ID 0x3640c02b found on line 26
// Part ID is 0x3640c02b
// UID: 0x0214f5f5 - 0x4e434314 - 0x09393536 - 0x54001e3e

/***************************************************************************** */
/* Pins configuration */
/* pins blocks are passed to set_pins() for pins configuration.
 * Unused pin blocks can be removed safely with the corresponding set_pins() call
 * All pins blocks may be safelly merged in a single block for single set_pins() call..
 */
const struct pio_config common_pins[] = {
	/* UART 0 */
	{ LPC_UART0_RX_PIO_0_1,  LPC_IO_DIGITAL },
	{ LPC_UART0_TX_PIO_0_2,  LPC_IO_DIGITAL },
	/* I2C 0 */
	{ LPC_I2C0_SCL_PIO_0_10, (LPC_IO_DIGITAL | LPC_IO_OPEN_DRAIN_ENABLE) },
	{ LPC_I2C0_SDA_PIO_0_11, (LPC_IO_DIGITAL | LPC_IO_OPEN_DRAIN_ENABLE) },
	/* SPI */
	{ LPC_SSP0_SCLK_PIO_0_14, LPC_IO_DIGITAL },
	{ LPC_SSP0_MOSI_PIO_0_17, LPC_IO_DIGITAL },
	{ LPC_SSP0_MISO_PIO_0_16, LPC_IO_DIGITAL },
	/* ADC */
	{ LPC_ADC_AD0_PIO_0_30, LPC_IO_ANALOG },
	{ LPC_ADC_AD1_PIO_0_31, LPC_IO_ANALOG },
	{ LPC_ADC_AD2_PIO_1_0,  LPC_IO_ANALOG },
	ARRAY_LAST_PIO,
};

const struct pio cc1101_cs_pin = LPC_GPIO_0_15;
const struct pio cc1101_miso_pin = LPC_SSP0_MISO_PIO_0_16;
const struct pio cc1101_gdo0 = LPC_GPIO_0_6;
const struct pio cc1101_gdo2 = LPC_GPIO_0_7;

// We're going to be using the green and red LEDs to warn about an error
// instead of UART0, since it will be use to transfer data.
const struct pio status_led_green = LPC_GPIO_0_28;
const struct pio status_led_red = LPC_GPIO_0_29;

const struct pio button = LPC_GPIO_0_12; // ISP button


/***************************************************************************** */
/* Basic system init and configuration */

void system_init()
{
	/* Stop the Watchdog */
	startup_watchdog_disable(); /* Do it right now, before it gets a chance to break in */
	system_set_default_power_state();
	clock_config(SELECTED_FREQ);
	set_pins(common_pins);
	gpio_on();
	status_led_config(&status_led_green, &status_led_red);

	/* System tick timer MUST be configured and running in order to use the sleeping
	 * functions */
	systick_timer_on(1); /* 1ms */
	systick_start();

	// Clearing the LEDs
	gpio_clear(status_led_red);
	gpio_clear(status_led_green);
}

/******************************************************************************/
/* RF Communication */
#define RF_BUFF_LEN 64

static volatile int check_rx = 0;
void rf_rx_calback(uint32_t gpio)
{
	check_rx = 1;
}

static uint8_t rf_specific_settings[] = {
	CC1101_REGS(gdo_config[2]), 0x07, /* GDO_0 - Assert on CRC OK | Disable temp sensor */
	CC1101_REGS(gdo_config[0]), 0x2E, /* GDO_2 - FIXME : do something usefull with it for tests */
	CC1101_REGS(pkt_ctrl[0]), 0x0F, /* Accept all sync, CRC err auto flush, Append, Addr check and Bcast */
#if (RF_915MHz == 1)
	/* FIXME : Add here a define protected list of settings for 915MHz configuration */
#endif
};

/* RF config */
void rf_config(void)
{
	config_gpio(&cc1101_gdo0, LPC_IO_MODE_PULL_UP, GPIO_DIR_IN, 0);
	cc1101_init(0, &cc1101_cs_pin, &cc1101_miso_pin); /* ssp_num, cs_pin, miso_pin */
	/* Set default config */
	cc1101_config();
	/* And change application specific settings */
	cc1101_update_config(rf_specific_settings, sizeof(rf_specific_settings));
	set_gpio_callback(rf_rx_calback, &cc1101_gdo0, EDGE_RISING);
	cc1101_set_address(MODULE_ADDRESS);

#ifdef DEBUG
	uprintf(UART0, "CC1101 RF link init done.\n\r");
#endif
}

/* Payload types
 *
 * In order to send and receive data, whether it is values from the sensors
 * or an order change request to the sensors' display, we encapsulate it
 * in a struct to make it easier to handle.
 *
 */

// Packets containing values received from the sensors go here
typedef struct packet_t
{
	unsigned char source;
	unsigned char checksum;
	unsigned char message_type;
	unsigned char data[47];
} packet_t;

// This will be used to transfer data from where we got it (rf) to the USB (UART0)
static volatile packet_t cc_tx_packet;

// Calculating checksum
// We calculate it here rather than on the Python platform for two reasons:
// 1. It's calculated as close to the transmittors as possible before sending
// 2. When receiving, we can drop the packet as soon as possible if it's incorrect
unsigned char checksum(unsigned char message[], int nBytes) 
{
	unsigned char sum = 0;

	while (nBytes-- > 0)
	{
		int carry = (sum + *message > 255) ? 1 : 0;
		sum += *(message++) + carry;
	}

	return (~sum);
}

// Function called when data comes from the radio
void handle_rf_rx_data(void)
{
	uint8_t data[RF_BUFF_LEN];
	uint8_t status = 0;

	/* Check for received packet (and get it if any) */
	cc1101_receive_packet(data, RF_BUFF_LEN, &status);
	
	/* Go back to RX mode */
	cc1101_enter_rx_mode();

#ifdef DEBUG
	uprintf(UART0, "RF: ret:%d, st: %d.\n\r", ret, status);
#endif

	// We instantate it locally so we don't mess up with volatile data (yet :))
	packet_t received_payload;

	// Address verification
	if(data[1] == MODULE_ADDRESS)
	{
		// We use the led to signal we're handling the data.
		// However, it barely blinks so it's barely noticeable, but still.
		gpio_clear(status_led_green);
		gpio_set(status_led_red);

		// Copy the received data in our own struct so we can handle it better
		memcpy(&received_payload, &data[2], sizeof(packet_t));

		// Sending our sensors values on the USB, which will then
		// be handled on the Raspberry Pi and then to the app.
		// We only do that if the checksum is correct though.
		if(checksum(received_payload.data, 47) == received_payload.checksum)
			uprintf(UART0, "%x;%x;%x;%s\n\r", 
				received_payload.source,
				received_payload.checksum,
				received_payload.message_type,
				received_payload.data);
		else
			uprintf(UART0, "%x;%x;%x;ERROR: incorrect checksum. Ask for the data again.",
				received_payload.source,
				received_payload.checksum,
				received_payload.message_type);

		// We're done handling the data, so we're resetting the LEDs.
		gpio_clear(status_led_red);
		gpio_set(status_led_green);
	}	   
}


/* Data sent on radio comes from the UART, put any data received from UART in
 * cc_tx_buff and send when either '\r' or '\n' is received.
 * This function is very simple and data received between cc_tx flag set and
 * cc_ptr rewind to 0 may be lost. */
static volatile uint32_t cc_tx = 0;
static volatile uint8_t cc_tx_buff[RF_BUFF_LEN];
static volatile uint8_t cc_ptr = 0;
static volatile unsigned char cc_checksum = 0;
void handle_uart_cmd(uint8_t c)
{
#ifdef DEBUG
	uprintf(UART0, "Received command : %c, buffer size: %d.\n\r",c,cc_ptr);
#endif

	// Data
	// Most of the data is handled in the main loop, so we just use it as it is
	// passed here
	if (cc_ptr < RF_BUFF_LEN)
	{
		cc_tx_buff[cc_ptr++] = c;
	} else {
		// Reset the pointer
		cc_ptr = 0;
	}
	
	if ((c == '\n') || (c == '\r') || (cc_ptr>=63)) {
		// Using the leds again to signal we're ready to send
		gpio_clear(status_led_green);
		gpio_set(status_led_red);

		// Setting the "please send me" flag
		cc_tx = 1;

		// Resetting the pointer
		cc_ptr = 0;

		// Resetting the leds
		gpio_clear(status_led_red);
		gpio_set(status_led_green);
	}
}

void send_on_rf(void)
{
	uint8_t cc_tx_data[sizeof(packet_t) + 2];
	int ret = 0;
	packet_t tbs_packet;

	/* Create a local copy */
	unsigned char packet_data[47];
	memcpy((char*)&packet_data, (char*)&(cc_tx_buff[2]), 47);
	tbs_packet.source = MODULE_ADDRESS; // Address is set at compile time
	tbs_packet.checksum = checksum(packet_data, 47);
	tbs_packet.message_type = cc_tx_buff[1];
	memcpy((char*)&(tbs_packet.data), &packet_data, 47);

	// Preparing our packet by copying our payload inside
	// 0 and 1 indexes are for length and destination, respectively
	memcpy((char*)&(cc_tx_data[2]), &tbs_packet, sizeof(packet_t));

	/* Prepare buffer for sending */
	// Length
	cc_tx_data[0] = sizeof(packet_t) + 1;
	// Destination
	// We don't hardcode the destination so it can reply to anyone
	cc_tx_data[1] = cc_tx_buff[0];

	/* Send */
	if (cc1101_tx_fifo_state() != 0) {
		cc1101_flush_tx_fifo();
	}
	ret = cc1101_send_packet(cc_tx_data, (sizeof(packet_t) + 2));
	if(ret < 0)
	{
		// Since we don't use UART to signal problems and we don't have a screen
		// here either, we're using what we can, aka the LEDs again.
		gpio_clear(status_led_green);
		gpio_set(status_led_red);
	}

#ifdef DEBUG
	uprintf(UART0, "Tx ret: %d\n\r", ret);
#endif
}

/**************************************************************************** */
int main(void)
{
	// Setup phase
	system_init();
	uart_on(UART0, 115200, handle_uart_cmd);
	i2c_on(I2C0, I2C_CLK_100KHz, I2C_MASTER);
	ssp_master_on(0, LPC_SSP_FRAME_SPI, 8, 4*1000*1000); /* bus_num, frame_type, data_width, rate */

	/* Radio */
	rf_config();

	// When everything is up and running, we use the green LED
	gpio_set(status_led_green);

	while (1)
	{
		uint8_t status = 0;

		/* RF */
		if (cc_tx == 1) 
		{
			send_on_rf();
			cc_tx = 0;
		}

		/* Do not leave radio in an unknown or unwated state */
		do
		{
			status = (cc1101_read_status() & CC1101_STATE_MASK);
		} while (status == CC1101_STATE_TX);

		if (status != CC1101_STATE_RX) {
			static uint8_t loop = 0;
			loop++;
			if (loop > 10)
			{
				if (cc1101_rx_fifo_state() != 0)
				{
					cc1101_flush_rx_fifo();
				}
				cc1101_enter_rx_mode();
				loop = 0;
			}
		}

		if (check_rx == 1)
		{
			handle_rf_rx_data();
			check_rx = 0;
		}
	}
	return 0;
}