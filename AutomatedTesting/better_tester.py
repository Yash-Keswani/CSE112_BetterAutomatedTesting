__unittest=True  # comment this line for full traceback

from collections import defaultdict
import enum
import os
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
	"""
	@classmethod
	def setUpClass(cls) -> None:
	
	def factory(cwd, control_out_dir, experimental_in_dir):
		def toretfun(self):
			control_out = os.listdir(control_out_dir)
			experimental_in = os.listdir(experimental_in_dir)
			os.chdir(cwd)
			for a, b in zip(control_out, experimental_in):
				with self.subTest(msg=a):
					with open(experimental_in_dir + "/" + a) as fl:
						experimental_in = fl.read()
					
					with open("run") as run_script_file:
						run_script = run_script_file.read().split(' ')

					experimental = subprocess.run(run_script, input=experimental_in, text=True, capture_output=True).stdout 
					
					with open(control_out + "/" + b) as fl:
						control = fl.read()
						self.assertEqual(control.strip(), experimental.strip())
		return toretfun
	"""

	def testAssemblerHard(self):
		os.chdir(ASM)
		for a, b in zip(asms_hard, bins_hard):
			with self.subTest(msg=a):
				with open(asm_tests_hard_dir + "/" + a) as fl:
					asm = fl.read()
				
				with open("run") as asm_run_script_file:
					asm_run_script = asm_run_script_file.read().split(' ')
	
				asm_out = subprocess.check_output(asm_run_script, input=asm, text=True, timeout=5)
				
				with open(bin_tests_hard_dir + "/" + b) as fl:
					byt = fl.read()
					self.assertEqual(asm_out.strip(), byt.strip())

	def testAssembler(self):
		os.chdir(ASM)
		for a, b in zip(asms, bins):
			with self.subTest(msg=a):
				with open(asm_tests_dir + "/" + a) as fl:
					asm = fl.read()
				
				with open("run") as asm_run_script_file:
					asm_run_script = asm_run_script_file.read().split(' ')

				asm_out = subprocess.check_output(asm_run_script, input=asm, text=True, timeout=5)
				
				with open(bin_tests_dir + "/" + b) as fl:
					byt = fl.read()
					self.assertEqual(asm_out.strip(), byt.strip())
	
	def testSimulatorHard(self):
		os.chdir(SIM)
		for b, f in zip(bins_hard, fins_hard):
			with self.subTest(msg=b):
				with open(bin_tests_hard_dir + "/" + b) as fl:
					byt = fl.read()

				with open("run") as sim_run_script_file:
					sim_run_script = sim_run_script_file.read().split(' ')

				byt_out = subprocess.check_output(sim_run_script, input=byt, text=True, timeout=5)
				
				with open(fin_tests_hard_dir + "/" + f) as fl:
					fin = fl.read()
					self.assertEqual(byt_out.strip(), fin.strip())

	def testSimulator(self):
		os.chdir(SIM)
		for b, f in zip(bins, fins):
			with self.subTest(msg=b):
				with open(bin_tests_dir + "/" + b) as fl:
					byt = fl.read()

				with open("run") as sim_run_script_file:
					sim_run_script = sim_run_script_file.read().split(' ')

				byt_out = subprocess.check_output(sim_run_script, input=byt, text=True, timeout=5)
				
				with open(fin_tests_dir + "/" + f) as fl:
					fin = fl.read()
					self.assertEqual(byt_out.strip(), fin.strip())

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
		elif type(err) == AssertionError:
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