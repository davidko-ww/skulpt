// This is a thin wrapper for the API functions in WonderJS.
// Documentation for WonderJS here: https://github.com/playi/WonderJS/tree/master

var $builtinmodule = function(name) {
    var mod = {};
    
    mod.RobotImpl = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.__init__ = new Sk.builtin.func(function(self) {
            self.robot = null;

            // self._sendCommandResolve holds a Promise.resolve() function.
            // Upon calling any member function which sends a Bluetooth command,
            // this variable is set. The calling function then waits until 
            // the promise is fulfilled, which occurs in the onSensor()
            // callback. This effectively limits the rate of robot functions to 
            // once per sensor packet received.
            self._sendCommandResolve = null;
            self._sensor_event_handlers = [];
            var onSensor = function(sensors_obj) {
                if(self._sendCommandResolve) {
                    self._sendCommandResolve();
                    self._sendCommandResolve = null;
                }
                let id = sensors_obj.id;
                let sensors = sensors_obj.sensors;
                sensors = Sk.ffi.remapToPy(sensors);
                if(id == self.robot.id) {
                    let i = 0;
                    while ( i < self._sensor_event_handlers.length ) {
                        let rc = Sk.misceval.callsim(self._sensor_event_handlers[i], sensors);
                        rc = Sk.ffi.remapToJs(rc);
                        if ( rc ) {
                            i++;
                        } else {
                            self._sensor_event_handlers.splice(i, 1);
                        }
                    };
                }
            };
            Wonder.addEventListener('onsensor', onSensor);

            return new Sk.misceval.promiseToSuspension( new Promise( resolve => {
                Wonder.addEventListener('onconnect', _robot => {
                    self.robot = _robot;
                    window.lastConnectedRobot = _robot;
                    if(window.connectedRobots === undefined) {
                        window.connectedRobots = [];
                    }
                    window.connectedRobots.push(_robot.id);
                    resolve();
                });
                try {
                    Wonder.connect();
                } catch (e) {
                    if (e instanceof AlreadyConnected) {
                        self.robot = window.lastConnectedRobot;
                    } else {
                        throw e;
                    }
                }
            }));
        });

        $loc._add_sensor_event_listener = new Sk.builtin.func( (self, func) => {
            // Add a new sensor event listener. The callback function should
            // have the following prototype:
            //     bool func(sensor_object)
            // If the callback returns false, it will not be called again.
            self._sensor_event_handlers.push(func);
            console.log(self._sensor_event_handlers);
        });

        $loc._eye_ring = new Sk.builtin.func( (self, boolArray, brightness) => {
            boolArray = Sk.ffi.remapToJs(boolArray);
            brightness = Sk.ffi.remapToJs(brightness);
            self.robot.command.eyering(boolArray, brightness);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_all = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            g = Sk.ffi.remapToJs(g);
            b = Sk.ffi.remapToJs(b);
            self.robot.command.rgbAll(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_eye = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            g = Sk.ffi.remapToJs(g);
            b = Sk.ffi.remapToJs(b);
            self.robot.command.rgbEye(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_left_ear = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            self.robot.command.rgbLeftEar(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_right_ear = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            self.robot.command.rgbRightEar(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_chest = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            self.robot.command.rgbChest(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.rgb_button_main = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            self.robot.command.rgbButtonMain(r, g, b);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc._sound = new Sk.builtin.func( (self, filename, volume) => {
            filename = Sk.ffi.remapToJs(filename);
            volume = Sk.ffi.remapToJs(volume);
            self.robot.command.sound(filename, volume);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc._head_pan = new Sk.builtin.func( (self, degrees) => {
            degrees = Sk.ffi.remapToJs(degrees);
            self.robot.command.headPan(degrees);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc._head_tilt = new Sk.builtin.func( (self, degrees) => {
            degrees = Sk.ffi.remapToJs(degrees);
            self.robot.command.headTilt(degrees);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.linear_angular = new Sk.builtin.func( (self, cmPerSecond, degreesPerSecond) => {
            cmPerSecond = Sk.ffi.remapToJs(cmPerSecond);
            degreesPerSecond = Sk.ffi.remapToJs(degreesPerSecond);
            self.robot.command.linearAngular(cmPerSecond, degreesPerSecond);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc._pose = new Sk.builtin.func( (self, x, y, degrees, time) => {
            x = Sk.ffi.remapToJs(x);
            y = Sk.ffi.remapToJs(y);
            degrees = Sk.ffi.remapToJs(degrees);
            time = Sk.ffi.remapToJs(time);
            self.robot.command.pose(x, y, degrees, time);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

        $loc.wheel_speeds = new Sk.builtin.func( (self, leftCmS, rightCmS) => {
            left = Sk.ffi.remapToJs(leftCmS);
            right = Sk.ffi.remapToJs(RightCmS);
            self.robot.command.wheelSpeeds(left, right);
            return new Sk.misceval.promiseToSuspension( new Promise( function(resolve) {
                self._sendCommandResolve = resolve;
            }));
        });

    }, 'RobotImpl', []);

    return mod;
}
