__unittest=True  # comment this line for full traceback

from collections import defaultdict
import enum
import os
import subprocess
import unittest

HARD_SCORE = 20
SIMPLE_SCORE = 5
MAX_DIFF_SIZE = 500

EFFECTS = {'CYAN' : '\033[96m', 'GREEN' : '\033[92m', 'YELLOW' : '\033[93m',
'RED' : '\033[91m', 'BOLD' : '\033[1m', 'UNDERLINE'	 : '\033[4m', 'MAGENTA'	:	'\033[35m'}

EFFECTS_CLOSE = '\033[0m'
MANUAL_GRADED = ['error', 'image']
	
def aprint(text, *args, **kwargs):
	applied_effs = [EFFECTS[x] for x in args if x in EFFECTS]
	print(''.join(applied_effs) + text + EFFECTS_CLOSE, **kwargs)

here = os.path.dirname(os.path.realpath(__file__))
asm_tests_hard_dir = here + "/tests/assembly/hardBin"
bin_tests_hard_dir = here + "/tests/bin/hard"
fin_tests_hard_dir = here + "/tests/traces/hard"

asm_tests_dir = here + "/tests/assembly/simpleBin"
bin_tests_dir = here + "/tests/bin/simple"
fin_tests_dir = here + "/tests/traces/simple"
img_tests_dir = here + "/tests/images"

err_tests_dir = here + "/tests/assembly/errorGen"

ASM = here + "/../SimpleAssembler"
SIM = here + "/../SimpleSimulator"

asms_hard = os.listdir(asm_tests_hard_dir)
bins_hard = os.listdir(bin_tests_hard_dir)
fins_hard = os.listdir(fin_tests_hard_dir)

asms = os.listdir(asm_tests_dir)
bins = os.listdir(bin_tests_dir)
fins = os.listdir(fin_tests_dir)
errs = os.listdir(err_tests_dir)
imgs = os.listdir(img_tests_dir)

class AsmTest(unittest.TestCase):
	maxDiff = MAX_DIFF_SIZE
	def factory(self, cwd, control_out_dir, experimental_in_dir):
		control_out_files = os.listdir(control_out_dir)
		experimental_in_files = os.listdir(experimental_in_dir)
		os.chdir(cwd)
		for b, a in zip(control_out_files, experimental_in_files):
			with self.subTest(msg=a):
				with open(experimental_in_dir + "/" + a) as fl:
					experimental_in = fl.read()
				
				with open("run") as run_script_file:
					run_script = run_script_file.read().split(' ')

				experimental = subprocess.check_output(run_script, input=experimental_in, text=True, timeout=5)
				
				with open(control_out_dir + "/" + b) as fl:
					control = fl.read()
					self.assertEqual(control, experimental)

	def testErrors(self):
		os.chdir(ASM)
		aprint("Running Errors", 'BOLD', 'CYAN', end = '')
		for case in errs:
			with self.subTest(msg=case):
				with open(err_tests_dir + "/" + case) as fl:
					experimental_in = fl.read()
				
				with open("run") as run_script_file:
					run_script = run_script_file.read().split(' ')

				aprint(f"\n{case}", 'UNDERLINE')
				print(subprocess.check_output(run_script, input=experimental_in, text=True, timeout=5), end='')

	def testAssemblerHard(self):
		self.factory(ASM, asm_tests_hard_dir, bin_tests_hard_dir)

	def testAssembler(self):
		self.factory(ASM, asm_tests_dir, bin_tests_dir)
	
	def testSimulatorHard(self):
		self.factory(ASM, bin_tests_hard_dir, fin_tests_hard_dir)

	def testSimulator(self):
		self.factory(ASM, bin_tests_dir, fin_tests_dir)

	def testImages(self):
		os.chdir(SIM)
		if len(imgs) == 1 and imgs[0] == 'gnrtd.png':  # null case
			return 
		aprint("\nGenerating Images", 'BOLD', 'CYAN')
		for casefile in imgs:
			case = casefile.rstrip('.png')
			if case.endswith("gnrtd"):
				continue
			with self.subTest(msg=case):
				with open(bin_tests_hard_dir + "/" + case) as fl:
					experimental_in = fl.read()
				
				with open("run") as run_script_file:
					run_script = run_script_file.read().split(' ')
					run_script.extend(['--generate', {case}])

				aprint(f"{case}", 'UNDERLINE')
				subprocess.run(run_script, input=experimental_in, text=True, timeout=5)

class Graded_TextTestResult(unittest.TextTestResult):
	class TestStatus(enum.Enum):
		FAILURE = 0
		SUCCESS = 1
		CRASHED = -1
	def __init__(self, stream, descriptions, verbosity):
		super().__init__(stream, descriptions, verbosity)
		self.stats = defaultdict(lambda: {"failures": 0, "successes": 0, "total": 0})
		self.testResults = defaultdict(list)

	def addSubTest(self, test, subtest, err):
		super().addSubTest(test, subtest, err)
		self.stats[test._testMethodName]["total"] += 1
		if err is None:
			self.testResults[test._testMethodName].append({"name": subtest._message, "status": self.TestStatus.SUCCESS, "error": err})
			self.stats[test._testMethodName]["successes"] += 1
		elif err[0] == AssertionError:
			self.testResults[test._testMethodName].append({"name": subtest._message, "status": self.TestStatus.FAILURE, "error": err})
			self.stats[test._testMethodName]["failures"] += 1
		else:
			self.testResults[test._testMethodName].append({"name": subtest._message, "status": self.TestStatus.CRASHED, "error": err})
			self.stats[test._testMethodName]["failures"] += 1

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(AsmTest)
	with open(os.devnull, 'w') as nullstream:
		runner = unittest.TextTestRunner(resultclass= Graded_TextTestResult, verbosity=0, stream=nullstream)
		result = runner.run(suite)
	
	for testname, rslt in result.testResults.items():
		if any(x in testname.lower() for x in MANUAL_GRADED):
			continue
		aprint(f"\nRunning {testname.lstrip('test')}", 'CYAN', 'BOLD')
		for subtest in rslt:
			if subtest["status"] == Graded_TextTestResult.TestStatus.FAILURE:
				aprint("[FAIL]", 'RED', end=' ')
			elif subtest["status"] == Graded_TextTestResult.TestStatus.CRASHED:
				aprint("[CRSH]", 'YELLOW', end=' ')
			elif subtest["status"] == Graded_TextTestResult.TestStatus.SUCCESS:
				aprint("[PASS]", 'GREEN', end=' ')
			else:
				raise ValueError("Invalid Status")
		
			print(subtest['name'])
				
	aprint("\n\n============", 'CYAN')
	aprint("TOTAL SCORES", 'MAGENTA', 'BOLD')
	aprint("============", 'CYAN')
	for testname, testresults in result.stats.items():
		if any(x in testname.lower() for x in MANUAL_GRADED):
			continue
		if 'hard' in testname.lower():
			SCORE = HARD_SCORE
		else:
			SCORE = SIMPLE_SCORE
		aprint(testname.lstrip('test'), 'BOLD', end = '')
		print(f" - {testresults['successes']*SCORE}/{testresults['total']*SCORE}")