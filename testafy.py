import requests
import json
import time

class Test:
    def __init__(self, login_name, password, 
            base_uri='https://app.testafy.com/api/v0/',  
            args=None,
        ):
        if args is None: args = {}

        self.base_uri = base_uri
        default_test = "For the site http://www.google.com\nThen pass this test"

        args.setdefault('pbehave',default_test)
        args.setdefault('asynchronous', True)
        args.setdefault('trt_id', None)

        self.login_name = login_name
        self.password = password

        self.args = args
        self._results = None
        self._err = None
        self._msg = None

    def make_request(self, api_command, args):
        
        response = requests.post(
                url=self.base_uri + api_command, 
                data = {'json' : json.dumps(self.args)}, 
                verify=False,
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
    def run(self, async=0):
        r = self.make_request("test/run", self.args)

        self.args['trt_id'] = r.get('test_run_test_id', None)

        if async==0:
            while not self.is_done():
                time.sleep(1)

        return self.args['trt_id']

    # Returns the status of the test as a string.
    # One of "queued", "running", "stopped", or "completed".
    def status(self):
        if self.login_name is None:
            return None
        if self.args['trt_id'] is None:
            return "unscheduled"
        r = self.make_request( "test/status", 
                {
                    'trt_id' : self.args['trt_id'],
                },
           )

        return r.get('status', None)

    def is_done(self):
        s = self.status()
        if s is None:
            return False
        return s != "queued" and s != "running"

    def passed(self):
        if self.args['trt_id'] is None:
            return 0
        r = self.make_request("test/stats/passed", 
                {
                    "trt_id" : self.args['trt_id'],
                }, 
            )
        return r.get('passed', None)

    def failed(self):
        if self.args['trt_id'] is None:
            return 0
        r = self.make_request("test/stats/failed", 
                {
                    "trt_id" : self.args['trt_id'],
                }, 
            )
        return r.get('failed', None)

    def planned(self):
        if self.args['trt_id'] is None:
            return 0
        r = self.make_request("test/stats/planned",
                {
                    "trt_id" : self.args['trt_id'],
                },
            )

        return r.get('planned', None)

    def results(self):
        if self.args['trt_id'] is None:
            return None
        if self._results != None:
            return self._results

        r = self.make_request("test/results",
                {
                    "trt_id" : self.args["trt_id"],
                },
            )

        self._results = r.get('results', None)
        return self._results

    def results_string(self):
        r = self.results()
        if r is None:
            return None
        def second(x):
            return x[1]
        lines = map(second, r)
        return "\n".join(lines)

    def phrase_check(self):
        if self.args['trt_id'] is None:
            return None
        r = self.make_request("phrase_check",
                {
                    "trt_id" : self.args['trt_id'],
                },
            )
        return r.get('message', None)

    def error(self):
        return self._err

    def message(self):
        return self._msg
