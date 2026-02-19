/*
 * Zigbee Custom Server Example (Receiver)
 */
#pragma once

#include "esp_zigbee_core.h"

/* Zigbee configuration */
#define MAX_CHILDREN                    10
#define INSTALLCODE_POLICY_ENABLE       false
#define HA_SERVER_ENDPOINT              10
#define ESP_ZB_PRIMARY_CHANNEL_MASK     (1l << 13)

/* Basic manufacturer information */
#define ESP_MANUFACTURER_NAME "\x09""ESPRESSIF"
#define ESP_MODEL_IDENTIFIER "\x07"CONFIG_IDF_TARGET

/* Custom Attribute ID */
#define ESP_ZB_ZCL_ATTR_CUSTOM_DATA_ID  0xFF01

#define ESP_ZB_ZC_CONFIG()                                              \
    {                                                                   \
        .esp_zb_role = ESP_ZB_DEVICE_TYPE_COORDINATOR,                  \
        .install_code_policy = INSTALLCODE_POLICY_ENABLE,               \
        .nwk_cfg.zczr_cfg = {                                           \
            .max_children = MAX_CHILDREN,                               \
        },                                                              \
    }

#define ESP_ZB_DEFAULT_RADIO_CONFIG()       \
    {                                       \
        .radio_mode = ZB_RADIO_MODE_NATIVE, \
    }

#define ESP_ZB_DEFAULT_HOST_CONFIG()                          \
    {                                                         \
        .host_connection_mode = ZB_HOST_CONNECTION_MODE_NONE, \
    }