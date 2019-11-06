// import WonderJS from './wonder.min.js';

var $builtinmodule = function(name) {
    var mod = {};
    
    mod.Robot = Sk.misceval.buildClass(mod, function($gbl, $loc) {
        $loc.__init__ = new Sk.builtin.func(function(self) {
            /*
            return new Sk.misceval.promiseToSuspension( new Promise(function(resolve) {
                import('/wonder.min.js').then( module => {
                    console.log('Imported wonder.min.js');
                    console.log(module);
                    console.log(module.Module);
                    console.log(module.WonderJS);
                    console.log(window.moop);
                    module.connect();
                    module.WonderJS.connect();
                    resolve();
                });
            }));
            */
            self.robot = null;
            return new Sk.misceval.promiseToSuspension( new Promise( resolve => {
                Wonder.addEventListener('onconnect', _robot => {
                    self.robot = _robot;
                    resolve();
                });
                Wonder.connect();
            }));
        });

        $loc.pose = new Sk.builtin.func(function(self, x, y, degrees, time) {
            self.robot.command.pose(x, y, degrees, time);
        });
    }, 'Robot', []);

    return mod;
}
