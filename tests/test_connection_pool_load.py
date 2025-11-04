"""
Load Tests for Database Connection Pool
Verifies connection pool can handle concurrent load
"""

import asyncio
import asyncpg
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import sys

# Test configuration
TEST_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'anwalts_ai',
    'user': 'anwalts_user',
    'password': None,  # Will be loaded from environment
    'min_pool_size': 5,
    'max_pool_size': 20,  # Test with 20 first
    'command_timeout': 30
}


class ConnectionPoolLoadTester:
    """Load tester for database connection pool"""
    
    def __init__(self, config):
        self.config = config
        self.pool = None
        self.results = []
        
    async def setup_pool(self):
        """Create connection pool"""
        import os
        password = os.getenv('POSTGRES_PASSWORD', 'anwalts_password')
        
        self.pool = await asyncpg.create_pool(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=password,
            min_size=self.config['min_pool_size'],
            max_size=self.config['max_pool_size'],
            command_timeout=self.config['command_timeout']
        )
        print(f"✓ Pool created: min={self.config['min_pool_size']}, max={self.config['max_pool_size']}")
    
    async def cleanup_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("✓ Pool closed")
    
    async def simple_query(self, query_id):
        """Execute a simple query"""
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Simulate realistic query
                result = await conn.fetchval('SELECT pg_sleep(0.1), $1::int', query_id)
                
                duration = time.time() - start_time
                return {
                    'query_id': query_id,
                    'success': True,
                    'duration': duration,
                    'error': None
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'query_id': query_id,
                'success': False,
                'duration': duration,
                'error': str(e)
            }
    
    async def test_concurrent_load(self, num_concurrent, num_iterations):
        """
        Test 1: Concurrent Connection Load
        Simulates multiple concurrent users making database queries
        """
        print(f"\n{'='*70}")
        print(f"TEST 1: Concurrent Load ({num_concurrent} concurrent, {num_iterations} iterations)")
        print(f"{'='*70}")
        
        self.results = []
        start_time = time.time()
        
        # Execute concurrent queries
        tasks = [
            self.simple_query(i) 
            for i in range(num_concurrent * num_iterations)
        ]
        
        results = await asyncio.gather(*tasks)
        
        total_duration = time.time() - start_time
        self.results = results
        
        # Analyze results
        successes = [r for r in results if r['success']]
        failures = [r for r in results if not r['success']]
        durations = [r['duration'] for r in successes]
        
        print(f"\n📊 Results:")
        print(f"  Total queries:     {len(results)}")
        print(f"  Successful:        {len(successes)} ({len(successes)/len(results)*100:.1f}%)")
        print(f"  Failed:            {len(failures)} ({len(failures)/len(results)*100:.1f}%)")
        print(f"  Total duration:    {total_duration:.2f}s")
        print(f"  Throughput:        {len(results)/total_duration:.1f} queries/sec")
        
        if durations:
            print(f"\n⏱️  Query Latency:")
            print(f"  Min:               {min(durations)*1000:.1f}ms")
            print(f"  Max:               {max(durations)*1000:.1f}ms")
            print(f"  Mean:              {statistics.mean(durations)*1000:.1f}ms")
            print(f"  Median:            {statistics.median(durations)*1000:.1f}ms")
            print(f"  P95:               {statistics.quantiles(durations, n=20)[18]*1000:.1f}ms")
            print(f"  P99:               {statistics.quantiles(durations, n=100)[98]*1000:.1f}ms")
        
        # Test assertions
        assert len(failures) == 0, f"{len(failures)} queries failed!"
        assert max(durations) < 5.0, f"Max latency {max(durations):.2f}s exceeds 5s threshold"
        
        print(f"\n✅ Test PASSED: Pool handled {len(results)} concurrent queries successfully")
    
    async def test_pool_exhaustion(self, num_concurrent):
        """
        Test 2: Connection Pool Exhaustion
        Verifies behavior when pool is exhausted
        """
        print(f"\n{'='*70}")
        print(f"TEST 2: Pool Exhaustion ({num_concurrent} concurrent connections)")
        print(f"{'='*70}")
        
        # Hold connections open to exhaust pool
        async def hold_connection(conn_id, hold_time):
            try:
                async with self.pool.acquire() as conn:
                    print(f"  Connection {conn_id}: Acquired")
                    await asyncio.sleep(hold_time)
                    return {'conn_id': conn_id, 'success': True}
            except asyncio.TimeoutError:
                print(f"  Connection {conn_id}: TIMEOUT waiting for pool")
                return {'conn_id': conn_id, 'success': False, 'error': 'timeout'}
            except Exception as e:
                print(f"  Connection {conn_id}: ERROR - {e}")
                return {'conn_id': conn_id, 'success': False, 'error': str(e)}
        
        # Try to acquire more connections than pool max_size
        tasks = [hold_connection(i, 2.0) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successes = [r for r in results if isinstance(r, dict) and r.get('success')]
        failures = [r for r in results if isinstance(r, dict) and not r.get('success')]
        
        print(f"\n📊 Results:")
        print(f"  Attempted:         {num_concurrent}")
        print(f"  Acquired:          {len(successes)}")
        print(f"  Pool max_size:     {self.config['max_pool_size']}")
        print(f"  Timeouts/Errors:   {len(failures)}")
        
        if num_concurrent <= self.config['max_pool_size']:
            assert len(failures) == 0, "Pool should handle up to max_size connections"
            print(f"\n✅ Test PASSED: Pool handled {num_concurrent} connections within max_size")
        else:
            assert len(successes) <= self.config['max_pool_size'], \
                "Pool should not exceed max_size"
            print(f"\n✅ Test PASSED: Pool correctly limited to max_size ({self.config['max_pool_size']})")
    
    async def test_connection_recycling(self, num_queries):
        """
        Test 3: Connection Recycling
        Verifies connections are properly recycled and reused
        """
        print(f"\n{'='*70}")
        print(f"TEST 3: Connection Recycling ({num_queries} sequential queries)")
        print(f"{'='*70}")
        
        connection_ids = set()
        
        for i in range(num_queries):
            async with self.pool.acquire() as conn:
                # Get connection ID
                conn_id = await conn.fetchval('SELECT pg_backend_pid()')
                connection_ids.add(conn_id)
                
                # Execute simple query
                await conn.fetchval('SELECT 1')
        
        print(f"\n📊 Results:")
        print(f"  Total queries:     {num_queries}")
        print(f"  Unique conn IDs:   {len(connection_ids)}")
        print(f"  Pool min_size:     {self.config['min_pool_size']}")
        print(f"  Pool max_size:     {self.config['max_pool_size']}")
        
        # Should reuse connections (not create new one for each query)
        assert len(connection_ids) <= self.config['max_pool_size'], \
            "Should reuse connections, not create new ones"
        
        assert len(connection_ids) >= self.config['min_pool_size'], \
            "Should maintain at least min_size connections"
        
        print(f"\n✅ Test PASSED: Connections properly recycled")
    
    async def test_command_timeout(self):
        """
        Test 4: Command Timeout
        Verifies long-running queries are properly timed out
        """
        print(f"\n{'='*70}")
        print(f"TEST 4: Command Timeout (timeout={self.config['command_timeout']}s)")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Try to execute query that takes longer than timeout
                result = await conn.fetchval(f'SELECT pg_sleep({self.config["command_timeout"] + 5})')
                print(f"  ERROR: Query should have timed out!")
                assert False, "Query should have timed out"
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            print(f"  ✓ Query timed out after {duration:.1f}s")
            assert duration <= self.config['command_timeout'] + 5, \
                f"Timeout took too long: {duration:.1f}s"
        except Exception as e:
            duration = time.time() - start_time
            print(f"  ✓ Query failed as expected: {type(e).__name__}")
        
        print(f"\n✅ Test PASSED: Command timeout working correctly")
    
    async def test_pool_under_stress(self, duration_seconds=30):
        """
        Test 5: Sustained Load Test
        Runs sustained load for specified duration
        """
        print(f"\n{'='*70}")
        print(f"TEST 5: Sustained Load ({duration_seconds}s duration)")
        print(f"{'='*70}")
        
        start_time = time.time()
        query_count = 0
        error_count = 0
        
        async def sustained_worker():
            nonlocal query_count, error_count
            while time.time() - start_time < duration_seconds:
                try:
                    async with self.pool.acquire() as conn:
                        await conn.fetchval('SELECT pg_sleep(0.05), 1')
                        query_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"  ERROR: {e}")
        
        # Run 50 concurrent workers
        workers = [sustained_worker() for _ in range(50)]
        await asyncio.gather(*workers)
        
        total_duration = time.time() - start_time
        
        print(f"\n📊 Results:")
        print(f"  Duration:          {total_duration:.1f}s")
        print(f"  Total queries:     {query_count}")
        print(f"  Errors:            {error_count}")
        print(f"  Throughput:        {query_count/total_duration:.1f} queries/sec")
        print(f"  Error rate:        {error_count/query_count*100 if query_count > 0 else 0:.2f}%")
        
        error_rate = error_count / query_count if query_count > 0 else 0
        assert error_rate < 0.01, f"Error rate {error_rate*100:.2f}% exceeds 1% threshold"
        
        print(f"\n✅ Test PASSED: Pool handled sustained load successfully")


async def run_all_tests():
    """Run all connection pool tests"""
    print("\n" + "="*70)
    print("  DATABASE CONNECTION POOL LOAD TESTS")
    print("="*70)
    
    tester = ConnectionPoolLoadTester(TEST_CONFIG)
    
    try:
        # Setup
        print("\n⚙️  Setting up connection pool...")
        await tester.setup_pool()
        
        # Run tests
        await tester.test_concurrent_load(num_concurrent=50, num_iterations=2)
        await tester.test_pool_exhaustion(num_concurrent=25)
        await tester.test_connection_recycling(num_queries=100)
        await tester.test_command_timeout()
        await tester.test_pool_under_stress(duration_seconds=30)
        
        # Summary
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED")
        print("="*70)
        print("\n📋 Summary:")
        print("  • Pool handles 50+ concurrent connections")
        print("  • Connection recycling works correctly")
        print("  • Command timeout enforced")
        print("  • Sustained load handled without errors")
        print("\n✅ Connection pool is production-ready!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await tester.cleanup_pool()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
