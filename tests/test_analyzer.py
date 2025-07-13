import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from treeline.cli import cli
from treeline.utils import format_size
from treeline import TreeRenderer, CodeAnalyzer

def test_format_size():
    assert format_size(0) == "0B"
    assert format_size(42) == "42B"
    assert format_size(1024) == "1.0KB"
    assert format_size(1536) == "1.5KB"
    assert format_size(1048576) == "1.0MB"

class TestBasicTree:
    def setup_method(self):
        self.runner = CliRunner()
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir)
    
    def make_test_files(self):
        (self.path / "small.txt").write_text("hello")
        (self.path / "big.txt").write_text("x" * 1024)
        
        subdir = self.path / "stuff"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested content")
    
    def test_shows_files_with_sizes(self):
        self.make_test_files()
        result = self.runner.invoke(cli, [str(self.path)])
        
        assert result.exit_code == 0
        assert "small.txt" in result.output
        assert "(5B)" in result.output
        assert "(1.0KB)" in result.output
    
    def test_hides_sizes_when_asked(self):
        self.make_test_files()
        result = self.runner.invoke(cli, [str(self.path), "--no-size"])
        
        assert "small.txt" in result.output
        assert "(5B)" not in result.output
    
    def test_respects_depth_limit(self):
        self.make_test_files()
        result = self.runner.invoke(cli, [str(self.path), "--depth", "1"])
        
        assert "small.txt" in result.output
        assert "stuff/" in result.output
        assert "nested.txt" not in result.output
    
    def test_works_from_current_dir(self):
        old_dir = os.getcwd()
        try:
            os.chdir(self.path)
            self.make_test_files()
            result = self.runner.invoke(cli, [])
            assert "small.txt" in result.output
        finally:
            os.chdir(old_dir)

def test_handles_bad_paths():
    runner = CliRunner()
    result = runner.invoke(cli, ["/totally/fake/path"])
    assert result.exit_code != 0

def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = CliRunner()
        result = runner.invoke(cli, [tmpdir])
        assert result.exit_code == 0

class TestSkippingFiles:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir)
        self.runner = CliRunner()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir)
    
    def test_skips_common_junk(self):
        (self.path / ".git").mkdir()
        (self.path / "__pycache__").mkdir()
        (self.path / "node_modules").mkdir()
        (self.path / "code.py").write_text("print('hello')")
        
        result = self.runner.invoke(cli, [str(self.path)])
        
        assert "code.py" in result.output
        assert ".git" not in result.output
        assert "__pycache__" not in result.output
        assert "node_modules" not in result.output

class TestCodeAnalysis:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = Path(self.tmpdir)
        self.runner = CliRunner()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir)
    
    def test_python_class_detection(self):
        python_code = '''
class MyClass:
    def method1(self):
        pass
    
    def method2(self, arg):
        return arg

def standalone_function():
    pass
'''
        (self.path / "test.py").write_text(python_code)
        
        result = self.runner.invoke(cli, [str(self.path), "--code"])
        assert "MyClass" in result.output
        assert "method1()" in result.output
    
    def test_javascript_component_detection(self):
        js_code = '''
import React from 'react';

function MyComponent() {
    return <div>Hello</div>;
}

class ClassComponent extends React.Component {
    render() {
        return <div>World</div>;
    }
}

function helperFunction() {
    return "helper";
}
'''
        (self.path / "test.jsx").write_text(js_code)
        
        result = self.runner.invoke(cli, [str(self.path), "--code"])
        assert "MyComponent" in result.output
        assert "ClassComponent" in result.output
        assert "(2 components, 1 function)" in result.output

    def test_file_summary_counts(self):
        python_code = '''class One:
    def method(self):
        pass

class Two:
    pass

def func1():
    pass

def func2():
    pass
    '''
        (self.path / "multi.py").write_text(python_code)
        
        result = self.runner.invoke(cli, [str(self.path), "--code"])
        assert "(2 classes, 2 functions)" in result.output

def test_analyzer_directly():
    analyzer = CodeAnalyzer()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('''
def test_function():
    pass

class TestClass:
    def test_method(self):
        pass
''')
        f.flush()
        
        success = analyzer.analyze_file(Path(f.name))
        assert success
        assert len(analyzer.classes) == 1
        assert analyzer.classes[0]['name'] == 'TestClass'
        assert len(analyzer.functions) == 1
        assert analyzer.functions[0]['name'] == 'test_function'
        
        os.unlink(f.name)

def test_tree_renderer_directly():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "test.txt").write_text("content")
        
        renderer = TreeRenderer(show_size=False)
        renderer.render(tmpdir)
        
        assert renderer.total_files == 1

def test_tree_symbols_appear():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "file1.txt").write_text("test")
        (path / "file2.txt").write_text("test")
        
        runner = CliRunner()
        result = runner.invoke(cli, [tmpdir])
        
        has_tree_chars = "├──" in result.output or "└──" in result.output
        assert has_tree_chars

if __name__ == "__main__":
    pytest.main([__file__, "-v"])