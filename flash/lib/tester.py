""" history
    2021-04-03 DCN: created
    """
""" description
    Crude unit test system
    """

def run(context,test_specs,*,stop_on_fail=False):
    """ run all the tests in test_specs (via _expect)
        test_specs is an arry of lists, each list represents a test
        each list consists of:
         item[0] = test name, the full name is constructed as context:test name
         item[1] = expected result
         item[2] = the function to call
         item[3..4] = positional paramters (a list) and/or keyword parameters (a dict)
        at the end of the tests the number executed, passed and failed are printed
        returns the count of failed tests
        if stop_on_fail is asserted all tests are run, otherwise tests stop as soon as one fails
        """
    tests  = 0
    passes = 0
    for test in test_specs:
        tests  += 1
        name    = '{}:{}'.format(context,test[0])
        expect  = test[1]
        func    = test[2]
        args    = ()
        kwargs  = {}
        if len(test) > 3 and type(test[3]) == type(()):
            # got positional arguments in [3]
            args = test[3]
        if len(test) > 3 and type(test[3]) == type({}):
            # got keyword arguments in [3]
            kwargs = test[3]
        if len(test) > 4 and type(test[4]) == type(()):
            # got positional arguments in [4]
            args = test[4]
        if len(test) > 4 and type(test[4]) == type({}):
            # got keyword arguments in [4]
            kwargs = test[4]
        passed  = _expect(name,tests,expect,func,*args,**kwargs)
        passes += passed
        if stop_on_fail and not passed:
            break
    print('{}: {} tests run, {} passed, {} failed, {} skipped'.format(context,tests,passes,tests-passes,len(test_specs)-tests))
    return tests-passes
    
def _expect(testname,testnum,shouldbe,func,*args,**kwargs):
    """ execute a function and verify its result is that expected
        if the test succeeds there is silence and 1 is returned
        if its fails (i.e. does not return the expected result), or throws an exception, the result is printed and 0 is returned
        """
    try:
        result = func(*args,**kwargs)
        if result != shouldbe:
            print('{}: test#{}: failed - expected {}, got {}'.format(testname,testnum,shouldbe,result))
            return 0
    except Exception as e:
        import sys
        print('{}: test#{}: failed - threw exception {}({})'.format(testname,testnum,sys.exc_info()[0].__name__,sys.exc_info()[1]))
        return 0
    return 1
