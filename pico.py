from gpiozero import Motor, PhaseEnableMotor
from gpiozero import SourceMixin, CompositeDevice
import gpiozero

class Robot(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` to represent a generic dual-motor robot.

    This class is constructed with two motor instances representing the left
    and right wheels of the robot respectively. For example, if the left
    motor's controller is connected to GPIOs 4 and 14, while the right motor's
    controller is connected to GPIOs 17 and 18 then the following example will
    drive the robot forward::

        from gpiozero import Robot

        robot = Robot(left=Motor(4, 14), right=Motor(17, 18))
        robot.forward()

    :type left: Motor or PhaseEnableMotor
    :param left:
        A :class:`~gpiozero.Motor` or a :class:`~gpiozero.PhaseEnableMotor`
        for the left wheel of the robot.

    :type right: Motor or PhaseEnableMotor
    :param right:
        A :class:`~gpiozero.Motor` or a :class:`~gpiozero.PhaseEnableMotor`
        for the right wheel of the robot.

    :type pin_factory: Factory or None
    :param pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. attribute:: left_motor

        The :class:`Motor` on the left of the robot.

    .. attribute:: right_motor

        The :class:`Motor` on the right of the robot.
    """
    def __init__(self, left, right, *, pin_factory=None):
        if not isinstance(left, (Motor, PhaseEnableMotor)):
            if isinstance(left, tuple):
                warnings.warn(
                    DeprecationWarning(
                        "Passing a tuple as the left parameter of the Robot "
                        "constructor is deprecated; please pass a Motor or "
                        "PhaseEnableMotor instance instead"))
                left = Motor(*left, pin_factory=pin_factory)
            else:
                raise GPIOPinMissing('left must be a Motor or PhaseEnableMotor')
        if not isinstance(right, (Motor, PhaseEnableMotor)):
            if isinstance(right, tuple):
                warnings.warn(
                    DeprecationWarning(
                        "Passing a tuple as the right parameter of the Robot "
                        "constructor is deprecated; please pass a Motor or "
                        "PhaseEnableMotor instance instead"))
                right = Motor(*right, pin_factory=pin_factory)
            else:
                raise GPIOPinMissing('right must be a Motor or PhaseEnableMotor')
        super().__init__(left_motor=left, right_motor=right,
                         _order=('left_motor', 'right_motor'),
                         pin_factory=pin_factory)

    @property
    def value(self):
        """
        Represents the motion of the robot as a tuple of (left_motor_speed,
        right_motor_speed) with ``(-1, -1)`` representing full speed backwards,
        ``(1, 1)`` representing full speed forwards, and ``(0, 0)``
        representing stopped.
        """
        return super().value

    @value.setter
    def value(self, value):
        self.left_motor.value, self.right_motor.value = value

    def forward(self, speed=1, *, curve_left=0, curve_right=0):
        """
        Drive the robot forward by running both motors forward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving forwards, by driving the
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving forwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
        """
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError("curve_left and curve_right can't be used at "
                             "the same time")
        self.left_motor.forward(speed * (1 - curve_left))
        self.right_motor.forward(speed * (1 - curve_right))


    def backward(self, speed=1, *, curve_left=0, curve_right=0):
        """
        Drive the robot backward by running both motors backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.

        :param float curve_left:
            The amount to curve left while moving backwards, by driving the
            left motor at a slower speed. Maximum *curve_left* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_right*.

        :param float curve_right:
            The amount to curve right while moving backwards, by driving the
            right motor at a slower speed. Maximum *curve_right* is 1, the
            default is 0 (no curve). This parameter can only be specified as a
            keyword parameter, and is mutually exclusive with *curve_left*.
        """
        if not 0 <= curve_left <= 1:
            raise ValueError('curve_left must be between 0 and 1')
        if not 0 <= curve_right <= 1:
            raise ValueError('curve_right must be between 0 and 1')
        if curve_left != 0 and curve_right != 0:
            raise ValueError("curve_left and curve_right can't be used at "
                             "the same time")
        self.left_motor.backward(speed * (1 - curve_left))
        self.right_motor.backward(speed * (1 - curve_right))


    def left(self, speed=1):
        """
        Make the robot turn left by running the right motor forward and left
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.right_motor.forward(speed)
        self.left_motor.backward(speed)


    def right(self, speed=1):
        """
        Make the robot turn right by running the left motor forward and right
        motor backward.

        :param float speed:
            Speed at which to drive the motors, as a value between 0 (stopped)
            and 1 (full speed). The default is 1.
        """
        self.left_motor.forward(speed)
        self.right_motor.backward(speed)



    def reverse(self):
        """
        Reverse the robot's current motor directions. If the robot is currently
        running full speed forward, it will run full speed backward. If the
        robot is turning left at half-speed, it will turn right at half-speed.
        If the robot is currently stopped it will remain stopped.
        """
        self.left_motor.reverse()
        self.right_motor.reverse()


    def stop(self):
        """
        Stop the robot.
        """
        self.left_motor.stop()
        self.right_motor.stop()
