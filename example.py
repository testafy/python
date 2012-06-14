import testafy
import time

test = testafy.Test("username","password")
# Run a test synchronously
print "trt_id:" + test.run()
print "status:" + test.status()
status = test.status()

test = testafy.Test("username","password")
test.run()
while not test.is_done():
    time.sleep(1)

print "passed:" + test.passed()
print "failed:" + test.failed()
print "total:" + test.planned()
print "results:\n" + str(test.results())
