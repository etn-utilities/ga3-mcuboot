/**
 * @file ga3_watchdog.h
 * @author Rahul Gavade
 * @brief This is a header file for Watchdog timer realted functionalities.
 * @version
 * @date 2025-07-24
 *
 * @copyright Copyright Eaton Corporation {2023}
 *
 */
#if defined(CONFIG_SOC_NRF5340_CPUAPP)
#include "ga3_watchdog.h"
#include <hal/nrf_wdt.h>


/**
 * @brief This function will Disable the hardware watchdog timer on the nRF5340.
 *
 * This function is used to stop the watchdog timer (WDT) early in the bootloader
 * process to prevent unintended system resets during time-consuming operations
 * such as firmware image verification, USB DFU wait, or serial recovery.
 *
 * It replaces the default MCUboot macros `MCUBOOT_WATCHDOG_SETUP()` and
 * `MCUBOOT_WATCHDOG_FEED()` with a custom implementation that fully disables
 * the watchdog instead of periodically feeding it.
 *
 * The function performs the following steps:
 * - Enables the STOP task in the watchdog configuration by setting the
 *   `WDT_CONFIG_STOPEN_Msk` bit.
 * - Writes a magic unlock value (`0x6E524635`, ASCII for "nRF5") to the TSEN
 *   (Task Stop Enable) register to allow stopping the watchdog.
 * - Triggers the STOP task by writing `1` to `TASKS_STOP`.
 * - Waits for the `EVENTS_STOPPED` flag to be set, indicating the watchdog has stopped.
 * - Clears the `EVENTS_STOPPED` flag to reset the event state.
 * - Clears the TSEN register to prevent accidental reactivation of the STOP task.
 *
 * This approach ensures that the watchdog does not interfere with bootloader
 * operations, especially in scenarios where the boot process may take longer
 * than the watchdog timeout period.
 * 
 * Ref:- https://eaton-corp.atlassian.net/browse/GA-1681
 * Ref:- https://docs.nordicsemi.com/bundle/ps_nrf5340/page/wdt.html#ariaid-title5
 *
 * @note This function is specific to the nRF5340 and uses the NRF_WDT0 peripheral.
 *       It should be called early in the bootloader before any long-running tasks.
 *
 * @return void
 */
void hw_watchdog_disable()
{
    // Enable STOP task in CONFIG
    NRF_WDT0->CONFIG |= WDT_CONFIG_STOPEN_Msk;

    // Write unlock value to TSEN
    NRF_WDT0->TSEN = 0x6E524635;

    // Trigger STOP task
    NRF_WDT0->TASKS_STOP = 1;

    // Wait for STOPPED event (optional)
    while (NRF_WDT0->EVENTS_STOPPED == 0) {
        // Busy wait
    }

    // Clear STOPPED event
    NRF_WDT0->EVENTS_STOPPED = 0;

    // Clear TSEN to avoid accidental STOP
    NRF_WDT0->TSEN = 0x00000000;
}
#endif // CONFIG_SOC_NRF5340_CPUAPP
