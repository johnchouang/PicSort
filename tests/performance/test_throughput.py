"""Performance tests for file processing throughput."""
import pytest
import os
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import random
from typing import List, Dict

from src.lib.file_scanner import FileScanner
from src.lib.date_organizer import DateOrganizer
from src.lib.file_mover import FileMover
from src.models.configuration import Configuration


class TestThroughputPerformance:
    """Performance tests for file processing throughput."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)

        # Performance-optimized configuration
        self.config = Configuration()
        self.config.verify_checksum = False  # Disable for performance
        self.config.duplicate_handling = 'increment'
        self.config.process_all_files = False
        self.config.date_format = "YYYY-MM"

        # Initialize components
        self.scanner = FileScanner(self.config)
        self.organizer = DateOrganizer(self.config)
        self.mover = FileMover(self.config)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_files(self, count: int, file_size_kb: int = 1) -> List[str]:
        """Create test files for performance testing.

        Args:
            count: Number of files to create
            file_size_kb: Size of each file in KB

        Returns:
            List of created file paths
        """
        file_paths = []
        content = 'x' * (file_size_kb * 1024)  # File content

        # Create files with realistic naming patterns
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        all_extensions = image_extensions + video_extensions

        for i in range(count):
            # Generate realistic filename
            extension = random.choice(all_extensions)

            # Various naming patterns
            patterns = [
                f"IMG_{20230101 + i:08d}{extension}",
                f"DSC_{i:05d}{extension}",
                f"photo_{i:04d}{extension}",
                f"video_{datetime.now().strftime('%Y%m%d')}_{i:03d}{extension}",
                f"capture_{i:06d}{extension}",
            ]

            filename = random.choice(patterns)
            file_path = os.path.join(self.source_dir, filename)

            # Ensure unique filenames
            counter = 1
            while os.path.exists(file_path):
                base_name = Path(filename).stem
                ext = Path(filename).suffix
                filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(self.source_dir, filename)
                counter += 1

            # Create subdirectories occasionally for realistic folder structures
            if i % 20 == 0 and i > 0:
                subdir = os.path.join(self.source_dir, f"subfolder_{i // 20}")
                os.makedirs(subdir, exist_ok=True)
                file_path = os.path.join(subdir, filename)

            with open(file_path, 'w') as f:
                f.write(content)

            file_paths.append(file_path)

        return file_paths

    def _set_realistic_timestamps(self, file_paths: List[str]) -> None:
        """Set realistic creation and modification timestamps on test files.

        Args:
            file_paths: List of file paths to modify timestamps for
        """
        base_date = datetime(2023, 1, 1)

        for i, file_path in enumerate(file_paths):
            # Create realistic date spread over several months
            days_offset = i % 365  # Spread over a year
            file_date = base_date + timedelta(days=days_offset)

            # Convert to timestamp
            timestamp = file_date.timestamp()

            # Set both access and modification time
            os.utime(file_path, (timestamp, timestamp))

    @pytest.mark.performance
    def test_scan_throughput_1000_files(self):
        """Test scanning throughput with 1000 files."""
        # Create test files
        file_paths = self._create_test_files(1000, file_size_kb=5)  # 5KB files
        self._set_realistic_timestamps(file_paths)

        # Measure scanning performance
        start_time = time.perf_counter()

        media_files = self.scanner.scan_directory(self.source_dir)

        end_time = time.perf_counter()
        duration_seconds = end_time - start_time

        # Calculate throughput
        files_per_second = len(media_files) / duration_seconds
        files_per_minute = files_per_second * 60

        print(f"\nScan Performance:")
        print(f"Files scanned: {len(media_files)}")
        print(f"Duration: {duration_seconds:.2f} seconds")
        print(f"Throughput: {files_per_second:.1f} files/second")
        print(f"Throughput: {files_per_minute:.1f} files/minute")

        # Performance assertions
        assert len(media_files) == 1000
        assert files_per_minute >= 1000, f"Scan throughput {files_per_minute:.1f} files/minute is below target of 1000"

    @pytest.mark.performance
    def test_organize_throughput_1000_files(self):
        """Test organization throughput with 1000 files."""
        # Create and scan test files
        file_paths = self._create_test_files(1000, file_size_kb=5)
        self._set_realistic_timestamps(file_paths)
        media_files = self.scanner.scan_directory(self.source_dir)

        # Measure organization performance
        start_time = time.perf_counter()

        organization = self.organizer.organize_files(media_files, self.target_dir)

        end_time = time.perf_counter()
        duration_seconds = end_time - start_time

        # Calculate throughput
        total_files = sum(len(files) for files in organization.values())
        files_per_second = total_files / duration_seconds
        files_per_minute = files_per_second * 60

        print(f"\nOrganize Performance:")
        print(f"Files organized: {total_files}")
        print(f"Target folders: {len(organization)}")
        print(f"Duration: {duration_seconds:.2f} seconds")
        print(f"Throughput: {files_per_second:.1f} files/second")
        print(f"Throughput: {files_per_minute:.1f} files/minute")

        # Performance assertions
        assert total_files > 0
        assert files_per_minute >= 5000, f"Organize throughput {files_per_minute:.1f} files/minute is below target of 5000"

    @pytest.mark.performance
    def test_move_throughput_1000_files_dry_run(self):
        """Test move throughput with 1000 files in dry run mode."""
        # Create, scan, and organize test files
        file_paths = self._create_test_files(1000, file_size_kb=5)
        self._set_realistic_timestamps(file_paths)
        media_files = self.scanner.scan_directory(self.source_dir)
        organization = self.organizer.organize_files(media_files, self.target_dir)

        # Measure move performance in dry run
        start_time = time.perf_counter()

        operations = self.mover.move_files(organization, dry_run=True)

        end_time = time.perf_counter()
        duration_seconds = end_time - start_time

        # Calculate throughput
        files_per_second = len(operations) / duration_seconds
        files_per_minute = files_per_second * 60

        print(f"\nMove (Dry Run) Performance:")
        print(f"Operations planned: {len(operations)}")
        print(f"Duration: {duration_seconds:.2f} seconds")
        print(f"Throughput: {files_per_second:.1f} files/second")
        print(f"Throughput: {files_per_minute:.1f} files/minute")

        # Performance assertions
        assert len(operations) > 0
        assert all(op.status == 'skipped' for op in operations)  # Dry run
        assert files_per_minute >= 10000, f"Move dry run throughput {files_per_minute:.1f} files/minute is below target of 10000"

    @pytest.mark.performance
    @pytest.mark.slow
    def test_move_throughput_100_files_actual(self):
        """Test actual move throughput with 100 files (smaller for actual file operations)."""
        # Create, scan, and organize test files
        file_paths = self._create_test_files(100, file_size_kb=2)  # Smaller files for actual moves
        self._set_realistic_timestamps(file_paths)
        media_files = self.scanner.scan_directory(self.source_dir)
        organization = self.organizer.organize_files(media_files, self.target_dir)

        # Measure actual move performance
        start_time = time.perf_counter()

        operations = self.mover.move_files(organization, dry_run=False)

        end_time = time.perf_counter()
        duration_seconds = end_time - start_time

        # Calculate throughput
        successful_operations = [op for op in operations if op.status == 'completed']
        files_per_second = len(successful_operations) / duration_seconds
        files_per_minute = files_per_second * 60

        print(f"\nMove (Actual) Performance:")
        print(f"Files moved: {len(successful_operations)}")
        print(f"Failed operations: {len(operations) - len(successful_operations)}")
        print(f"Duration: {duration_seconds:.2f} seconds")
        print(f"Throughput: {files_per_second:.1f} files/second")
        print(f"Throughput: {files_per_minute:.1f} files/minute")

        # Performance assertions
        assert len(successful_operations) > 0
        assert files_per_minute >= 200, f"Actual move throughput {files_per_minute:.1f} files/minute is below target of 200"

        # Verify files were actually moved
        for op in successful_operations:
            assert os.path.exists(op.destination_path), f"Destination file missing: {op.destination_path}"
            assert not os.path.exists(op.source_file.path), f"Source file still exists: {op.source_file.path}"

    @pytest.mark.performance
    def test_end_to_end_throughput_1000_files(self):
        """Test complete end-to-end throughput with 1000 files."""
        # Create test files
        file_paths = self._create_test_files(1000, file_size_kb=3)
        self._set_realistic_timestamps(file_paths)

        # Measure complete pipeline performance
        start_time = time.perf_counter()

        # Step 1: Scan
        scan_start = time.perf_counter()
        media_files = self.scanner.scan_directory(self.source_dir)
        scan_duration = time.perf_counter() - scan_start

        # Step 2: Organize
        organize_start = time.perf_counter()
        organization = self.organizer.organize_files(media_files, self.target_dir)
        organize_duration = time.perf_counter() - organize_start

        # Step 3: Move (dry run for performance)
        move_start = time.perf_counter()
        operations = self.mover.move_files(organization, dry_run=True)
        move_duration = time.perf_counter() - move_start

        total_duration = time.perf_counter() - start_time

        # Calculate throughput
        files_per_second = len(media_files) / total_duration
        files_per_minute = files_per_second * 60

        print(f"\nEnd-to-End Performance (1000 files):")
        print(f"Scan: {scan_duration:.2f}s ({len(media_files)/scan_duration:.1f} files/sec)")
        print(f"Organize: {organize_duration:.2f}s ({len(media_files)/organize_duration:.1f} files/sec)")
        print(f"Move (dry): {move_duration:.2f}s ({len(operations)/move_duration:.1f} files/sec)")
        print(f"Total: {total_duration:.2f}s")
        print(f"Overall throughput: {files_per_minute:.1f} files/minute")

        # Performance assertions
        assert files_per_minute >= 1000, f"End-to-end throughput {files_per_minute:.1f} files/minute is below target of 1000"

    @pytest.mark.performance
    def test_memory_usage_large_dataset(self):
        """Test memory usage with large dataset."""
        import psutil
        import gc

        # Get initial memory usage
        process = psutil.Process()
        initial_memory_mb = process.memory_info().rss / 1024 / 1024

        # Create large dataset
        file_paths = self._create_test_files(2000, file_size_kb=1)
        self._set_realistic_timestamps(file_paths)

        # Process files and measure memory
        media_files = self.scanner.scan_directory(self.source_dir)
        after_scan_memory_mb = process.memory_info().rss / 1024 / 1024

        organization = self.organizer.organize_files(media_files, self.target_dir)
        after_organize_memory_mb = process.memory_info().rss / 1024 / 1024

        operations = self.mover.move_files(organization, dry_run=True)
        after_move_memory_mb = process.memory_info().rss / 1024 / 1024

        # Calculate memory usage
        peak_memory_mb = max(after_scan_memory_mb, after_organize_memory_mb, after_move_memory_mb)
        memory_per_file_kb = (peak_memory_mb - initial_memory_mb) * 1024 / len(media_files)

        print(f"\nMemory Usage (2000 files):")
        print(f"Initial: {initial_memory_mb:.1f} MB")
        print(f"After scan: {after_scan_memory_mb:.1f} MB")
        print(f"After organize: {after_organize_memory_mb:.1f} MB")
        print(f"After move planning: {after_move_memory_mb:.1f} MB")
        print(f"Peak usage: {peak_memory_mb:.1f} MB")
        print(f"Memory per file: {memory_per_file_kb:.2f} KB")

        # Memory assertions (should stay under 100MB for 2000 files)
        assert peak_memory_mb < 100, f"Peak memory usage {peak_memory_mb:.1f} MB exceeds 100MB limit"
        assert memory_per_file_kb < 25, f"Memory per file {memory_per_file_kb:.2f} KB is too high"

    @pytest.mark.performance
    def test_concurrent_scanning_performance(self):
        """Test concurrent scanning performance with multiple directories."""
        # Create multiple source directories
        num_dirs = 4
        files_per_dir = 250
        source_dirs = []

        for i in range(num_dirs):
            dir_path = os.path.join(self.temp_dir, f"source_{i}")
            os.makedirs(dir_path)
            source_dirs.append(dir_path)

            # Create files in each directory
            for j in range(files_per_dir):
                file_path = os.path.join(dir_path, f"file_{j:03d}.jpg")
                with open(file_path, 'w') as f:
                    f.write('x' * 1024)  # 1KB file

        # Test sequential scanning
        start_time = time.perf_counter()
        sequential_results = []
        for dir_path in source_dirs:
            media_files = self.scanner.scan_directory(dir_path)
            sequential_results.extend(media_files)
        sequential_duration = time.perf_counter() - start_time

        # Test concurrent scanning
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.scanner.scan_directory, dir_path) for dir_path in source_dirs]
            concurrent_results = []
            for future in futures:
                concurrent_results.extend(future.result())
        concurrent_duration = time.perf_counter() - start_time

        # Calculate performance metrics
        total_files = num_dirs * files_per_dir
        sequential_fps = total_files / sequential_duration
        concurrent_fps = total_files / concurrent_duration
        speedup_factor = sequential_duration / concurrent_duration

        print(f"\nConcurrent Scanning Performance ({total_files} files):")
        print(f"Sequential: {sequential_duration:.2f}s ({sequential_fps:.1f} files/sec)")
        print(f"Concurrent: {concurrent_duration:.2f}s ({concurrent_fps:.1f} files/sec)")
        print(f"Speedup factor: {speedup_factor:.2f}x")

        # Performance assertions
        assert len(sequential_results) == total_files
        assert len(concurrent_results) == total_files
        assert speedup_factor > 1.5, f"Concurrent scanning speedup {speedup_factor:.2f}x is below expected 1.5x"

    @pytest.mark.performance
    def test_large_file_handling_performance(self):
        """Test performance with larger files (simulating real photo sizes)."""
        # Create files with realistic photo sizes (1-5MB)
        large_file_sizes = [1024, 2048, 3072, 4096, 5120]  # KB sizes
        file_paths = []

        for i, size_kb in enumerate(large_file_sizes * 20):  # 100 files total
            filename = f"large_photo_{i:03d}.jpg"
            file_path = os.path.join(self.source_dir, filename)

            # Create file with specified size
            content = 'x' * (size_kb * 1024)
            with open(file_path, 'w') as f:
                f.write(content)

            file_paths.append(file_path)

        self._set_realistic_timestamps(file_paths)

        # Test scanning performance with large files
        start_time = time.perf_counter()
        media_files = self.scanner.scan_directory(self.source_dir)
        scan_duration = time.perf_counter() - start_time

        # Test organization
        organize_start = time.perf_counter()
        organization = self.organizer.organize_files(media_files, self.target_dir)
        organize_duration = time.perf_counter() - organize_start

        total_size_mb = sum(f.size for f in media_files) / (1024 * 1024)
        mb_per_second_scan = total_size_mb / scan_duration
        files_per_minute = len(media_files) / scan_duration * 60

        print(f"\nLarge File Performance ({len(media_files)} files, {total_size_mb:.1f} MB total):")
        print(f"Scan: {scan_duration:.2f}s ({mb_per_second_scan:.1f} MB/sec, {files_per_minute:.1f} files/min)")
        print(f"Organize: {organize_duration:.2f}s")
        print(f"Average file size: {total_size_mb / len(media_files):.1f} MB")

        # Performance assertions
        assert files_per_minute >= 300, f"Large file throughput {files_per_minute:.1f} files/minute is below target of 300"
        assert mb_per_second_scan >= 50, f"Data throughput {mb_per_second_scan:.1f} MB/sec is below target of 50"

    @pytest.mark.performance
    def test_deep_directory_structure_performance(self):
        """Test performance with deep directory structures."""
        # Create deep directory structure
        max_depth = 8
        files_per_level = 5
        total_files_created = 0

        def create_deep_structure(current_path: str, depth: int) -> int:
            files_created = 0
            if depth >= max_depth:
                return files_created

            # Create files at current level
            for i in range(files_per_level):
                filename = f"file_{depth}_{i}.jpg"
                file_path = os.path.join(current_path, filename)
                with open(file_path, 'w') as f:
                    f.write('x' * 1024)
                files_created += 1

            # Create subdirectories and recurse
            for i in range(2):  # 2 subdirs per level
                subdir = os.path.join(current_path, f"level_{depth}_sub_{i}")
                os.makedirs(subdir, exist_ok=True)
                files_created += create_deep_structure(subdir, depth + 1)

            return files_created

        total_files_created = create_deep_structure(self.source_dir, 0)

        # Test scanning performance with deep structure
        start_time = time.perf_counter()
        media_files = self.scanner.scan_directory(self.source_dir)
        scan_duration = time.perf_counter() - start_time

        files_per_second = len(media_files) / scan_duration

        print(f"\nDeep Directory Performance:")
        print(f"Directory depth: {max_depth} levels")
        print(f"Files created: {total_files_created}")
        print(f"Files found: {len(media_files)}")
        print(f"Scan duration: {scan_duration:.2f}s")
        print(f"Throughput: {files_per_second:.1f} files/sec")

        # Performance assertions
        assert len(media_files) == total_files_created
        assert files_per_second >= 100, f"Deep directory scan throughput {files_per_second:.1f} files/sec is below target of 100"


if __name__ == '__main__':
    # Run performance tests with verbose output
    pytest.main(['-v', '--tb=short', '-m', 'performance', __file__])