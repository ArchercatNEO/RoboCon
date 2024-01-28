"""
The module containing the `Robot` class

Mainly provides init routine for the brain and binds attributes of the `Robot`
class to their respecitve classes
"""
import logging

from smbus2 import SMBus

from .vision import Camera, Detections, Vision
from .cytron import CytronBoard
from .greengiant import GreenGiantInternal, GreenGiantGPIOPinList, GreenGiantMotors

from . import marker_setup
from .marker_setup.teams import TEAM


_logger = logging.getLogger("robot")

# path to file with status of USB program copy,
# if this exists it is because the code on the robot has been copied from the robotusb
# this boot cycle. This is to highlight weird behaviour in the arena
COPY_STAT_FILE = "/tmp/usb_file_uploaded"


def setup_logging(level: (int | str)) -> None:
    """Display the just the message when logging events
    Sets the logging level to `level`"""

class NoCameraPresent(Exception):
    """Camera not connected."""
    def __str__(self) -> str: pass


class Robot():
    """Class for initialising and accessing robot hardware"""

    _initialised: bool = False

    def __init__(
            self,
            wait_for_start: bool = True,
            camera: (Camera | None) = None,
            max_motor_voltage: int = 6,
            logging_level: int = logging.INFO
        ) -> None:

        self.zone: TEAM = marker_setup.TEAM.RUSSET
        self._max_motor_voltage: int = max_motor_voltage

        self._initialised: bool = False
        self._start_pressed: bool = False
        self._warnings: list[str] = []

        self.enable_12v = True
        type(self)._initialised = True

        self._green_giant: GreenGiantInternal
        self._gg_version: int
        self._adc_max: int

        self.bus: SMBus
        self.gpio: GreenGiantGPIOPinList
        self.servos: GreenGiantGPIOPinList
        self.motors: (GreenGiantMotors | CytronBoard)

        self.camera: Camera
        self._vision: Vision

    def subsystem_init(self, camera: Camera) -> None:
        """Allows for initalisation of subsystems after instansating `Robot()`
        Can only be called once"""

    def report_hardware_status(self) -> None:
        """Print out a nice log message at the start of each robot init with
        the hardware status"""

    @property
    def enable_motors(self) -> bool:
        """Return if motors are currently enabled

        For the GG board this will be the state of the 12v line, which we cannot query,
        so return what it was set to.

        For the PiLow series the Motors have both a power control and a enable. Generally
        the Power should not be switched on and off, just the enable bits. The power may
        be tripped in extreame circumstances. I guess that here we want to report any 
        reason for  the motors not working, which includes power and enable

        """

    @enable_motors.setter
    def enable_motors(self, on: bool) -> (bool | None):
        """An nice alias for set_12v"""

    def stop(self) -> None:
        """Stops the robot and cuts power to the motors.
        does not touch the servos position."""

    def _parse_cmdline(self) -> None:
        """Parse the command line arguments"""

    def _wait_start_blink(self) -> None:
        """Blink status LED until start is pressed"""

    def _get_start_info(self) -> object:
        """Get the start infomation from the fifo which was passed as an arg"""

    def wait_start(self) -> (TEAM | None):
        """Wait for the start signal to happen"""

    def see(self, return_frame: bool = False)-> Detections:
        """Take a photo, detect markers in sene, attach RoboCon specific
        properties"""

    def __del__(self) -> None:
        """Frees hardware resources held by the vision object"""
