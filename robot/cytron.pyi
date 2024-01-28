"""An interface to the cyctron motor board. A gpio pin is used for each motor
to give direction and has a PWM signal at 100Hz giving infomation about voltage
to apply
"""
_MAX_OUTPUT_VOLTAGE = 12

_PWM_PIN_1 = 26
_PWM_PIN_2 = 23
_DIR_PIN_1 = 25
_DIR_PIN_2 = 5

_WP_OUT = 1
_WP_PWM = 2

# Wiring pi's PWM has range 0-1024 but we want to present a range of 0-100
_WP_PWM_MAX = 1024
_RC_PWM_MAX = 100

def wp_to_rc_pwm(wp_pwm: int) -> float:
    """Convert from wiring pi's numbering to percentages"""


def rc_to_wp_pwm(rc_pwm: float) -> int:
    """Convert from percenatges to wiring pi's numbering"""


class CytronBoard():
    def __init__(self, max_motor_voltage: float) -> None:
        """The interface to the CytronBoard
        max_motor_voltage - The motors will be scaled so that this is the maxium
                            average voltage the Cyctron will output
        """
        self.power_scaling_factor = (
            max_motor_voltage / _MAX_OUTPUT_VOLTAGE) ** 2

        self._percentages = [0, 0]
        self._dir = [_DIR_PIN_1, _DIR_PIN_2]
        self._pwm_pins = [_PWM_PIN_1, _PWM_PIN_2]

    def __getitem__(self, index: int) -> int:
        """Returns the current PWM value in RC units. Adds a sign to represent"""

    def __setitem__(self, index: int, percent: int) -> None:
        """Clamps input value, converts from percentage to wiring pi format and
        sets a PWM format"""

    def stop(self) -> None:
        """Turns motors off"""