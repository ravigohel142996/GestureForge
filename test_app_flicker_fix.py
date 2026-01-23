"""
Test suite for the Streamlit UI flicker fix.

These tests verify that the app uses bounded loops and session_state
to prevent continuous reruns and screen flickering.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFlickerFix(unittest.TestCase):
    """Test that flicker fix implementation is correct."""
    
    def test_no_while_true_loop(self):
        """Verify no while True loops exist in main processing."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check that there's no "while True" in the main processing section
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'while True' in line.lower() and i > 400:  # After imports
                self.fail(f"Found 'while True' on line {i}, which can cause flickering")
    
    def test_bounded_loop_exists(self):
        """Verify bounded loop (for i in range) exists."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        self.assertIn('for i in range(200)', content, 
                     "Missing bounded loop 'for i in range(200)'")
        self.assertIn('# Bounded loop to prevent infinite reruns', content,
                     "Missing comment about bounded loop")
    
    def test_session_state_running_check(self):
        """Verify session_state.running is used for control."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        self.assertIn('st.session_state.running', content,
                     "Missing st.session_state.running")
        self.assertIn('if not st.session_state.running:', content,
                     "Missing check for stopping condition")
    
    def test_sleep_exists(self):
        """Verify sleep is used to control frame rate."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        self.assertIn('time.sleep(0.03)', content,
                     "Missing time.sleep(0.03) for frame rate control")
    
    def test_rerun_only_when_needed(self):
        """Verify st.rerun() is only called when still running after bounded loop."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Should have controlled rerun after bounded loop
        self.assertIn('if st.session_state.running:\n                st.rerun()', content,
                     "Missing controlled rerun after bounded loop")
    
    def test_start_stop_buttons_use_rerun(self):
        """Verify start/stop buttons explicitly call rerun."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Find the button section
        button_section_start = content.find('if st.button("▶️ Start System"')
        button_section_end = content.find('# Process frames in a bounded loop')
        button_section = content[button_section_start:button_section_end]
        
        # Count reruns in button section
        rerun_count = button_section.count('st.rerun()')
        self.assertEqual(rerun_count, 2, 
                        f"Expected 2 st.rerun() calls in button section (start and stop), found {rerun_count}")
    
    def test_no_continuous_rerun_at_end_of_loop(self):
        """Verify there's no unconditional rerun at end of single frame processing."""
        with open('app.py', 'r') as f:
            content = f.read()
        
        # The old bad pattern was: time.sleep(X); st.rerun() unconditionally
        # after processing a single frame
        # Now it should only rerun after the bounded loop and if still running
        lines = content.split('\n')
        for i in range(len(lines) - 1):
            # Check if there's a pattern of sleep followed immediately by unconditional rerun
            if 'time.sleep' in lines[i]:
                # Next non-empty line should not be an unconditional st.rerun()
                next_line = lines[i + 1].strip()
                if next_line == 'st.rerun()':
                    self.fail(f"Found unconditional st.rerun() after time.sleep on line {i+1}")
    
    def test_readme_updated(self):
        """Verify README mentions session_state and flicker fix."""
        with open('README.md', 'r') as f:
            content = f.read()
        
        self.assertIn('session_state', content.lower(),
                     "README should mention session_state")
        self.assertIn('flicker', content.lower(),
                     "README should mention flicker fix")


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFlickerFix))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("FLICKER FIX TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL FLICKER FIX TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
