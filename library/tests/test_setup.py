import mock


def test_setup(smbus2, GPIO):
    from hyperpixel2r import Touch

    touch = Touch()

    GPIO.setmode.assert_has_calls((
        mock.call(GPIO.BCM),
    ))

    GPIO.setup.assert_has_calls((
        mock.call(touch._interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP),
    ))

    del touch
