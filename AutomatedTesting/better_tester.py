import os
import subprocess
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
		self.maxDiff = None
	
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
					self.assertEqual(byt_out.strip(), fin.strip())

if __name__ == '__main__':
	unittest.main()