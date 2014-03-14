import sys, inspect, os
import jpype
import numpy as np

os.environ["R_HOME"] = "/Library/Frameworks/R.framework/Resources"

jvmargs = ["-Djava.class.path=./lib/jmotif.lib-0.97.jar:./lib/hackystatlogger.lib.jar:./lib/hackystatuserhome.lib.jar:./lib/weka.jar:./lib/rjava/jri/JRI.jar:./lib/rjava/jri/REngine.jar:./lib/rjava/jri/JRIEngine.jar"]

jpype.startJVM(jpype.getDefaultJVMPath(), *jvmargs)

#lots of code taken from https://github.com/neo4j-contrib/python-embedded/blob/master/src/main/python/neo4j/_backend.py

JAVA_CLASSES = (
    ('edu.hawaii.jmotif.sax.alphabet', ('NormalAlphabet',)),
    ('edu.hawaii.jmotif.sax', ('SAXFactory',)),
    ('edu.hawaii.jmotif.timeseries', ('TSUtils',)),
    ('org.rosuda.JRI', ('Rengine','REXP',)),
)   

isStatic = jpype.JPackage("java.lang.reflect").Modifier.isStatic
def _add_jvm_connection_boilerplate_to_class(CLASS):
    ''' In order for JPype to work in a threaded
    environment, each time we're in a new thread,
    the method jpype.attachThreadToJVM() needs to
    be called.
    This wraps all methods in a java class with
    boilerplate to check if the current thread
    is connected, and to connect it if that is
    not the case.
    '''
    def add_jvm_connection_boilerplate(fn):
        def decorator(*args,**kwargs):
            if not jpype.isThreadAttachedToJVM():
                jpype.attachThreadToJVM()
            return fn(*args, **kwargs)
        return decorator
    
    statics = []
    for m in CLASS.__javaclass__.getMethods():
        if isStatic(m.getModifiers()):
            statics.append(m.getName())
            
    for key, val in inspect.getmembers(CLASS):
        if not key.startswith("__") and hasattr(val,'__call__'):
            wrapped = add_jvm_connection_boilerplate(val)
            if key in statics:
                wrapped = staticmethod(wrapped)
            setattr(CLASS, key, wrapped)

# Import java classes
for pkg_name, class_names in JAVA_CLASSES:
    package = jpype.JPackage(pkg_name)
    for class_name in class_names:
        cls = getattr(package,class_name)
        _add_jvm_connection_boilerplate_to_class(cls)
        globals()[class_name] = cls

def create_long_vector(r_engine, lst):
   #not a huge fan of this approach, but its the only one i could get working
   str_list = ",".join(str(x) for x in lst)
   return r_engine.eval("c(" + str_list + ")")

#test jmotif
normal_a = NormalAlphabet()
ts = TSUtils.readTS("timeseries01.csv", 15);
sax = SAXFactory.ts2string(ts, 10, normal_a, 11);
print(sax)

#test R
engine = Rengine(['--no-save'], True, None)
engine.startMainLoop()
r_expression = engine.eval("pi")
print(r_expression)

#this works for integer vectors
x = range(-100, 100, 1)
x_wrapped = engine.rniPutIntArray(x);
engine.rniAssign("x_int", x_wrapped, 0);

#something different needed for long vectors
engine.assign("x_long", create_long_vector(engine, np.arange(-100,100,0.1)))

#render a bell curve with R
engine.eval("jpeg(\"normal.jpg\")")
engine.eval("y <- dnorm(x_long, mean=0, sd=25)")
engine.eval("plot(x_long, y)")
engine.eval("dev.off()")

#needed to terminate R thread I guess
jpype.java.lang.System.exit(0)
