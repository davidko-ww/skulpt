
import future
import impl
import time

# Minimum timeout for waiting for robot events to finish, such as playing
# sounds, poses, etc.
MIN_TIMEOUT = 0.5

def iGen():
    # Index generator
    i = 0
    while True:
        yield i
        i += 1

class Obstacle:
    Left = iGen()
    Right = iGen()
    Rear = iGen()

class ObstacleState:
    NotSeen = iGen()
    Seen = iGen()

class Buttons:
    Main = iGen()
    Circle = iGen()
    Square = iGen()
    Triangle = iGen()

class ButtonState:
    Up = iGen()
    Down = iGen()

class Heard:
    Clap = iGen()
    Voice = iGen()

class EventCallback:
    def __init__(self, event_id, callback):
        # event_id: e.g. ButtonState.Up
        # callback: The callback to call if the event is triggered
        self.event_id = event_id
        self.callback = callback

def sensors_to_eventlist(sensors):
    events = {}

class EventHandler:
    def __init__(self):
        self._last_event_obj = None
        self._callbacks = []
        self._id_index = 0

    def register_callback(self, event_callback):
        # event_callback should be an instance of EventCallback
        # Returns an ID number for the new event handler
        event_callback.id = self._id_index
        self._id_index += 1
        self._callbacks.append(event_callback)
        return event_callback.id

    def deregister_callback(self, callback_id):
        filter(lambda x: x.id != callback_id, self._callbacks)

    def handle_sensors(self, sensors):
        if self._last_event_obj is None:
            self._last_event_obj = sensors
            return

class Robot(impl.RobotImpl):
    def __init__(self, *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self._event_handlers = []
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
        # bit_string is a string of 12 ones and zeroes. e.g. "101100111011"
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
        fut = self.sound_async(filename, volume)
        fut.wait()

    def pose_async(self, x, y, degrees, pose_time):
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
        fut = self.pose_async(x, y, degrees, time)
        fut.wait()

    def head_pan_async(self, degrees):
        if degrees > 120:
            degrees = 120
        if degrees < -120:
            degrees = -120
        head_pan_threshold = 2.0
        self._head_pan(degrees)
        fut = future.Future()
        call_time = time.time()
        def head_pan_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
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
        fut = self.head_pan_async(degrees)
        fut.wait()

    def head_tilt_async(self, degrees):
        if degrees > 7:
            degrees = 7
        if degrees < -22.5:
            degrees = -22.5
        head_tilt_threshold = 2.0
        self._head_tilt(degrees)
        fut = future.Future()
        call_time = time.time()
        def head_tilt_done_cb(sensor_obj):
            if (time.time() - call_time) < MIN_TIMEOUT:
                return True
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
        # Add a callback for when the main button is pressed. The callback
        # signature should be:
        #     fn(button_down) -> bool
        # If the callback function returns False, the callback will not be
        # called again.
        return self.on_button('BUTTON_MAIN', fn)

    def on_button_1(self, fn):
        # Add a callback for when the button 1 is pressed. The callback
        # signature should be:
        #     fn(button_down) -> bool
        # If the callback function returns False, the callback will not be
        # called again.
        return self.on_button('BUTTON_1', fn)

    def on_button_2(self, fn):
        # Add a callback for when the button 2 is pressed. The callback
        # signature should be:
        #     fn(button_down) -> bool
        # If the callback function returns False, the callback will not be
        # called again.
        return self.on_button('BUTTON_2', fn)

    def on_button_3(self, fn):
        # Add a callback for when the button 3 is pressed. The callback
        # signature should be:
        #     fn(button_down) -> bool
        # If the callback function returns False, the callback will not be
        # called again.
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
        return self.wait_until_button('BUTTON_MAIN')

    def wait_until_button_1(self):
        return self.wait_until_button('BUTTON_1')

    def wait_until_button_2(self):
        return self.wait_until_button('BUTTON_2')

    def wait_until_button_3(self):
        return self.wait_until_button('BUTTON_3')

    def ir_distance_left(self):
        return self._last_sensor_obj['DISTANCE_FRONT_LEFT_FACING']['cm']

    def ir_distance_right(self):
        return self._last_sensor_obj['DISTANCE_FRONT_RIGHT_FACING']['cm']

    def ir_distance_back(self):
        return self._last_sensor_obj['DISTANCE_BACK']['cm']

    def on_clap_heard(self, fn):
        # Add a callback for when a clap is heard. Callback signature:
        # fn() -> bool
        # if the callback returns False, it will not be called again if there
        # are additional claps.
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
        fut = future.Future()
        def _cb():
            fut.set_result(None)
            return False
        self.on_clap_heard(_cb)
        fut.wait()

    def get_mic_volume(self):
        # Get the current detected microphone volume
        return self._last_sensor_obj['MICROPHONE']['amp']

    def on_voice_heard(self, fn):
        # Add a callback for when a voice is heard. Callback signature:
        #     fn() -> bool
        # If the callback returns Fals, it will not be called again.

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
        fut = future.Future()
        def _cb():
            fut.set_result(None)
            return False
        self.on_voice_heard(_cb)
        fut.wait()
