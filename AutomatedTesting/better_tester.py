__unittest = True

from collections import defaultdict
from dataclasses import dataclass
import enum
import itertools
import os
import subprocess
from typing import TextIO
import unittest

class AsmTest(unittest.TestCase):
	def setUp(self) -> None:
		here = os.path.dirname(os.path.realpath(__file__))
		self.asm_tests_dir = here + "/tests/assembly/hardBin"
		self.bin_tests_dir = here + "/tests/bin/hard"
		self.fin_tests_dir = here + "/tests/traces/hard"

		self.ASM = here + "/../SimpleAssembler"
		self.SIM = here + "/../SimpleSimulator"

		self.asms = list(os.walk(self.asm_tests_dir))[0][2]
		self.bins = list(os.walk(self.bin_tests_dir))[0][2]
		self.fins = list(os.walk(self.fin_tests_dir))[0][2]

		self.maxDiff = 400
	
	def testAssembler(self):
		os.chdir(self.ASM)
		for a, b in zip(self.asms, self.bins):
			with self.subTest(msg=a):
				with open(self.asm_tests_dir + "/" + a) as fl:
					asm = fl.read()
				
				with open("run") as asm_run_script_file:
					asm_run_script = asm_run_script_file.read().split(' ')

				asm_out = subprocess.run(asm_run_script, input=asm, text=True, capture_output=True).stdout 
				
				with open(self.bin_tests_dir + "/" + b) as fl:
					byt = fl.read()
					self.assertEqual(asm_out.strip(), byt.strip())
	
	def testExecutor(self):
		os.chdir(self.SIM)
		for b, f in zip(self.bins, self.fins):
			with self.subTest(msg=b):
				with open(self.bin_tests_dir + "/" + b) as fl:
					byt = fl.read()

				with open("run") as sim_run_script_file:
					sim_run_script = sim_run_script_file.read().split(' ')

				byt_out = subprocess.run(sim_run_script, input=byt, encoding='utf-8', capture_output=True).stdout
				
				with open(self.fin_tests_dir + "/" + f) as fl:
					fin = fl.read()
					# self.assertEqual(byt_out.strip(), fin.strip())

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
		else:
			self.testResults[test._testMethodName].append({"name": subtest._message, "status": self.TestStatus.FAILURE, "error": err})
			self.stats[test._testMethodName]["failures"] += 1

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(AsmTest)
	with open(os.devnull, 'w') as nullstream:
		runner = unittest.TextTestRunner(resultclass= Graded_TextTestResult, verbosity=0, stream=nullstream)
		result = runner.run(suite)
	
	for testname, rslt in result.testResults.items():
		print(f"Running {testname}")
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
				
	print(dict(result.stats))