// This is a thin wrapper for the API functions in WonderJS.
// Documentation for WonderJS here: https://github.com/playi/WonderJS/tree/master

var $builtinmodule = function(name) {
    var mod = {};
    
    mod.RobotImpl = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.__init__ = new Sk.builtin.func(function(self) {
            self.robot = null;

            self._sensor_event_handlers = [];
            var onSensor = function(sensors_obj) {
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

        $loc._addSensorEventListener = new Sk.builtin.func( (self, func) => {
            // Add a new sensor event listener. The callback function should
            // have the following prototype:
            //     bool func(sensor_object)
            // If the callback returns false, it will not be called again.
            self._sensor_event_handlers.push(func);
            console.log(self._sensor_event_handlers);
        });

        $loc.eyeRing = new Sk.builtin.func( (self, boolArray, brightness) => {
            boolArray = Sk.ffi.remapToJs(boolArray);
            brightness = Sk.ffi.remapToJs(brightness);
            return self.robot.command.eyeRing(boolArray, brightness);
        });

        $loc.rgbAll = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbAll(r, g, b);
        });

        $loc.rgbEye = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbEye(r, g, b);
        });

        $loc.rgbLeftEar = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbLeftEar(r, g, b);
        });

        $loc.rgbRightEar = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbRightEar(r, g, b);
        });

        $loc.rgbChest = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbChest(r, g, b);
        });

        $loc.rgbButtonMain = new Sk.builtin.func( (self, r, g, b) => {
            r = Sk.ffi.remapToJs(r);
            b = Sk.ffi.remapToJs(g);
            g = Sk.ffi.remapToJs(b);
            return self.robot.command.rgbButtonMain(r, g, b);
        });

        $loc._sound = new Sk.builtin.func( (self, filename, volume) => {
            filename = Sk.ffi.remapToJs(filename);
            volume = Sk.ffi.remapToJs(volume);
            return self.robot.command.sound(filename, volume);
        });

        $loc._headPan = new Sk.builtin.func( (self, degrees) => {
            degrees = Sk.ffi.remapToJs(degrees);
            return self.robot.command.headPan(degrees);
        });

        $loc._headTilt = new Sk.builtin.func( (self, degrees) => {
            degrees = Sk.ffi.remapToJs(degrees);
            return self.robot.command.headTilt(degrees);
        });

        $loc.linearAngular = new Sk.builtin.func( (self, cmPerSecond, degreesPerSecond) => {
            cmPerSecond = Sk.ffi.remapToJs(cmPerSecond);
            degreesPerSecond = Sk.ffi.remapToJs(degreesPerSecond);
            return self.robot.command.linearAngular(cmPerSecond, degreesPerSecond);
        });

        $loc._pose = new Sk.builtin.func( (self, x, y, degrees, time) => {
            x = Sk.ffi.remapToJs(x);
            y = Sk.ffi.remapToJs(y);
            degrees = Sk.ffi.remapToJs(degrees);
            time = Sk.ffi.remapToJs(time);
            return self.robot.command.pose(x, y, degrees, time);
        });

        $loc.wheelSpeeds = new Sk.builtin.func( (self, leftCmS, rightCmS) => {
            left = Sk.ffi.remapToJs(leftCmS);
            right = Sk.ffi.remapToJs(RightCmS);
            return self.robot.command.wheelSpeeds(left, right);
        });

    }, 'RobotImpl', []);

    return mod;
}
