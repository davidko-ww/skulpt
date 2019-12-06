
import future
try:
    import impl
except:
    import impl_stub as impl
    
import time

# Minimum timeout for waiting for robot events to finish, such as playing
# sounds, poses, etc.
MIN_TIMEOUT = 0.5

class Robot(impl.RobotImpl):
    """A class for controlling Dash, Dot, and Cue robots.

    This class contains a number of member functions to peform a variety of
    tasks related to Dash, Dot, and Cue robots. These tasks include:
        * Moving the robot
        * Getting sensor information from the robot
        * Registering callback functions to be invoked when certain events occur.

    Examples:

        Moving the robot forward 20 centimeters:

            import wonder
            robot = wonder.Robot()
            robot.pose(20, 0, 0, 1)

        Setting all RGB LEDs to purple:

            import wonder
            robot = wonder.Robot()
            robot.rgb_all(255, 0, 255)

        Very naive object following for 1 minute:

            import wonder
            import time
            robot = wonder.Robot()
            start_time = time.time()
            while (time.time() - start_time) < 60:
                distance = robot.ir_distance_left()
                if distance > 20:
                    robot.linear_angular(10, 0)
                if distance < 10:
                    robot.linear_angular(-10, 0)
                else:
                    robot.linear_angular(0, 0)
    """
    def __init__(self, *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self._state_vars = {}
        self._state_var_keys = 0
        self._last_sensor_obj = {}
        self._add_sensor_event_listener(self._on_sensor)
        # Wait for first sensor packet to arrive
        while len(self._last_sensor_obj) == 0:
            time.sleep(0.1)

    def _on_sensor(self, sensor_obj):
        self._last_sensor_obj.update(sensor_obj)
        return True

    def _new_state_var(self):
        self._state_vars[self._state_var_keys] = 0
        rc = self._state_var_keys
        self._state_var_keys += 1
        return rc

    def eye_ring(self, bit_string, brightness):
        """Set the eye ring pattern on Dash and Cue.

        Args:
            bit_string: A string of 12 "1" characters and "2" characters. e.g.
                "101100111011"
            brightness: A float value from 0 to 1
        """
        def f(x):
            if x == '0':
                return False
            elif x == '1':
                return True
            else:
                raise ValueError('bit_string must be a string of "0" and "1" characters')
        bool_array = list(map(f, bit_string))
        self._eye_ring(bool_array, brightness)

    def sound_async(self, filename, volume):
        """The asynchronous version of Robot.sound().

        See also: Robot.sound()

        Returns:
            A Future object. See: future.Future() in :mod:`future`
        """
        self._sound(filename, volume)
        fut = future.Future()
        call_time = time.time()
        def sound_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
            if not sensor_obj.SOUND_PLAYING.flag:
                fut.set_result(None)
                return False
            else:
                return True
        self._add_sensor_event_listener(sound_done_cb)
        return fut

    def sound(self, filename, volume):
        """Play a sound.

        Args:
            filename: A string containing the filename of a sound file on
                Dash/Dot/Cue to play.
            volume: A number from 0.0 to 1.0
        """
        fut = self.sound_async(filename, volume)
        fut.wait()

    def pose_async(self, x, y, degrees, pose_time):
        """Move the robot to a new position (asynchronous)

        See also: robot.pose()

        Returns: a wonder.future.Future object.
        """
        self._pose(x, y, degrees, pose_time)
        fut = future.Future()
        call_time = time.time()
        def pose_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
            try:
                # The watermark field is "sparse" so it may not appear in every sensor packet
                if sensor_obj['BODY_POSE']['watermark'] == 255:
                    fut.set_result(None)
                    return False
                else:
                    return True
            except KeyError:
                return True
        self._add_sensor_event_listener(pose_done_cb)
        return fut

    def pose(self, x, y, degrees, time):
        """Perform a 'pose' command.

        This commands moves the robot from its current position to a relative
        position (x,y). The coordinate system is fixed to Dash's body as shown in 
		ascii image below:

                    +X  (Forward)
                     ^
                     |         <-
                     |            \\
            +Y <--- Robot  +Angle |
            (Left)                /

        For example, the following command will move Dash so that it ends up 10
        centimeters forward and facing to the left:

            robot.pose(10, 0, 90, 1)

        Similarly, the following command will make Dash move so that it ends up 
        10 centimeters to the right of its starting position:

            robot.pose(0, -10, 0, 1)

        Finally, the next command turns Dash in place 30 degrees to the right:

            robot.pose(0, 0, -30, 1)

        Args:
            x: number of centimeters to move forward
            y: number of centimeters to move to the left
            degrees: Number of degrees counter-clockwise for the end position
                to be offset from the starting position.
            pose_time: Number of seconds allotted to complete the action.
                Larger numbers result in slower movement.
        """
        fut = self.pose_async(x, y, degrees, time)
        fut.wait()

    def head_pan_async(self, degrees):
        """ Pan Dash/Cue's head (asynchronous)

        See also: Robot.head_pan()

        Returns: A wonder.future.Future object.
        """
        if degrees > 120:
            degrees = 120
        if degrees < -120:
            degrees = -120
        head_pan_threshold = 2.0
        self._head_pan(degrees)
        fut = future.Future()
        call_time = time.time()
        head_pan_timeout = 1.0
        def head_pan_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
            if (time.time() - call_time) > head_pan_timeout:
                fut.set_result(None)
                return False
            try:
                pan_angle = sensor_obj['HEAD_POSITION_PAN']['degree']
            except KeyError:
                return True
            if abs(pan_angle - degrees) < head_pan_threshold:
                fut.set_result(None)
                return False
            else:
                return True
        self._add_sensor_event_listener(head_pan_done_cb)
        return fut

    def head_pan(self, degrees):
        """Pan Dash/Cue's head left or right.

        Args:
            degrees: Number of degrees to pan the head to the left.
        """
        fut = self.head_pan_async(degrees)
        fut.wait()

    def head_tilt_async(self, degrees):
        """Tilt Dash/Cue's head up or down.

        See Also: Robot.head_tilt()

        Returns: wonder.future.Future object.
        """
        if degrees > 7:
            degrees = 7
        if degrees < -22.5:
            degrees = -22.5
        head_tilt_threshold = 2.0
        self._head_tilt(degrees)
        fut = future.Future()
        call_time = time.time()
        head_tilt_timeout = 1.0
        def head_tilt_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
            if (time.time() - call_time) > head_tilt_timeout:
                fut.set_result(None)
                return False
            try:
                tilt_angle = sensor_obj['HEAD_POSITION_TILT']['degree']
            except KeyError:
                return True
            if abs(tilt_angle - degrees) < head_tilt_threshold:
                fut.set_result(None)
                return False
            else:
                return True
        self._add_sensor_event_listener(head_tilt_done_cb)
        return fut

    def head_tilt(self, degrees):
        """Tilt Dash/Cue's head up or down.

        Args:
            degrees: Number of degrees down. Use negative values to make the
                robot look up.
        """
        fut = self.head_tilt_async(degrees)
        fut.wait()

    def on_button(self, button_id, fn):
        # Register a callback for a button. Returns callback handler ID.
        # button_id: A string. One of 'BUTTON_MAIN', 'BUTTON_1', 'BUTTON_2', or
        #   'BUTTON_3'
        # fn: The callback function. Signature should be 'fn(button_down) -> bool'
        state_key = self._new_state_var()
        self._state_vars[state_key] = self._last_sensor_obj[button_id]['s']
        def _cb(sensor_obj):
            last_button_state = self._state_vars[state_key]

            try:
                button_down = sensor_obj[button_id]['s']
            except KeyError:
                return True

            rc = True
            if last_button_state != button_down:
                rc = fn(button_down)
                self._state_vars[state_key] = button_down
                if rc is not False:
                    rc = True
            return rc

        return self._add_sensor_event_listener(_cb)

    def on_button_main(self, fn):
        """Add a callback function which will be called when the main button is
        pressed.

        Args:
            fn: The function to call when the button is pressed. The function
                signature should be:

                    fn(button_down) -> bool

                If the callback function returns False, it will not be called
                again if the button is pressed again. "button_down" will be "1"
                if the button was pressed down or "0" if the button was raised.

        Example:

            import time
            import wonder

            robot = wonder.Robot() 

            def my_func(button_down):
                if button_down:
                    print('Button pressed!')
                else:
                    print('Button released!')
                return True

            robot.on_button_main(my_func)
            
            # Spin the program while waiting for button presses.
            while True:
                time.sleep(1)
        """
        return self.on_button('BUTTON_MAIN', fn)

    def on_button_1(self, fn):
        """Add a callback function which will be called when button 1 is pressed.

        See also: Robot.on_button_main()
        """
        return self.on_button('BUTTON_1', fn)

    def on_button_2(self, fn):
        """Add a callback function which will be called when button 2 is pressed.

        See also: Robot.on_button_main()
        """
        return self.on_button('BUTTON_2', fn)

    def on_button_3(self, fn):
        """Add a callback function which will be called when button 2 is pressed.

        See also: Robot.on_button_main()
        """
        return self.on_button('BUTTON_3', fn)

    def wait_until_button(self, button_id):
        # Wait for a button press.
        # button_id: A string. One of 'BUTTON_MAIN', 'BUTTON_1', 'BUTTON_2', 'BUTTON_3'
        fut = future.Future()
        def _cb(button_down):
            if button_down:
                fut.set_result(None) 
                return False
            return True
        self.on_button(button_id, _cb)
        fut.wait()

    def wait_until_button_main(self):
        """Halt the program until the main button is pressed.

        Example:
            import wonder

            robot = wonder.Robot()

            print("Please press the main button on the robot's head.")
            robot.wait_until_button_main()
            print("Button press detected!")
        """
        return self.wait_until_button('BUTTON_MAIN')

    def wait_until_button_1(self):
        """Halt the program until button 1 is pressed.

        See also: Robot.wait_until_button_main()
        """
        return self.wait_until_button('BUTTON_1')

    def wait_until_button_2(self):
        """Halt the program until button 2 is pressed.

        See also: Robot.wait_until_button_main()
        """
        return self.wait_until_button('BUTTON_2')

    def wait_until_button_3(self):
        """Halt the program until button 3 is pressed.

        See also: Robot.wait_until_button_main()
        """
        return self.wait_until_button('BUTTON_3')

    def ir_distance_left(self):
        """Get the estimated distance from the front-left IR sensor to any
        object.

        Returns:
            Floating point number from 0.0 to 50 indicating the approximate
                distance to an obstacle in centimeters.
        """
        return self._last_sensor_obj['DISTANCE_FRONT_LEFT_FACING']['cm']

    def ir_distance_right(self):
        """Get the estimated distance from the front-right IR sensor to any
        object.

        Returns:
            Floating point number from 0.0 to 50 indicating the approximate
                distance to an obstacle in centimeters.
        """
        return self._last_sensor_obj['DISTANCE_FRONT_RIGHT_FACING']['cm']

    def ir_distance_back(self):
        """Get the estimated distance from the rear IR sensor to any object.

        Returns:
            Floating point number from 0.0 to 50 indicating the approximate
                distance to an obstacle in centimeters.
        """
        return self._last_sensor_obj['DISTANCE_BACK']['cm']

    def attitude_pitch(self):
        """Get the pitch of the robot in degrees"""
        return self._last_sensor_obj['ATTITUDE']['attitudePitch']

    def attitude_roll(self):
        """Get the roll of the robot in degrees"""
        return self._last_sensor_obj['ATTITUDE']['attitudeRoll']

    def attitude_slope(self):
        """Get the slope of the robot in degrees"""
        return self._last_sensor_obj['ATTITUDE']['attitudeSlope']

    def on_robot_tilted(self, fn):
        """Add a callback function which will be called when the robot is tilted.

        Args:
            fn: The function to call when the robot is tilted or leveled.
                The function signature should be:

                    fn(tilt) -> bool

                when fn() is called, the tilt argument will be "True" if the 
                robot was straight but is now tilted, or "False" if the robot
                was tilted and is now level.

                If fn() returns False, it will not be called again for future
                tilt/level events.

        Example:

            import time
            import wonder

            robot = wonder.Robot()

            def my_func(tilt):
                if tilt:
                    print("Robot is tilted!")
                else:
                    print("Robot is level.")
            
            robot.on_robot_tilted(my_func)

            # Spin the program while waiting for tilt events.
            while True:
                time.sleep(1)
        """
        _s = {}
        _s['last_tilt'] = 0

        def _cb(sensor_obj):
            tilted = sensor_obj['ATTITUDE']['slopeType']
            if tilted != _s['last_tilt']:
                t = True
                if tilted == 0:
                    t = False
                rc = fn(t)
                _s['last_tilt'] = tilted
                if rc is not False:
                    return True
                return rc
            return True
        return self._add_sensor_event_listener(_cb)

    def wait_until_robot_tilted(self):
        """Halt the program until the robot is tilted"""
        fut = future.Future()
        def _cb(tilted):
            if tilted:
                fut.set_result(None)
                return False
            return True
        self.on_robot_tilted(_cb)
        fut.wait()

    def on_clap_heard(self, fn):
        """Add a callback function which will be called when a clap is heard

        Args:
            fn: The function to call when a clap is heard. The function
                signature should be:

                    fn() -> bool

                If the callback function returns False, it will not be called
                again if another clap is heard. 

        Example:

            import time
            import wonder

            robot = wonder.Robot() 

            def my_func():
                print('Clap heard!')
                # If we return False, this function will not be called again if
                # another clap is heard.
                return True

            robot.on_clap_heard(my_func)
            
            # Spin the program while waiting for claps.
            while True:
                time.sleep(1)
        """
        state_key = self._new_state_var()
        self._state_vars[state_key] = self._last_sensor_obj['MICROPHONE']['clap']
        def _cb(sensor_obj):
            last_clap_state = self._state_vars[state_key]

            try:
                clap_heard = sensor_obj['MICROPHONE']['clap']
            except KeyError:
                return True

            rc = True
            if (last_clap_state != clap_heard) and (clap_heard):
                rc = fn()
                if rc is not False:
                    rc = True
            self._state_vars[state_key] = clap_heard
            return rc

        return self._add_sensor_event_listener(_cb)

    def wait_until_clap(self):
        """Halt the program until a clap is heard.

        Example:
            import wonder

            robot = wonder.Robot()

            print("Please clap.")
            robot.wait_until_clap()
            print("Clap detected!")
        """
        fut = future.Future()
        def _cb():
            fut.set_result(None)
            return False
        self.on_clap_heard(_cb)
        fut.wait()

    def get_mic_volume(self):
        """Get the current ambient volume as detected by the robot's
        microphones.

        Returns: 
            A number between 0.0 and 1.0
        """
        return self._last_sensor_obj['MICROPHONE']['amp']

    def get_accelerometer(self):
        """Get the current accelerometer readings.

        Returns:
            A tuple of the form (x, y, z) where x, y, and z are the
            acceleration in units of Earth G's for the x, y, and z axes
            respectively. The axes are oriented such that the X axis points
            in the robot's forward direction, the Y axis points to the robot's
            left side, and the Z axis points up through the robot's head.
        """
        x = self._last_sensor_obj['ACCELEROMETER']['x']
        y = self._last_sensor_obj['ACCELEROMETER']['y']
        z = self._last_sensor_obj['ACCELEROMETER']['z']
        return (x, y, z)

    def get_gyro(self):
        """Get the current gyro readings.

        Returns:
            A tuple of the form (roll, pitch, yaw) where roll, pitch, and yaw
            are each in units of radians/second.
        """
        r = self._last_sensor_obj['GYROSCOPE']['r']
        p = self._last_sensor_obj['GYROSCOPE']['p']
        y = self._last_sensor_obj['GYROSCOPE']['y']
        return (r, p, y)

    def on_voice_heard(self, fn):
        """Add a callback function which will be called when a voice is heard.

        Args:
            fn: The function to call when a voice is heard. The function
                signature should be:

                    fn() -> bool

                If the callback function returns False, it will not be called
                again if another voice is heard. 

        Example:

            import time
            import wonder

            robot = wonder.Robot() 

            def my_func():
                print('Voice heard!')
                # If we return False, this function will not be called again if
                # another voice is heard.
                return True

            robot.on_voice_heard(my_func)
            
            # Spin the program while waiting for voice.
            while True:
                time.sleep(1)
        """

        # Number of consecutive volume events
        num_cons_hits = self._new_state_var() 
        voice_heard_state = self._new_state_var()

        self._state_vars[num_cons_hits] = 0
        voice_vol_upper_threshold = 0.1
        voice_vol_lower_threshold = 0.05
        if self.get_mic_volume() > voice_vol_lower_threshold:
            self._state_vars[voice_heard_state] = True
        else:
            self._state_vars[voice_heard_state] = False
        debounce_threshold = 1

        def _cb(sensor_obj):
            vol = sensor_obj['MICROPHONE']['amp']
            state = self._state_vars[voice_heard_state]
            debounce = self._state_vars[num_cons_hits]

            if state == False:
                if vol > voice_vol_upper_threshold:
                    if debounce > debounce_threshold:
                        self._state_vars[num_cons_hits] = 0
                        self._state_vars[voice_heard_state] = True
                        return fn()
                    else:
                        self._state_vars[num_cons_hits] += 1
                else:
                    self._state_vars[num_cons_hits] = 0
            else:
                if vol < voice_vol_lower_threshold:
                    if debounce > debounce_threshold:
                        self._state_vars[num_cons_hits] = 0
                        self._state_vars[voice_heard_state] = False
                    else:
                        self._state_vars[num_cons_hits] += 1
                else:
                    self._state_vars[num_cons_hits] = 0
            return True

        return self._add_sensor_event_listener(_cb)

    def wait_until_voice(self):
        """Halt the program until a voice is heard.

        Example:
            import wonder

            robot = wonder.Robot()

            print("Please speak.")
            robot.wait_until_voice()
            print("Voice detected!")
        """
        fut = future.Future()
        def _cb():
            fut.set_result(None)
            return False
        self.on_voice_heard(_cb)
        fut.wait()
