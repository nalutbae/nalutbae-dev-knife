"""
Tests for performance optimization components.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from devknife.core.performance import (
    ProgressIndicator, ProgressType, StreamingInputHandler, MemoryOptimizer,
    progress_context, create_optimized_input_data
)
from devknife.core.models import InputData, InputSource, Config


class TestProgressIndicator:
    """Test progress indicator functionality."""
    
    def test_spinner_creation(self):
        """Test creating a spinner progress indicator."""
        indicator = ProgressIndicator(ProgressType.SPINNER, "Testing...")
        assert indicator.progress_type == ProgressType.SPINNER
        assert indicator.message == "Testing..."
        assert not indicator.running
    
    def test_percentage_creation(self):
        """Test creating a percentage progress indicator."""
        indicator = ProgressIndicator(ProgressType.PERCENTAGE, "Processing", total=100)
        assert indicator.progress_type == ProgressType.PERCENTAGE
        assert indicator.total == 100
    
    def test_progress_context(self):
        """Test progress context manager."""
        with progress_context(ProgressType.SPINNER, "Test operation") as progress:
            assert progress.running
            progress.update(message="Updated message")
        
        assert not progress.running


class TestStreamingInputHandler:
    """Test streaming input handler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = StreamingInputHandler()
    
    def test_stream_file_lines(self):
        """Test streaming file lines."""
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("line1\nline2\nline3\n")
            temp_path = f.name
        
        try:
            lines = list(self.handler.stream_file_lines(temp_path))
            assert lines == ["line1", "line2", "line3"]
        finally:
            os.unlink(temp_path)
    
    def test_stream_file_chunks(self):
        """Test streaming file chunks."""
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("abcdefghijklmnop")
            temp_path = f.name
        
        try:
            chunks = list(self.handler.stream_file_chunks(temp_path, chunk_size=5))
            assert len(chunks) >= 3  # Should be split into chunks
            assert ''.join(chunks) == "abcdefghijklmnop"
        finally:
            os.unlink(temp_path)
    
    def test_process_large_file(self):
        """Test processing large file with progress."""
        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            for i in range(10):
                f.write(f"line{i}\n")
            temp_path = f.name
        
        try:
            def processor(line):
                return line.upper()
            
            results = list(self.handler.process_large_file(
                temp_path, processor, show_progress=False
            ))
            
            assert len(results) == 10
            assert results[0] == "LINE0"
            assert results[9] == "LINE9"
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        with pytest.raises(FileNotFoundError):
            list(self.handler.stream_file_lines("nonexistent.txt"))


class TestMemoryOptimizer:
    """Test memory optimizer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = MemoryOptimizer(max_memory_mb=1)  # 1MB limit for testing
    
    def test_should_use_streaming(self):
        """Test streaming decision logic."""
        small_size = 1024  # 1KB
        large_size = 1024 * 1024  # 1MB
        
        assert not self.optimizer.should_use_streaming(small_size)
        assert self.optimizer.should_use_streaming(large_size)
    
    def test_optimize_csv_processing(self):
        """Test CSV processing optimization decision."""
        small_csv = "a,b,c\n1,2,3\n"
        # Create a larger CSV that exceeds the 1MB limit (0.5MB * 2 = 1MB threshold)
        large_csv = "a,b,c\n" + "1,2,3\n" * 100000  # About 600KB, should trigger streaming
        
        assert not self.optimizer.optimize_csv_processing(small_csv)
        assert self.optimizer.optimize_csv_processing(large_csv)
    
    def test_chunk_data(self):
        """Test data chunking."""
        data = "abcdefghijklmnop"
        chunks = list(self.optimizer.chunk_data(data, chunk_size=5))
        
        assert len(chunks) == 4
        assert chunks == ["abcde", "fghij", "klmno", "p"]
    
    def test_memory_limit_context(self):
        """Test memory limit context manager."""
        original_limit = self.optimizer.max_memory_bytes
        
        with self.optimizer.memory_limit_context(20):
            assert self.optimizer.max_memory_bytes == 20 * 1024 * 1024
        
        assert self.optimizer.max_memory_bytes == original_limit


class TestOptimizedInputData:
    """Test optimized input data creation."""
    
    def test_small_file_optimization(self):
        """Test optimization for small files."""
        # Create a small temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("small content")
            temp_path = f.name
        
        try:
            config = Config(max_file_size=1024*1024, streaming_threshold=1024)
            input_data = create_optimized_input_data(temp_path, config)
            
            assert input_data.source == InputSource.FILE
            assert not input_data.metadata.get("streaming", False)
            assert input_data.content == "small content"
        finally:
            os.unlink(temp_path)
    
    def test_large_file_optimization(self):
        """Test optimization for large files."""
        # Create a larger temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            # Write enough content to trigger streaming (more than 1KB threshold)
            for i in range(5000):  # Much more content
                f.write(f"This is line {i} with some content to make it larger and exceed the streaming threshold\n")
            temp_path = f.name
        
        try:
            config = Config(max_file_size=10*1024*1024, streaming_threshold=1024)
            input_data = create_optimized_input_data(temp_path, config)
            
            assert input_data.source == InputSource.FILE
            # The file should be large enough to trigger streaming
            file_size = input_data.metadata.get("file_size", 0)
            assert file_size > 1024  # Should be larger than threshold
            assert input_data.metadata.get("streaming", False)  # Should be True for large files
            assert input_data.content == str(Path(temp_path))  # Should store path
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        with pytest.raises(FileNotFoundError):
            create_optimized_input_data("nonexistent.txt")


if __name__ == "__main__":
    pytest.main([__file__])