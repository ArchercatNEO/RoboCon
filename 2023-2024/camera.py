from robot.vision import Camera

class CameraExtended:
    def __init__(self, camera: Camera) -> None:
        self.camera = camera

    def see(self):
        self.camera.capture()