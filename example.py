import testafy
import time

test = testafy.Test("username","password")
# Run a test synchronously
print "trt_id:" + test.run()

print "passed:" + test.passed()
print "failed:" + test.failed()
print "total:" + test.planned()
print "results:\n" + test.results_string()

# Run a test asynchronously
test = testafy.Test("username","password")
print "trt_id:" + test.run(1)

while not test.is_done():
    print "status: " + test.status()
    time.sleep(1)


print "passed:" + test.passed()
print "failed:" + test.failed()
print "total:" + test.planned()
print "results:\n" + str(test.results_string())
