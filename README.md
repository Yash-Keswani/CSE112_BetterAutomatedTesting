This is a remake of IIIT-D's testing suite for CSE112 / CO. it's platform agnostic (will work on both windows and linux) and IDE agnostic (you can run it with pycharm / vscode testing tools and it'll work). 

it will detect in-code errors (such as ValueErrors or infinite loops) as well.

changing the run script works as usual. 

image generator is currently WIP. copy images with names `test01.png`, `test04.png` etc. Accept `--generate test09`, etc. in your simulator code and save it as `AutomatedTesting/images/test09_gnrtd.png` for desired behaviour.

use `./run` in `AutomatedTesting` to run it in grading mode.

use `python3 -m unittest discover -f better_tester.py` in AutomatedTesting to run it in debugging mode, which will show assert results.

mail me at yash20158@iiitd.ac.in to report any bugs / suggestions, or use the issues tab here.
