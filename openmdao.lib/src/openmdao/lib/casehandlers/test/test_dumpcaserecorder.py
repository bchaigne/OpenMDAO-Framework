"""
Test for CaseRecorders.
"""

import unittest
import StringIO

from openmdao.main.api import Assembly, Case, set_as_top
from openmdao.test.execcomp import ExecComp
from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.drivers.sensitivity import SensitivityDriver
from openmdao.lib.drivers.simplecid import SimpleCaseIterDriver


class DumpCaseRecorderTestCase(unittest.TestCase):

    def setUp(self):
        self.top = top = set_as_top(Assembly())
        driver = top.add('driver', SimpleCaseIterDriver())
        top.add('comp1', ExecComp(exprs=['z=x+y']))
        top.add('comp2', ExecComp(exprs=['z=x+1']))
        top.connect('comp1.z', 'comp2.x')
        driver.workflow.add(['comp1', 'comp2'])

        # now create some Cases
        outputs = ['comp1.z', 'comp2.z']
        cases = []
        for i in range(10):
            i = float(i)
            inputs = [('comp1.x', i), ('comp1.y', i*2)]
            cases.append(Case(inputs=inputs, outputs=outputs))

        Case.set_vartree_inputs(driver, cases)
        driver.add_responses(outputs)

    def test_bad_recorder(self):
        try:
            self.top.recorders = DumpCaseRecorder()
        except Exception as err:
            self.assertTrue(str(err).startswith("The 'recorders' trait of an Assembly"))
            self.assertTrue(str(err).endswith(" was specified."))
        else:
            self.fail("Exception expected")

    def test_dumprecorder(self):
        sout1 = StringIO.StringIO()
        sout2 = StringIO.StringIO()
        self.top.recorders = [DumpCaseRecorder(sout1), DumpCaseRecorder(sout2)]
        self.top.run()

        expected_constants = """\
Constants:
   comp1.directory:
   comp1.force_fd: False
   comp1.missing_deriv_policy: error
   comp2.directory:
   comp2.force_fd: False
   comp2.missing_deriv_policy: error
   directory:
   driver.case_inputs.comp1.x: [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
   driver.case_inputs.comp1.y: [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
   driver.directory:
   driver.force_fd: False
   driver.gradient_options.atol: 1e-09
   driver.gradient_options.derivative_direction: auto
   driver.gradient_options.directional_fd: False
   driver.gradient_options.fd_blocks: []
   driver.gradient_options.fd_form: forward
   driver.gradient_options.fd_step: 1e-06
   driver.gradient_options.fd_step_type: absolute
   driver.gradient_options.force_fd: False
   driver.gradient_options.lin_solver: scipy_gmres
   driver.gradient_options.maxiter: 100
   driver.gradient_options.rtol: 1e-09
   force_fd: False
   missing_deriv_policy: assume_zero"""

        expected_case = """\
Case:
   uuid: ad4c1b76-64fb-11e0-95a8-001e8cf75fe
   timestamp: 1383239074.309192
   inputs:
      comp1.x: 8.0
      comp1.y: 16.0
   outputs:
      Response(comp1.z): 24.0
      Response(comp2.z): 25.0
      comp1.derivative_exec_count: 0
      comp1.exec_count: 9
      comp1.itername: 9-comp1
      comp1.z: 24.0
      comp2.derivative_exec_count: 0
      comp2.exec_count: 9
      comp2.itername: 9-comp2
      comp2.z: 25.0
      driver.workflow.itername: 9"""

        # print sout1.getvalue()
        expected = expected_constants.split('\n')
        for sout in [sout1, sout2]:
            lines = sout.getvalue().split('\n')
            lines = [line.rstrip() for line in lines]
            for i in range(len(expected)):
                self.assertEqual(lines[i].rstrip(), expected[i])

        expected = expected_case.split('\n')
        for sout in [sout1, sout2]:
            lines = sout.getvalue().split('\n')
            lines = [line.rstrip() for line in lines]
            start = 0
            for i in range(9):
                index = start + lines[start:].index('Case:')
                start = index + 1
            for i in range(len(expected)):
                if expected[i].startswith('   uuid:'):
                    self.assertTrue(lines[index+i].startswith('   uuid:'))
                elif expected[i].startswith('   timestamp:'):
                    self.assertTrue(lines[index+i].startswith('   timestamp:'))
                else:
                    self.assertEqual(lines[index+i], expected[i])

    def test_multiple_objectives(self):
        sout = StringIO.StringIO()
        self.top.add('driver', SensitivityDriver())
        self.top.driver.workflow.add(['comp1', 'comp2'])
        self.top.driver.add_parameter(['comp1.x'], low=-100, high=100)
        self.top.driver.add_objective('comp1.z')
        self.top.driver.add_objective('comp2.z')

        self.top.recorders = [DumpCaseRecorder(sout)]
        self.top.run()

        expected = """\
Constants:
   comp1.directory:
   comp1.force_fd: False
   comp1.missing_deriv_policy: error
   comp1.y: 0.0
   comp2.directory:
   comp2.force_fd: False
   comp2.missing_deriv_policy: error
   directory:
   driver.directory:
   driver.force_fd: False
   driver.gradient_options.atol: 1e-09
   driver.gradient_options.derivative_direction: auto
   driver.gradient_options.directional_fd: False
   driver.gradient_options.fd_blocks: []
   driver.gradient_options.fd_form: forward
   driver.gradient_options.fd_step: 1e-06
   driver.gradient_options.fd_step_type: absolute
   driver.gradient_options.force_fd: False
   driver.gradient_options.lin_solver: scipy_gmres
   driver.gradient_options.maxiter: 100
   driver.gradient_options.rtol: 1e-09
   force_fd: False
   missing_deriv_policy: assume_zero
   recording_options.excludes: []
   recording_options.includes: ['*']
   recording_options.save_problem_formulation: True
Case:
   uuid: 766f9b47-5bc0-11e4-803d-080027a1f086
   timestamp: 1414184290.686166
   inputs:
      comp1.x: 0.0
   outputs:
      Objective(comp1.z): 0.0
      Objective(comp2.z): 1.0
      comp1.derivative_exec_count: 0
      comp1.exec_count: 1
      comp1.itername: 1-comp1
      comp1.z: 0.0
      comp2.derivative_exec_count: 0
      comp2.exec_count: 1
      comp2.itername: 1-comp2
      comp2.z: 1.0
      driver.workflow.itername: 1
"""

        # print sout.getvalue()
        expected = expected.split('\n')
        lines = sout.getvalue().split('\n')
        lines = [line.rstrip() for line in lines]
        for i in range(len(expected)):
            if expected[i].startswith('   uuid:'):
                self.assertTrue(lines[i].startswith('   uuid:'))
            elif expected[i].startswith('   timestamp:'):
                self.assertTrue(lines[i].startswith('   timestamp:'))
            else:
                self.assertEqual(lines[i].rstrip(), expected[i])

    def test_close(self):
        sout1 = StringIO.StringIO()
        self.top.recorders = [DumpCaseRecorder(sout1)]
        self.top.recorders[0].close()
        self.top.run()
        self.assertEqual(sout1.getvalue(), '')


if __name__ == '__main__':
    unittest.main()

