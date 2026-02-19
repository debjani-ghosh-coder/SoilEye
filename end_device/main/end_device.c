#include "end_device.h"
#include "esp_check.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "string.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/uart.h"
#include "driver/gpio.h"
#include "esp_timer.h"

/* ================= CONFIG ================= */
static const char *TAG = "SENSOR_CLIENT";

/* Pin Configuration */
#define RE_PIN          4
#define DE_PIN          14
#define MODBUS_RX_PIN   5
#define MODBUS_TX_PIN   13
#define MODBUS_UART_NUM UART_NUM_1
#define SERIAL_BAUD     9600    // Corrected to 9600 for Soil Sensor
#define TIMEOUT_MS      300

/* ============== MODBUS FRAMES ============== */
const uint8_t moisture[]     = {0x01, 0x03, 0x00, 0x12, 0x00, 0x01, 0x24, 0x0F};
const uint8_t temperature[]  = {0x01, 0x03, 0x00, 0x13, 0x00, 0x01, 0x75, 0xCF};
const uint8_t conductivity[] = {0x01, 0x03, 0x00, 0x15, 0x00, 0x01, 0x95, 0xCE};
const uint8_t phFrame[]      = {0x01, 0x03, 0x00, 0x06, 0x00, 0x01, 0x64, 0x0B};
const uint8_t nitrogen[]     = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const uint8_t phosphorus[]   = {0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const uint8_t potassium[]    = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

/* Remote device address info */
typedef struct {
    uint8_t  endpoint;
    uint16_t short_addr;
} remote_device_t;

remote_device_t remote_server = {0};
bool server_found = false;

/* ================= CRC16 ================= */
uint16_t crc16(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    while (len--) {
        crc ^= *data++;
        for (uint8_t i = 0; i < 8; i++) {
            crc = (crc & 1) ? (crc >> 1) ^ 0xA001 : (crc >> 1);
        }
    }
    return crc;
}

/* ============== MODBUS QUERY (Ported to ESP-IDF) ============== */
int16_t querySensor(const uint8_t *frame, uint8_t frameSize) {
    uint8_t responseValues[32]; // Buffer for response
    
    // Clear RX buffer
    uart_flush_input(MODBUS_UART_NUM);

    // Enable transmit (DE/RE HIGH)
    gpio_set_level(DE_PIN, 1);
    gpio_set_level(RE_PIN, 1);
    esp_rom_delay_us(200); // Tiny delay for stable switching

    // Write Data
    uart_write_bytes(MODBUS_UART_NUM, frame, frameSize);
    uart_wait_tx_done(MODBUS_UART_NUM, pdMS_TO_TICKS(100)); // Wait for TX complete

    // Enable receive (DE/RE LOW)
    gpio_set_level(DE_PIN, 0);
    gpio_set_level(RE_PIN, 0);

    // Read Response
    int len = uart_read_bytes(MODBUS_UART_NUM, responseValues, sizeof(responseValues), pdMS_TO_TICKS(TIMEOUT_MS));

    if (len < 7) return -32768;

    // Validate address & function
    if (responseValues[0] != 0x01 || responseValues[1] != 0x03)
        return -32768;

    // Validate CRC
    uint16_t receivedCRC = responseValues[len - 2] | (responseValues[len - 1] << 8);
    uint16_t computedCRC = crc16(responseValues, len - 2);

    if (receivedCRC != computedCRC)
        return -32768;

    // Extract register value (Big Endian from Modbus to Native int16)
    return (int16_t)((responseValues[3] << 8) | responseValues[4]);
}

/* ================= SENSOR & ZIGBEE TASK ================= */
void sensor_task(void *pvParameters)
{
    // Initialize GPIO for DE/RE
    gpio_reset_pin(RE_PIN);
    gpio_reset_pin(DE_PIN);
    gpio_set_direction(RE_PIN, GPIO_MODE_OUTPUT);
    gpio_set_direction(DE_PIN, GPIO_MODE_OUTPUT);
    gpio_set_level(RE_PIN, 0);
    gpio_set_level(DE_PIN, 0);

    // Initialize UART
    uart_config_t uart_config = {
        .baud_rate = SERIAL_BAUD,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };
    uart_param_config(MODBUS_UART_NUM, &uart_config);
    uart_set_pin(MODBUS_UART_NUM, MODBUS_TX_PIN, MODBUS_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    uart_driver_install(MODBUS_UART_NUM, 256, 0, 0, NULL, 0);

    ESP_LOGI(TAG, "Sensor Task Started, waiting 1.5s...");
    vTaskDelay(pdMS_TO_TICKS(1500)); // Initial warmup delay

    static int16_t data[7];

    while (1) {
        // 1. Wait for interval
        vTaskDelay(pdMS_TO_TICKS(SEND_INTERVAL_MS));

        // 2. Query Sensors
        data[0] = querySensor(temperature,  sizeof(temperature));
        data[1] = querySensor(moisture,     sizeof(moisture));
        data[2] = querySensor(conductivity, sizeof(conductivity));
        data[3] = querySensor(phFrame,      sizeof(phFrame));
        data[4] = querySensor(nitrogen,     sizeof(nitrogen));
        data[5] = querySensor(phosphorus,   sizeof(phosphorus));
        data[6] = querySensor(potassium,    sizeof(potassium));

        // 3. Check availability
        uint8_t available = 1;
        for (uint8_t i = 0; i < 7; i++) {
            if (data[i] == -32768) {
                available = 0;
                break;
            }
        }

        if (!available) memset(data, 0, sizeof(data));

        // 4. Build 21-byte Frame
        uint8_t frame[21] = {0};
        frame[0] = 0x01;
        memcpy(&frame[1], data, 14); // Copy 7 * 2 bytes
        frame[15] = available;
        
        uint16_t crc = crc16(frame, 19);
        frame[19] = crc & 0xFF;
        frame[20] = crc >> 8;

        // --- PREPARE LOG STRING (Done regardless of connection) ---
        char payload_str[150];
        int pos = 0;
        pos += sprintf(&payload_str[pos], "(");
        for (int i = 0; i < 21; i++) {
            pos += sprintf(&payload_str[pos], "%d", frame[i]);
            if (i < 20) {
                pos += sprintf(&payload_str[pos], ", ");
            }
        }
        sprintf(&payload_str[pos], ")");
        // --------------------------------------------------------

        // 5. Send via Zigbee if server is found
        if (server_found) {
            esp_zb_zcl_write_attr_cmd_t write_req;
            write_req.zcl_basic_cmd.dst_addr_u.addr_short = remote_server.short_addr;
            write_req.zcl_basic_cmd.dst_endpoint = remote_server.endpoint;
            write_req.zcl_basic_cmd.src_endpoint = HA_CLIENT_ENDPOINT;
            write_req.address_mode = ESP_ZB_APS_ADDR_MODE_16_ENDP_PRESENT;
            write_req.clusterID = ESP_ZB_ZCL_CLUSTER_ID_BASIC;
            write_req.attr_number = 1;

            // --- FIXED LINE: Correctly disable default response ---
            write_req.dis_default_resp = 1; 
            // ----------------------------------------------------

            esp_zb_zcl_attribute_t attr_field;
            attr_field.id = ESP_ZB_ZCL_ATTR_CUSTOM_DATA_ID;
            attr_field.data.type = ESP_ZB_ZCL_ATTR_TYPE_OCTET_STRING;
            
            uint8_t zb_payload[22];
            zb_payload[0] = 21; // Length
            memcpy(&zb_payload[1], frame, 21); // Data

            attr_field.data.size = sizeof(zb_payload);
            attr_field.data.value = zb_payload;
            write_req.attr_field = &attr_field;

            esp_zb_lock_acquire(portMAX_DELAY);
            esp_zb_zcl_write_attr_cmd_req(&write_req);
            esp_zb_lock_release();
            
            ESP_LOGI(TAG, "SENT via Zigbee: %s", payload_str);
        } 
        else {
            ESP_LOGW(TAG, "Zigbee Disconnected - READ ONLY: %s", payload_str);
        }
    }
}

/* Callback when server is found */
static void user_find_cb(esp_zb_zdp_status_t zdo_status, uint16_t addr, uint8_t endpoint, void *user_ctx)
{
    if (zdo_status == ESP_ZB_ZDP_STATUS_SUCCESS) {
        ESP_LOGI(TAG, "Found Server! Address: 0x%x, Endpoint: %d", addr, endpoint);
        remote_server.short_addr = addr;
        remote_server.endpoint = endpoint;
        server_found = true;
    }
}

static void bdb_start_top_level_commissioning_cb(uint8_t mode_mask)
{
    ESP_ERROR_CHECK(esp_zb_bdb_start_top_level_commissioning(mode_mask));
}

void esp_zb_app_signal_handler(esp_zb_app_signal_t *signal_struct)
{
    uint32_t *p_sg_p = signal_struct->p_app_signal;
    esp_err_t err_status = signal_struct->esp_err_status;
    esp_zb_app_signal_type_t sig_type = *p_sg_p;

    switch (sig_type) {
    case ESP_ZB_BDB_SIGNAL_DEVICE_FIRST_START:
    case ESP_ZB_BDB_SIGNAL_DEVICE_REBOOT:
    case ESP_ZB_BDB_SIGNAL_STEERING:
        if (err_status != ESP_OK) {
            ESP_LOGW(TAG, "Network steering failed, retrying...");
            esp_zb_scheduler_alarm((esp_zb_callback_t)bdb_start_top_level_commissioning_cb, ESP_ZB_BDB_MODE_NETWORK_STEERING, 1000);
        } else {
            ESP_LOGI(TAG, "Joined network successfully");
            /* Start Finding the Server */
            esp_zb_zdo_match_desc_req_param_t find_req;
            find_req.addr_of_interest = 0xFFFF; 
            find_req.dst_nwk_addr = 0xFFFF;
            esp_zb_zdo_find_on_off_light(&find_req, user_find_cb, NULL);
        }
        break;
    default:
        ESP_LOGI(TAG, "ZDO signal: %s (0x%x)", esp_zb_zdo_signal_to_string(sig_type), sig_type);
        break;
    }
}

static void esp_zb_task(void *pvParameters)
{
    esp_zb_cfg_t zb_nwk_cfg = ESP_ZB_ZED_CONFIG();
    esp_zb_init(&zb_nwk_cfg);

    /* Basic Cluster Setup */
    esp_zb_attribute_list_t *esp_zb_basic_cluster = esp_zb_zcl_attr_list_create(ESP_ZB_ZCL_CLUSTER_ID_BASIC);
    esp_zb_basic_cluster_add_attr(esp_zb_basic_cluster, ESP_ZB_ZCL_ATTR_BASIC_MANUFACTURER_NAME_ID, ESP_MANUFACTURER_NAME);
    esp_zb_basic_cluster_add_attr(esp_zb_basic_cluster, ESP_ZB_ZCL_ATTR_BASIC_MODEL_IDENTIFIER_ID, ESP_MODEL_IDENTIFIER);

    /* Endpoint Setup */
    esp_zb_cluster_list_t *esp_zb_cluster_list = esp_zb_zcl_cluster_list_create();
    esp_zb_cluster_list_add_basic_cluster(esp_zb_cluster_list, esp_zb_basic_cluster, ESP_ZB_ZCL_CLUSTER_SERVER_ROLE);

    esp_zb_ep_list_t *esp_zb_ep_list = esp_zb_ep_list_create();
    esp_zb_endpoint_config_t endpoint_config = {
        .endpoint = HA_CLIENT_ENDPOINT,
        .app_profile_id = ESP_ZB_AF_HA_PROFILE_ID,
        .app_device_id = ESP_ZB_HA_ON_OFF_SWITCH_DEVICE_ID,
        .app_device_version = 0
    };
    esp_zb_ep_list_add_ep(esp_zb_ep_list, esp_zb_cluster_list, endpoint_config);
    esp_zb_device_register(esp_zb_ep_list);

    esp_zb_set_primary_network_channel_set(ESP_ZB_PRIMARY_CHANNEL_MASK);
    ESP_ERROR_CHECK(esp_zb_start(true));
    esp_zb_stack_main_loop();
}

void app_main(void)
{
    esp_zb_platform_config_t config = {
        .radio_config = ESP_ZB_DEFAULT_RADIO_CONFIG(),
        .host_config = ESP_ZB_DEFAULT_HOST_CONFIG(),
    };
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_zb_platform_config(&config));
    
    // Start Zigbee Task
    xTaskCreate(esp_zb_task, "Zigbee_main", 4096, NULL, 5, NULL);
    
    // Start Sensor Task (Modbus)
    // Priority 4 (lower than Zigbee) to avoid starvation, stack size 4096
    xTaskCreate(sensor_task, "Sensor_main", 4096, NULL, 4, NULL);
}