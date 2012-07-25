python
======

Testafy's python API wrapper
One dependency:
    requests 
        use 'pip install requests'
        or 'easy_install requests'
        further instruction at:
             http://docs.python-requests.org/en/latest/user/install/#installs

Known issue:
You may have problems verifying the SSL certificate for testafy.com. This is possibly a version issue with Python 2.6.3, or it may be a separate configuration issue.
If you run into this, 
1) please let us know what version of python you are running, and anything else that seems relevant
2) at your own risk, you may turn off SSL verification by uncommenting line 53 of testafy.py, "#verify=False"
