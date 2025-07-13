import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from treeline.cli import cli

class TestCLIOptions:
    def setup_method(self):
        self.runner = CliRunner()
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir)
    
    def make_test_files(self):
        (self.path / "test.py").write_text('''
class MyClass:
    def method(self):
        pass

def my_function():
    pass
''')
        (self.path / "readme.txt").write_text("Hello world")
        (self.path / ".hidden").write_text("secret")
        
        subdir = self.path / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("print('nested')")
    
    def test_depth_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path)])
        assert "nested.py" in result.output
        
        result = self.runner.invoke(cli, [str(self.path), "--depth", "1"])
        assert "subdir/" in result.output
        assert "nested.py" not in result.output
    
    def test_no_size_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path)])
        assert "B)" in result.output
        
        result = self.runner.invoke(cli, [str(self.path), "--no-size"])
        assert "readme.txt" in result.output
        assert "B)" not in result.output
    
    def test_all_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path)])
        assert ".hidden" not in result.output
        
        result = self.runner.invoke(cli, [str(self.path), "--all"])
        assert ".hidden" in result.output
    
    def test_include_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path), "--include", "test.py"])
        print("Include result:", result.output)
        assert "test.py" in result.output
        assert "readme.txt" not in result.output
    
    def test_exclude_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path), "--exclude", "readme.txt"])
        assert "test.py" in result.output
        assert "readme.txt" not in result.output
    
    def test_file_count_option(self):
        """test flag with and without code"""
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path), "--file-count"])
        assert "files" in result.output and "dirs" in result.output
    
    def test_code_option(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [str(self.path)])
        assert "MyClass" not in result.output
        
        result = self.runner.invoke(cli, [str(self.path), "--code"])
        assert "MyClass" in result.output
        assert "my_function" in result.output
        assert "(1 class, 1 function)" in result.output
    
    def test_output_option(self):
        self.make_test_files()
        output_file = self.path / "output.txt"
                
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "test.py" in content
        assert "readme.txt" in content
    
    def test_multiple_includes(self):
        self.make_test_files()
        (self.path / "script.js").write_text("console.log('hi')")
        
        result = self.runner.invoke(cli, [
            str(self.path), 
            "--include", "test.py",
            "--include", "script.js"
        ])
        
        assert "test.py" in result.output
        assert "script.js" in result.output
        assert "readme.txt" not in result.output
    
    def test_combine_options(self):
        self.make_test_files()
        
        result = self.runner.invoke(cli, [
            str(self.path),
            "--code",
            "--no-size", 
            "--depth", "1",
            "--include", "test.py"
        ])
        
        assert "test.py" in result.output
        assert "MyClass" in result.output
        assert "B)" not in result.output
        assert "nested.py" not in result.output
        assert "readme.txt" not in result.output

def test_directory_argument():
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "test.txt").write_text("test")
        
        result = runner.invoke(cli, [tmpdir])
        assert "test.txt" in result.output
        
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = runner.invoke(cli, [])
            assert "test.txt" in result.output
        finally:
            os.chdir(old_cwd)

def test_invalid_directory():
    runner = CliRunner()
    result = runner.invoke(cli, ["/does/not/exist"])
    assert result.exit_code != 0

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "max depth" in result.output
    assert "hide file sizes" in result.output
    assert "show classes and functions" in result.output

if __name__ == "__main__":
    pytest.main([__file__, "-v"])