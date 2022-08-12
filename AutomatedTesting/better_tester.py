__unittest=True  # comment this line for full traceback

from collections import defaultdict
import enum
import os
from socket import timeout
import subprocess
from typing import TextIO
import unittest

HARD_SCORE = 20
SIMPLE_SCORE = 5

here = os.path.dirname(os.path.realpath(__file__))
asm_tests_hard_dir = here + "/tests/assembly/hardBin"
bin_tests_hard_dir = here + "/tests/bin/hard"
fin_tests_hard_dir = here + "/tests/traces/hard"
asm_tests_dir = here + "/tests/assembly/simpleBin"
bin_tests_dir = here + "/tests/bin/simple"
fin_tests_dir = here + "/tests/traces/simple"

ASM = here + "/../SimpleAssembler"
SIM = here + "/../SimpleSimulator"

asms_hard = os.listdir(asm_tests_hard_dir)
bins_hard = os.listdir(bin_tests_hard_dir)
fins_hard = os.listdir(fin_tests_hard_dir)

asms = os.listdir(asm_tests_dir)
bins = os.listdir(bin_tests_dir)
fins = os.listdir(fin_tests_dir)

class AsmTest(unittest.TestCase):
	maxDiff = 400
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

	def testAssemblerHard(self):
		self.factory(ASM, asm_tests_hard_dir, bin_tests_hard_dir)

	def testAssembler(self):
		self.factory(ASM, asm_tests_dir, bin_tests_dir)
	
	def testSimulatorHard(self):
		self.factory(ASM, bin_tests_hard_dir, fin_tests_hard_dir)

	def testSimulator(self):
		self.factory(ASM, bin_tests_dir, fin_tests_dir)

class Graded_TextTestResult(unittest.TextTestResult):
	class TestStatus(enum.Enum):
		FAILURE = 0
		SUCCESS = 1
		CRASHED = -1
	def __init__(self, stream: TextIO, descriptions: bool, verbosity: int) -> None:
		super().__init__(stream, descriptions, verbosity)
		self.stats = defaultdict(lambda: {"failures": 0, "successes": 0, "total": 0})
		self.testResults = defaultdict(list)

	def addSubTest(self, test: unittest.case.TestCase, subtest: unittest.case.TestCase, err) -> None:
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
	"""
	here = os.path.dirname(os.path.realpath(__file__))
	asm_tests_dir = here + "/tests/assembly/hardBin"
	bin_tests_dir = here + "/tests/bin/hard"
	fin_tests_dir = here + "/tests/traces/hard"

	ASM = here + "/../SimpleAssembler"
	SIM = here + "/../SimpleSimulator"
	suite = unittest.TestSuite()
	suite.addTest(AsmTest.factory(ASM, asm_tests_dir, bin_tests_dir))
	"""
	with open(os.devnull, 'w') as nullstream:
		runner = unittest.TextTestRunner(resultclass= Graded_TextTestResult, verbosity=0, stream=nullstream)
		result = runner.run(suite)
	
	for testname, rslt in result.testResults.items():
		print(f"\nRunning {testname.lstrip('test')}")
		for subtest in rslt:
			if subtest["status"] == Graded_TextTestResult.TestStatus.FAILURE:
				pretext = "[FAIL]"
			elif subtest["status"] == Graded_TextTestResult.TestStatus.CRASHED:
				pretext = "[CRASHED]"
			elif subtest["status"] == Graded_TextTestResult.TestStatus.SUCCESS:
				pretext = "[PASS]"
			else:
				raise ValueError("Invalid Status")
		
			print(f"{pretext} {subtest['name']}")
				
	print("\n\n==============")
	print("TOTAL SCORES")
	print("==============")
	for testname, testresults in result.stats.items():
		if 'hard' in testname.lower():
			SCORE = HARD_SCORE
		else:
			SCORE = SIMPLE_SCORE
		print(f"{testname.lstrip('test')} - {testresults['successes']*SCORE}/{testresults['total']*SCORE}")