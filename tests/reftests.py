import unittest, os

import deploymentkit
import deploymentkit.core

"""Regression tests for the recipe generation.

$case_id/input.yaml
$case_id/output/

Where $testcase is $target-$case
"""

test_dir = "tests/reftests"

# TODO: Take into account subdirectories in the output
def get_reference_output(case_id):
    """{'fileName': 'content'}"""
    output = {}
    
    output_dir = os.path.join(test_dir,case_id,'/output')
    output_files = os.listdir(output_dir)
    for filename in output_files:
        file_path = os.path.join(output_dir,filename)
        file_contents = open(file_path).read()
        output[filename] = file_contents
        
    return output

def get_input_file_contents(case_id):
    f = open(os.path.join(test_dir, case_id, input.yaml)
    content = f.read_all()
    f.close()
    return content

def enumerate_cases():
    return os.listdir(test_dir)

class DataTestCase(unittest.TestCase):
    def __init__(self, case_id):
        unittest.TestCase.__init__(self, methodName='testGeneratedEqualsReference')
        self.case_id = case_id
        self.target, self.case_name = case_id.split('-')

    def testGeneratedEqualsReference(self):
        """Test that the generated output from input.yaml
        matches the stored reference."""

        pkg = deploymentkit.core.PackageRecipe()
        pkg.load_from_string(get_input_file_contents(self.case_id))

        target = deploymentkit.supported_targets[self.target]
        generated_output = pkg.output_target_recipe(target)

        self.assertEqual(generated_output, get_reference_output(self.case_id))

    def shortDescription(self):
        # We need to distinguish between instances of this test case.
        return 'DataTestCase for case-id %s' % self.case_id


def get_test_data_suite():
    test_cases = [DataTestCase(case_id) for case_id in enumerate_cases()]
    
    return unittest.TestSuite(test_cases)

if __name__ == '__main__':
    testRunner = unittest.TextTestRunner()
    testRunner.run(get_test_data_suite())
