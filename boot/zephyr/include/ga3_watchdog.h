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

#ifndef GA3_WATCHDOG_H
#define GA3_WATCHDOG_H


/**
 * @brief Disables the hardware watchdog timer on the nRF5340.
 *
 * This function stops the watchdog timer by enabling the STOP task,
 * unlocking the TSEN register, triggering the STOP task, and waiting
 * for the STOPPED event. It then clears the STOPPED event and resets
 * the TSEN register to prevent accidental reactivation.
 *
 * @return void
 */

void hw_watchdog_disable();

#endif // HW_WATCHDOG_H ends here