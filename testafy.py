# This is the Python API wrapper for Testafy.
# See testafy.com for more info.
# Copyright 2012 Grant Street Group

import requests
import json
import time
import base64
import os
import errno

class Test:

    def __init__(self, login_name, password, 
            base_uri='https://app.testafy.com/api/v0/',  
            args=None,
        ):
        if args is None: args = {}

        self.base_uri = base_uri
        default_test = "For the site http://www.google.com\nThen pass this test"

        args.setdefault('pbehave',default_test)
        args.setdefault('trt_id', None)

        self.login_name = login_name
        self.password = password

        self.args = args
        self._results = None
        self._err = None
        self._msg = None

    @classmethod
    def try_it_now(self):
        t = self("try_it_now","")
        t.pbehave = """
            # Remember, try_it_now tests can only be 3 steps long
            # and automatically have a 2 second delay between steps.
            For the url http://testafy.com
            When the "About Us" link is clicked
            Then the text "Community. Efficiency. Innovation. Reliability." is present
        """
        return t

    # An internal method to make an API call.
    def make_request(self, api_command, args):
        
        response = requests.post(
                url=self.base_uri + api_command, 
                data = {'json' : json.dumps(args)}, 

                #verify=False,
                auth=(self.login_name, self.password),
            )

        r_json = response.content
        r = json.loads(r_json)

        # get() assigns the second value to the key if it doesn't exist already
        self._err = r.get('error', None)
        if self._err is not None:
            raise ValueError(self._err)
            
        self._msg = r.get('message', None)

        return r

    # Returns the trt_id of the test being run,
    # which uniquely identifies it on the server (and can be used in other API
    # calls to get more information about it)

    def run(self):

        path = "test/run"
        if self.login_name == "try_it_now":
            path = "try_it_now/run" 
        r = self.make_request(path, self.args)

        self.args['trt_id'] = r.get('test_run_test_id', None)
        return self.args['trt_id']

    def run_and_wait(self):
        trt_id = self.run()
        while not self.is_done():
            time.sleep(5)
        return trt_id

    # Returns the status of the test as a string.
    # One of "queued", "running", "stopped", or "completed".
    def status(self):
        if self.login_name is None:
            return None
        if self.args['trt_id'] is None:
            return "unscheduled"

        path = "test/status"
        if self.login_name == "try_it_now": 
            path = "try_it_now/status" 
        r = self.make_request(path,
                {
                    'trt_id' : self.args['trt_id'],
                },
           )

        return r.get('status', None)

    # Get whether or not the test is done running
    def is_done(self):
        s = self.status()
        if s is None:
            return False
        return s != "unscheduled" and s != "queued" and s != "running"

    # Get the number of "then" statements that have passed so far
    # in this test run.
    def passed(self):
        if self.args['trt_id'] is None:
            return 0

        path = "test/stats/passed"
        if self.login_name == "try_it_now":
            path = "try_it_now/stats/passed" 
        r = self.make_request(path, 
                {
                    "trt_id" : self.args['trt_id'],
                }, 
            )
        return r.get('passed', None)

    # Get the number of "then" statements that have failed so far
    # in this test run.
    def failed(self):
        if self.args['trt_id'] is None:
            return 0
        path = "test/stats/failed"
        if self.login_name == "try_it_now":
            path = "try_it_now/stats/failed" 
        r = self.make_request(path, 
                {
                    "trt_id" : self.args['trt_id'],
                }, 
            )
        return r.get('failed', None)

    # Get the number of planned "then" statements for this test
    def planned(self):
        if self.args['trt_id'] is None:
            return 0

        path = "test/stats/planned"
        if self.login_name == "try_it_now": 
            path = "try_it_now/stats/planned" 
        r = self.make_request(path,
                {
                    "trt_id" : self.args['trt_id'],
                },
            )

        return r.get('planned', None)

    # Get the results of the test as an array of 2-element arrays, where the
    # inner arrays consist of:
    #   [ "a string describing the type of line", "a line in TAP format" ]
    #
    # Note that results_string concatenates the second elements of the inner
    # arrays, yielding the full results in TAP format.
    def results(self):
        if self.args['trt_id'] is None:
            return None
        if self._results != None:
            return self._results

        path = "test/results"
        if self.login_name == "try_it_now":
            path = "try_it_now/results" 
        r = self.make_request(path,
                {
                    "trt_id" : self.args["trt_id"],
                },
            )

        self._results = r.get('results', None)
        return self._results

    # Get the results of the test as a string in TAP format
    def results_string(self):
        r = self.results()
        if r is None:
            return None
        def second(x):
            return x[1]
        lines = map(second, r)
        return "\n".join(lines)

    # Get a string describing the validity of the phrases in the current test's 
    # PBehave code, and detailing any problems found.
    def phrase_check(self):
        r = self.make_request("phrase_check",
                {
                    "trt_id" : self.args['trt_id'],
                    "pbehave" : self.args['pbehave'],
                },
            )
        return r.get('message', None)

    # Get a list containing the names of all the saved screenshots for this test
    def screenshots(self):
        if self.args['trt_id'] is None:
            return None
        path = "test/screenshots"
        if self.login_name == "try_it_now":
            path = "try_it_now/screenshots" 
        r = self.make_request(path, 
                {
                    "trt_id" : self.args['trt_id'],
                },
            )
        return r.get('screenshots', None)

    # Get a screenshot, by name, as a base64-encoded string
    def screenshot_as_base64(self, screenshot_name):
        if self.args['trt_id'] is None:
            return None
        path = "test/screenshot"
        if self.login_name == "try_it_now":
            path = "try_it_now/screenshot" 
        r = self.make_request(path,
                {
                    "trt_id" : self.args['trt_id'],
                    "filename" : screenshot_name,
                }
            )
        return r.get('screenshot', None)

    # Get a dict containing:
    #   screenshot names as keys
    #   base64-encoded screenshots as values
    def all_screenshots_as_base64(self):
        if self.args['trt_id'] is None:
            return None
        
        all_screenshots = {}
        for screenshot_name in self.screenshots():
            all_screenshots[screenshot_name] = self.screenshot_as_base64(screenshot_name)
        return all_screenshots

    # Write a screenshot to a file.
    def save_screenshot(self, screenshot_name, local_filename):
        if self.args['trt_id'] is None:
            return None
        ss = base64.b64decode(self.screenshot_as_base64(screenshot_name))
        with open(local_filename, "w") as f:
            f.write(ss)
    
    # Write all screenshots to the given directory (using their names on the Testafy server)
    def save_all_screenshots(self, local_dir):
        if self.args['trt_id'] is None:
            return None

        try:
            os.makedirs(local_dir)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise

        for ss in self.screenshots():
            self.save_screenshot(ss, local_dir + "/" + ss)

    # Get the last received error message
    def error(self):
        return self._err

    # Get the last received message
    def message(self):
        return self._msg
