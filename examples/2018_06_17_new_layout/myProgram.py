import mepy

class myProgram(mepy.Program):

    def init(self, configurations):
        super(configurations)

    def set_speed(self, speed):

        right_motor = self.hardware.getByName('right motor')
        left_motor = self.hardware.getByName('left motor')

        right_motor.set_speed(speed)
        left_motor.set_speed(speed)


    def 